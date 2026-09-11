using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;

public static class TfwrRunMain
{
	const string DefaultFile = "main";
	const BindingFlags Inst = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance;
	const BindingFlags Stat = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;

	public static void Load()
	{
		try
		{
			object context = FindUnitySyncContext();
			if (context != null)
			{
				MethodInfo post = context.GetType().GetMethod("Post", new[] { typeof(SendOrPostCallback), typeof(object) });
				if (post != null)
				{
					post.Invoke(context, new object[] { new SendOrPostCallback(RunOnMainThread), null });
					WriteLog("posted to UnitySynchronizationContext");
					return;
				}
			}
			WriteLog("no sync context, calling directly");
			RunOnMainThread(null);
		}
		catch (Exception ex)
		{
			WriteLog(ex.ToString());
		}
	}

	static void RunOnMainThread(object _)
	{
		try
		{
			string command = ReadTarget();
			if (command == "snapshot")
			{
				WriteSnapshot();
				return;
			}
			if (command == "stop")
			{
				StopExecution();
				return;
			}
			StartNamedFile(command);
		}
		catch (Exception ex)
		{
			WriteLog(ex.ToString());
		}
	}

	static void StopExecution()
	{
		Type mainSimType = FindType("MainSim");
		object inst = GetInst(mainSimType);
		if (inst == null)
		{
			WriteLog("stop: MainSim.Inst is null");
			return;
		}
		mainSimType.GetMethod("StopMainExecution", Type.EmptyTypes)?.Invoke(inst, null);
		WriteLog("StopMainExecution");
	}

	static void StartNamedFile(string fileName)
	{
		Type mainSimType = FindType("MainSim");
		object inst = GetInst(mainSimType);
		if (inst == null)
		{
			WriteLog("MainSim.Inst is null; are you in a save?");
			return;
		}
		object workspace = GetField(inst, "workspace");
		object windows = workspace == null ? null : GetField(workspace, "codeWindows");
		if (windows == null)
		{
			WriteLog("codeWindows is null");
			return;
		}
		object codeWindow = DictGet(windows, fileName);
		if (codeWindow == null)
		{
			WriteLog("code window not open: " + fileName);
			return;
		}
		MethodInfo isExecuting = mainSimType.GetMethod("IsExecuting", Type.EmptyTypes);
		if (isExecuting != null && (bool)isExecuting.Invoke(inst, null))
		{
			mainSimType.GetMethod("StopMainExecution", Type.EmptyTypes)?.Invoke(inst, null);
			WriteLog("stopped current execution");
		}
		object node = Call(codeWindow, "Parse");
		if (node == null)
		{
			WriteLog("Parse() returned null for " + fileName);
			return;
		}
		MethodInfo start = mainSimType.GetMethod("StartMainExecution");
		if (start == null)
		{
			WriteLog("StartMainExecution missing");
			return;
		}
		start.Invoke(inst, new[] { codeWindow, node });
		WriteLog("StartMainExecution(" + fileName + ")");
	}

	static void WriteSnapshot()
	{
		Type mainSimType = FindType("MainSim");
		object inst = GetInst(mainSimType);
		StringBuilder json = new StringBuilder();
		json.Append("{");
		Field("taken_at", DateTime.Now.ToString("o"), json, first: true);
		if (inst == null)
		{
			Field("ok", false, json);
			Field("error", "MainSim.Inst is null", json);
			json.Append("}");
			SaveSnapshot(json.ToString());
			WriteLog("snapshot failed: no MainSim");
			return;
		}
		Field("ok", true, json);
		bool executing = CallBool(inst, "IsExecuting");
		Field("executing", executing, json);
		Field("simulating", CallBool(inst, "IsSimulating"), json);
		Field("time_factor", GetPropDouble(inst, "TimeFactor"), json);
		object world = Call(inst, "GetWorldSize");
		if (world != null)
		{
			Field("world_x", VecInt(world, "x"), json);
			Field("world_y", VecInt(world, "y"), json);
		}
		object now = Call(inst, "GetCurrentTime");
		Field("sim_seconds", DurationSeconds(now), json);
		Field("output", CallStaticString("Logger", "GetOutputString"), json);
		AppendItems(inst, json);
		AppendSim(inst, json);
		AppendCallStack(inst, json);
		json.Append("}");
		SaveSnapshot(json.ToString());
		WriteLog("snapshot ok exec=" + executing + " t=" + DurationSeconds(now).ToString("0.###", CultureInfo.InvariantCulture));
	}

	static void AppendItems(object inst, StringBuilder json)
	{
		json.Append(",\"items\":{");
		object block = Call(inst, "GetInventory");
		if (block != null)
		{
			Call(block, "Serialize");
			object list = GetField(block, "serializeList");
			bool first = true;
			if (list is IEnumerable rows)
			{
				foreach (object row in rows)
				{
					if (row == null)
					{
						continue;
					}
					string name = Convert.ToString(GetField(row, "name") ?? GetProp(row, "name"));
					double nr = ToDouble(GetField(row, "nr") ?? GetProp(row, "nr"));
					if (string.IsNullOrEmpty(name))
					{
						continue;
					}
					if (!first)
					{
						json.Append(",");
					}
					first = false;
					json.Append(Quote(name)).Append(":").Append(Nr(nr));
				}
			}
		}
		json.Append("}");
	}

	static void AppendSim(object inst, StringBuilder json)
	{
		object sim = GetField(inst, "sim");
		if (sim == null)
		{
			return;
		}
		json.Append(",\"sim\":{");
		Field("speed_factor", GetPropDouble(sim, "SpeedFactor"), json, first: true);
		Field("paused", ToBool(GetProp(sim, "Paused")), json);
		Field("step_by_step", ToBool(GetField(sim, "stepByStepMode") ?? GetProp(sim, "stepByStepMode")), json);
		object farm = GetField(sim, "farm");
		if (farm != null)
		{
			Field("used_power", ToDouble(GetProp(farm, "UsedPower")), json);
			Field("speed_upgrades", GetPropInt(farm, "NumSpeedUpgrades"), json);
			object drones = GetField(farm, "drones");
			int alive = 0;
			StringBuilder droneJson = new StringBuilder();
			droneJson.Append("[");
			if (drones is IEnumerable list)
			{
				bool first = true;
				foreach (object drone in list)
				{
					if (drone == null)
					{
						continue;
					}
					alive++;
					if (!first)
					{
						droneJson.Append(",");
					}
					first = false;
					object pos = GetField(drone, "pos");
					object hat = GetField(drone, "hat");
					object hatSo = hat == null ? null : GetField(hat, "hatSO") ?? GetProp(hat, "hatSO");
					droneJson.Append("{\"id\":").Append(GetPropInt(drone, "DroneId"));
					if (pos != null)
					{
						droneJson.Append(",\"x\":").Append(GetFieldInt(pos, "x"));
						droneJson.Append(",\"y\":").Append(GetFieldInt(pos, "y"));
					}
					if (hatSo != null)
					{
						object hatName = GetField(hatSo, "hatName") ?? GetProp(hatSo, "hatName");
						if (hatName != null)
						{
							droneJson.Append(",\"hat\":").Append(Quote(Convert.ToString(hatName)));
						}
					}
					droneJson.Append("}");
				}
			}
			droneJson.Append("]");
			Field("drone_count", alive, json);
			json.Append(",\"drones\":").Append(droneJson);
		}
		object execution = GetProp(sim, "Execution") ?? GetField(sim, "execution");
		if (execution != null)
		{
			Field("execution_id", ToDouble(GetField(inst, "executionId")), json);
			object mainState = GetProp(execution, "MainState") ?? GetField(execution, "MainState");
			if (mainState != null)
			{
				object node = GetProp(mainState, "CurrentExecutingNode") ?? GetField(mainState, "CurrentExecutingNode");
				json.Append(",\"current_node\":").Append(Quote(NodeName(node)));
			}
		}
		json.Append("}");
	}

	static void AppendCallStack(object inst, StringBuilder json)
	{
		json.Append(",\"call_stack\":[");
		object stack = Call(inst, "GetCallStack");
		bool first = true;
		if (stack is IEnumerable rows)
		{
			foreach (object row in rows)
			{
				if (row == null)
				{
					continue;
				}
				string func = "";
				string call = "";
				object funcNode = GetField(row, "func") ?? GetProp(row, "Item1") ?? GetTupleItem(row, 0);
				object callNode = GetField(row, "callNode") ?? GetProp(row, "Item2") ?? GetTupleItem(row, 1);
				func = NodeName(funcNode);
				call = NodeName(callNode);
				if (!first)
				{
					json.Append(",");
				}
				first = false;
				json.Append("{\"func\":").Append(Quote(func)).Append(",\"call\":").Append(Quote(call)).Append("}");
			}
		}
		json.Append("]");
	}

	static string NodeName(object node)
	{
		if (node == null)
		{
			return "";
		}
		object boxed = GetField(node, "boxedParams") ?? GetProp(node, "boxedParams");
		object window = boxed == null ? null : GetField(boxed, "codeWindow") ?? GetProp(boxed, "codeWindow");
		string file = "";
		if (window != null)
		{
			file = Convert.ToString(GetField(window, "fileName") ?? GetProp(window, "fileName") ?? "");
		}
		string typeName = node.GetType().Name;
		object name = GetField(node, "name") ?? GetProp(node, "name") ?? GetField(node, "funcName") ?? GetProp(node, "funcName");
		string extra = name == null ? "" : Convert.ToString(name);
		if (file.Length > 0 && extra.Length > 0)
		{
			return file + "." + extra;
		}
		if (file.Length > 0)
		{
			return file + ":" + typeName;
		}
		if (extra.Length > 0)
		{
			return extra;
		}
		return typeName;
	}

	static object GetTupleItem(object row, int index)
	{
		PropertyInfo rest = row.GetType().GetProperty("Rest");
		PropertyInfo item = row.GetType().GetProperty("Item" + (index + 1));
		if (item != null)
		{
			return item.GetValue(row);
		}
		if (rest != null && index >= 7)
		{
			return GetTupleItem(rest.GetValue(row), index - 7);
		}
		return null;
	}

	static object GetInst(Type mainSimType)
	{
		return mainSimType?.GetProperty("Inst", Stat)?.GetValue(null);
	}

	static object DictGet(object dict, string key)
	{
		object[] tryArgs = { key, null };
		MethodInfo tryGet = dict.GetType().GetMethod("TryGetValue");
		if (tryGet != null && (bool)tryGet.Invoke(dict, tryArgs))
		{
			return tryArgs[1];
		}
		return null;
	}

	static object Call(object target, string name)
	{
		return target?.GetType().GetMethod(name, Type.EmptyTypes)?.Invoke(target, null);
	}

	static bool CallBool(object target, string name)
	{
		return ToBool(Call(target, name));
	}

	static string CallStaticString(string typeName, string method)
	{
		Type type = FindType(typeName);
		object value = type?.GetMethod(method, Type.EmptyTypes)?.Invoke(null, null);
		return value == null ? "" : Convert.ToString(value);
	}

	static object GetField(object target, string name)
	{
		return target?.GetType().GetField(name, Inst)?.GetValue(target);
	}

	static object GetProp(object target, string name)
	{
		return target?.GetType().GetProperty(name, Inst)?.GetValue(target);
	}

	static int GetFieldInt(object target, string name)
	{
		return Convert.ToInt32(GetField(target, name) ?? 0);
	}

	static int VecInt(object target, string name)
	{
		object value = GetProp(target, name) ?? GetField(target, name);
		return Convert.ToInt32(value ?? 0);
	}

	static int GetPropInt(object target, string name)
	{
		return Convert.ToInt32(GetProp(target, name) ?? 0);
	}

	static double GetPropDouble(object target, string name)
	{
		return ToDouble(GetProp(target, name));
	}

	static double DurationSeconds(object duration)
	{
		if (duration == null)
		{
			return 0;
		}
		object seconds = GetProp(duration, "Seconds") ?? GetField(duration, "Seconds");
		if (seconds != null)
		{
			return ToDouble(seconds);
		}
		object ns = GetField(duration, "nanoseconds") ?? GetProp(duration, "nanoseconds");
		if (ns != null)
		{
			return ToDouble(ns) / 1000000000.0;
		}
		return 0;
	}

	static bool ToBool(object value)
	{
		return value != null && Convert.ToBoolean(value);
	}

	static double ToDouble(object value)
	{
		if (value == null)
		{
			return 0;
		}
		try
		{
			return Convert.ToDouble(value, CultureInfo.InvariantCulture);
		}
		catch
		{
			return 0;
		}
	}

	static void Field(string key, object value, StringBuilder json, bool first = false)
	{
		if (!first)
		{
			json.Append(",");
		}
		json.Append(Quote(key)).Append(":");
		if (value is bool flag)
		{
			json.Append(flag ? "true" : "false");
		}
		else if (value is int || value is long || value is double || value is float)
		{
			json.Append(Nr(ToDouble(value)));
		}
		else
		{
			json.Append(Quote(Convert.ToString(value) ?? ""));
		}
	}

	static string Nr(double value)
	{
		if (double.IsNaN(value) || double.IsInfinity(value))
		{
			return "0";
		}
		return value.ToString("0.######", CultureInfo.InvariantCulture);
	}

	static string Quote(string text)
	{
		if (text == null)
		{
			text = "";
		}
		StringBuilder json = new StringBuilder();
		json.Append('"');
		foreach (char ch in text)
		{
			if (ch == '\\' || ch == '"')
			{
				json.Append('\\').Append(ch);
			}
			else if (ch == '\n')
			{
				json.Append("\\n");
			}
			else if (ch == '\r')
			{
				json.Append("\\r");
			}
			else if (ch == '\t')
			{
				json.Append("\\t");
			}
			else
			{
				json.Append(ch);
			}
		}
		json.Append('"');
		return json.ToString();
	}

	static void SaveSnapshot(string json)
	{
		string dir = ErrorIterDir();
		Directory.CreateDirectory(dir);
		string path = Path.Combine(dir, "snapshot.json");
		File.WriteAllText(path, json);
		File.AppendAllText(Path.Combine(dir, "snapshot-history.jsonl"), json + Environment.NewLine);
	}

	static string ReadTarget()
	{
		try
		{
			string path = Path.Combine(ErrorIterDir(), "run-target.txt");
			if (File.Exists(path))
			{
				string name = File.ReadAllText(path).Trim();
				if (name.Length > 0)
				{
					return name;
				}
			}
		}
		catch (Exception ex)
		{
			WriteLog(ex.ToString());
		}
		return DefaultFile;
	}

	static string PersistentDataPath()
	{
		Type app = FindType("UnityEngine.Application");
		object path = app?.GetProperty("persistentDataPath", Stat)?.GetValue(null);
		return path as string;
	}

	static string ErrorIterDir()
	{
		string root = PersistentDataPath();
		if (string.IsNullOrEmpty(root))
		{
			root = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + "Low\\TheFarmerWasReplaced\\TheFarmerWasReplaced";
		}
		return Path.Combine(root, ".agents", "error-iter");
	}

	static object FindUnitySyncContext()
	{
		Type awaitable = FindType("UnityEngine.Awaitable");
		return awaitable?.GetField("_synchronizationContext", Stat)?.GetValue(null);
	}

	static Type FindType(string fullName)
	{
		foreach (Assembly assembly in AppDomain.CurrentDomain.GetAssemblies())
		{
			Type type = assembly.GetType(fullName);
			if (type != null)
			{
				return type;
			}
		}
		return null;
	}

	static void WriteLog(string text)
	{
		try
		{
			Directory.CreateDirectory(ErrorIterDir());
			File.AppendAllText(Path.Combine(ErrorIterDir(), "run-main-invoke.log"), DateTime.Now.ToString("o") + " " + text + Environment.NewLine);
		}
		catch
		{
		}
	}
}
