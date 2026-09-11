using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

internal static class TfwrInjector
{
	const int ProcessCreateThread = 0x0002;
	const int ProcessVmOperation = 0x0008;
	const int ProcessVmRead = 0x0010;
	const int ProcessVmWrite = 0x0020;
	const int ProcessQueryInformation = 0x0400;
	const int ProcessRights = ProcessCreateThread | ProcessVmOperation | ProcessVmRead | ProcessVmWrite | ProcessQueryInformation;
	const uint MemCommit = 0x1000;
	const uint MemReserve = 0x2000;
	const uint PageExecuteReadWrite = 0x40;
	const uint ListModulesAll = 0x03;

	static readonly string[] ExportNames =
	{
		"mono_get_root_domain",
		"mono_thread_attach",
		"mono_image_open_from_data",
		"mono_assembly_load_from_full",
		"mono_assembly_get_image",
		"mono_class_from_name",
		"mono_class_get_method_from_name",
		"mono_runtime_invoke",
		"mono_image_strerror",
		"mono_object_get_class",
		"mono_class_get_name",
	};

	static IntPtr handle;
	static IntPtr mono;
	static Dictionary<string, IntPtr> exports = new();
	static IntPtr rootDomain;
	static bool attach;

	static int Main(string[] args)
	{
		string processName = "TheFarmerWasReplaced";
		string dllPath = Path.Combine(AppContext.BaseDirectory, "TfwrRunMain.dll");
		string className = "TfwrRunMain";
		string methodName = "Load";
		int pid = 0;
		for (int i = 0; i < args.Length; i++)
		{
			if (args[i] == "--process" && i + 1 < args.Length) processName = args[++i];
			else if (args[i] == "--pid" && i + 1 < args.Length) pid = int.Parse(args[++i]);
			else if (args[i] == "--dll" && i + 1 < args.Length) dllPath = args[++i];
			else if (args[i] == "--class" && i + 1 < args.Length) className = args[++i];
			else if (args[i] == "--method" && i + 1 < args.Length) methodName = args[++i];
		}
		if (!File.Exists(dllPath))
		{
			Console.Error.WriteLine("payload missing: " + dllPath);
			return 2;
		}
		Process process = null;
		if (pid != 0)
		{
			try { process = Process.GetProcessById(pid); }
			catch (ArgumentException) { process = null; }
		}
		if (process == null)
		{
			process = Process.GetProcessesByName(processName).FirstOrDefault();
		}
		if (process == null)
		{
			foreach (Process candidate in Process.GetProcesses())
			{
				try
				{
					string path = candidate.MainModule?.FileName ?? "";
					if (path.EndsWith("TheFarmerWasReplaced.exe", StringComparison.OrdinalIgnoreCase))
					{
						process = candidate;
						break;
					}
				}
				catch
				{
				}
			}
		}
		if (process == null)
		{
			Console.Error.WriteLine("game process not found: " + processName);
			return 3;
		}
		Console.WriteLine("pid " + process.Id + " " + process.ProcessName);
		handle = OpenProcess(ProcessRights, false, process.Id);
		if (handle == IntPtr.Zero)
		{
			throw new Win32Exception(Marshal.GetLastWin32Error(), "OpenProcess");
		}
		try
		{
			if (!FindMono(out mono, out string monoPath))
			{
				Console.Error.WriteLine("mono-2.0-bdwgc.dll not loaded");
				return 4;
			}
			LoadExports(mono, monoPath);
			rootDomain = Call("mono_get_root_domain");
			if (rootDomain == IntPtr.Zero)
			{
				Console.Error.WriteLine("mono_get_root_domain failed");
				return 5;
			}
			attach = true;
			byte[] assembly = File.ReadAllBytes(dllPath);
			IntPtr status = AllocWrite(BitConverter.GetBytes(0));
			IntPtr image = Call("mono_image_open_from_data", AllocWrite(assembly), (IntPtr)assembly.Length, (IntPtr)1, status);
			int openStatus = ReadInt32(status);
			if (image == IntPtr.Zero || openStatus != 0)
			{
				Console.Error.WriteLine("mono_image_open_from_data status=" + openStatus);
				return 6;
			}
			string fakeName = "TfwrRunMain-" + DateTime.UtcNow.Ticks + ".dll";
			IntPtr loaded = Call("mono_assembly_load_from_full", image, AllocWrite(fakeName), status, IntPtr.Zero);
			if (loaded == IntPtr.Zero || ReadInt32(status) != 0)
			{
				Console.Error.WriteLine("mono_assembly_load_from_full status=" + ReadInt32(status));
				return 7;
			}
			IntPtr image2 = Call("mono_assembly_get_image", loaded);
			IntPtr klass = Call("mono_class_from_name", image2, AllocWrite(""), AllocWrite(className));
			if (klass == IntPtr.Zero)
			{
				Console.Error.WriteLine("class not found: " + className);
				return 8;
			}
			IntPtr method = Call("mono_class_get_method_from_name", klass, AllocWrite(methodName), IntPtr.Zero);
			if (method == IntPtr.Zero)
			{
				Console.Error.WriteLine("method not found: " + methodName);
				return 9;
			}
			IntPtr exc = AllocWrite(BitConverter.GetBytes(0L));
			Call("mono_runtime_invoke", method, IntPtr.Zero, IntPtr.Zero, exc);
			IntPtr exception = (IntPtr)ReadInt64(exc);
			if (exception != IntPtr.Zero)
			{
				Console.Error.WriteLine("runtime invoke threw");
				return 10;
			}
			Console.WriteLine("invoked " + className + "." + methodName);
			return 0;
		}
		finally
		{
			CloseHandle(handle);
		}
	}

	static bool FindMono(out IntPtr module, out string path)
	{
		module = IntPtr.Zero;
		path = "";
		IntPtr[] mods = new IntPtr[1024];
		if (!EnumProcessModulesEx(handle, mods, mods.Length * IntPtr.Size, out int needed, ListModulesAll))
		{
			return false;
		}
		int count = needed / IntPtr.Size;
		StringBuilder name = new StringBuilder(1024);
		StringBuilder full = new StringBuilder(1024);
		for (int i = 0; i < count; i++)
		{
			name.Length = 0;
			if (GetModuleBaseName(handle, mods[i], name, name.Capacity) == 0)
			{
				continue;
			}
			if (!name.ToString().Equals("mono-2.0-bdwgc.dll", StringComparison.OrdinalIgnoreCase))
			{
				continue;
			}
			full.Length = 0;
			GetModuleFileNameEx(handle, mods[i], full, full.Capacity);
			module = mods[i];
			path = full.ToString();
			return true;
		}
		return false;
	}

	static void LoadExports(IntPtr remoteBase, string diskPath)
	{
		exports.Clear();
		foreach (string name in ExportNames)
		{
			exports[name] = IntPtr.Zero;
		}
		using FileStream stream = File.OpenRead(diskPath);
		using BinaryReader reader = new BinaryReader(stream);
		stream.Position = 0x3C;
		int nt = reader.ReadInt32();
		stream.Position = nt + 6;
		int numSections = reader.ReadUInt16();
		stream.Position = nt + 20;
		int optSize = reader.ReadUInt16();
		stream.Position = nt + 24;
		ushort magic = reader.ReadUInt16();
		int exportDirOff = magic == 0x20B ? 112 : 96;
		stream.Position = nt + 24 + exportDirOff;
		int exportRva = reader.ReadInt32();
		int sectionStart = nt + 24 + optSize;
		List<(int va, int raw, int size)> sections = new();
		for (int i = 0; i < numSections; i++)
		{
			stream.Position = sectionStart + i * 40 + 8;
			int vsize = reader.ReadInt32();
			int va = reader.ReadInt32();
			int rawSize = reader.ReadInt32();
			int raw = reader.ReadInt32();
			sections.Add((va, raw, Math.Max(vsize, rawSize)));
		}
		long FileOff(int rva)
		{
			foreach (var s in sections)
			{
				if (rva >= s.va && rva < s.va + s.size)
				{
					return s.raw + (rva - s.va);
				}
			}
			return rva;
		}
		stream.Position = FileOff(exportRva + 24);
		int nNames = reader.ReadInt32();
		int funcsRva = reader.ReadInt32();
		int namesRva = reader.ReadInt32();
		int ordsRva = reader.ReadInt32();
		for (int i = 0; i < nNames; i++)
		{
			stream.Position = FileOff(namesRva) + i * 4;
			int nameRva = reader.ReadInt32();
			stream.Position = FileOff(nameRva);
			string name = ReadAscii(reader);
			if (!exports.ContainsKey(name))
			{
				continue;
			}
			stream.Position = FileOff(ordsRva) + i * 2;
			ushort ord = reader.ReadUInt16();
			stream.Position = FileOff(funcsRva) + ord * 4;
			int funcRva = reader.ReadInt32();
			exports[name] = remoteBase + funcRva;
		}
		foreach (var kv in exports)
		{
			if (kv.Value == IntPtr.Zero)
			{
				throw new Exception("missing export " + kv.Key);
			}
		}
	}

	static string ReadAscii(BinaryReader reader)
	{
		List<byte> bytes = new();
		byte b;
		while ((b = reader.ReadByte()) != 0)
		{
			bytes.Add(b);
		}
		return Encoding.ASCII.GetString(bytes.ToArray());
	}

	static IntPtr Call(string export, params IntPtr[] args)
	{
		IntPtr retPtr = AllocWrite(BitConverter.GetBytes(0L));
		byte[] code = Assemble64(exports[export], retPtr, args);
		IntPtr codePtr = AllocWrite(code);
		IntPtr thread = CreateRemoteThread(handle, IntPtr.Zero, UIntPtr.Zero, codePtr, IntPtr.Zero, 0, out _);
		if (thread == IntPtr.Zero)
		{
			throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateRemoteThread " + export);
		}
		if (WaitForSingleObject(thread, 15000) != 0)
		{
			throw new Exception("timeout calling " + export);
		}
		CloseHandle(thread);
		return (IntPtr)ReadInt64(retPtr);
	}

	static byte[] Assemble64(IntPtr function, IntPtr retPtr, IntPtr[] args)
	{
		List<byte> code = new();
		void Emit(params byte[] bytes) => code.AddRange(bytes);
		void MovRegImm(byte rex, byte reg, IntPtr value)
		{
			Emit(rex, reg);
			code.AddRange(BitConverter.GetBytes(value.ToInt64()));
		}
		Emit(0x48, 0x83, 0xEC, 0x28);
		if (attach)
		{
			MovRegImm(0x48, 0xB8, exports["mono_thread_attach"]);
			MovRegImm(0x48, 0xB9, rootDomain);
			Emit(0xFF, 0xD0);
		}
		MovRegImm(0x48, 0xB8, function);
		if (args.Length > 0) MovRegImm(0x48, 0xB9, args[0]);
		if (args.Length > 1) MovRegImm(0x48, 0xBA, args[1]);
		if (args.Length > 2) MovRegImm(0x49, 0xB8, args[2]);
		if (args.Length > 3) MovRegImm(0x49, 0xB9, args[3]);
		Emit(0xFF, 0xD0);
		Emit(0x48, 0x83, 0xC4, 0x28);
		MovRegImm(0x49, 0xBB, retPtr);
		Emit(0x49, 0x89, 0x03);
		Emit(0xC3);
		return code.ToArray();
	}

	static IntPtr AllocWrite(byte[] data)
	{
		IntPtr ptr = VirtualAllocEx(handle, IntPtr.Zero, (UIntPtr)Math.Max(data.Length, 8), MemCommit | MemReserve, PageExecuteReadWrite);
		if (ptr == IntPtr.Zero)
		{
			throw new Win32Exception(Marshal.GetLastWin32Error(), "VirtualAllocEx");
		}
		if (!WriteProcessMemory(handle, ptr, data, (UIntPtr)data.Length, out _))
		{
			throw new Win32Exception(Marshal.GetLastWin32Error(), "WriteProcessMemory");
		}
		return ptr;
	}

	static IntPtr AllocWrite(string text)
	{
		return AllocWrite(Encoding.UTF8.GetBytes(text + "\0"));
	}

	static int ReadInt32(IntPtr address)
	{
		byte[] buf = new byte[4];
		ReadProcessMemory(handle, address, buf, (UIntPtr)4, out _);
		return BitConverter.ToInt32(buf, 0);
	}

	static long ReadInt64(IntPtr address)
	{
		byte[] buf = new byte[8];
		ReadProcessMemory(handle, address, buf, (UIntPtr)8, out _);
		return BitConverter.ToInt64(buf, 0);
	}

	[DllImport("kernel32.dll", SetLastError = true)]
	static extern IntPtr OpenProcess(int access, bool inherit, int pid);

	[DllImport("kernel32.dll", SetLastError = true)]
	static extern bool CloseHandle(IntPtr handle);

	[DllImport("kernel32.dll", SetLastError = true)]
	static extern IntPtr VirtualAllocEx(IntPtr process, IntPtr addr, UIntPtr size, uint type, uint protect);

	[DllImport("kernel32.dll", SetLastError = true)]
	static extern bool WriteProcessMemory(IntPtr process, IntPtr addr, byte[] data, UIntPtr size, out UIntPtr written);

	[DllImport("kernel32.dll", SetLastError = true)]
	static extern bool ReadProcessMemory(IntPtr process, IntPtr addr, byte[] data, UIntPtr size, out UIntPtr read);

	[DllImport("kernel32.dll", SetLastError = true)]
	static extern IntPtr CreateRemoteThread(IntPtr process, IntPtr attr, UIntPtr stack, IntPtr start, IntPtr param, uint flags, out uint id);

	[DllImport("kernel32.dll", SetLastError = true)]
	static extern uint WaitForSingleObject(IntPtr handle, uint ms);

	[DllImport("psapi.dll", SetLastError = true)]
	static extern bool EnumProcessModulesEx(IntPtr process, IntPtr[] modules, int size, out int needed, uint filter);

	[DllImport("psapi.dll", CharSet = CharSet.Unicode)]
	static extern uint GetModuleBaseName(IntPtr process, IntPtr module, StringBuilder name, int size);

	[DllImport("psapi.dll", CharSet = CharSet.Unicode)]
	static extern uint GetModuleFileNameEx(IntPtr process, IntPtr module, StringBuilder name, int size);
}
