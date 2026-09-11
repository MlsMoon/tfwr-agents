# TFWR Agents

Không gian làm việc Agent cho **The Farmer Was Replaced**.

Một cây skill chuẩn, cài một lệnh, và mẫu script nông trại. Save không đưa lên repo.

**[English](../README.md)** ·
**[简体中文](README.zh-CN.md)** ·
**[繁體中文](README.zh-TW.md)** ·
**[日本語](README.ja.md)** ·
**[한국어](README.ko.md)** ·
**[Deutsch](README.de.md)** ·
**[Français](README.fr.md)** ·
**[Español](README.es.md)** ·
**[Português](README.pt-BR.md)** ·
**[Русский](README.ru.md)** ·
**[Tiếng Việt](README.vi.md)** ·
**[Bahasa Indonesia](README.id.md)**

## Có gì

- `AGENTS.md` — quy tắc Cursor / Claude / Grok khi thư mục này là workspace
- `.agents/skills/` — **bản skill duy nhất**. Các công cụ thấy qua symlink do setup tạo
- `templates/Save0/` — script drone (`main`, hướng dương, bí ngô, xương rồng, khủng long, mê cung, …)
- `setup.bat` / `setup.ps1` — trước hết ngôn ngữ, rồi đường dẫn save; chép repo và tự xong init
- `i18n/` — README dịch và câu setup. Thư mục gốc repo vẫn là tiếng Anh

## Không có gì

- `Saves/` (kể cả `save.json`)
- `Backup/`
- `Player.log`, `output.txt`, `options.txt`, file Steam Cloud
- `.claude/skills`, `.grok/skills`, `.cursor/skills` (chỉ là link, không phải bản sao thứ hai)

## Yêu cầu

- Game đã cài và chạy ít nhất một lần (có thư mục userdata)
- Windows (`mklink`; bật **Chế độ nhà phát triển** nếu lỗi)
- Mở [Cursor](https://cursor.com) (hoặc Claude Code / Grok) đúng **thư mục userdata**
- Python 3 cho `tfwr_control.py`
- Tuỳ chọn: .NET SDK, chỉ khi rebuild helper

Thư mục mặc định:

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## Khởi tạo (một lần)

Clone ở đâu cũng được. Không cần sẵn trong thư mục save.

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

`setup.bat` hỏi **ngôn ngữ** trước (`en`, `zh-CN`, `vi`, …), rồi đường dẫn save, **tự chép repo vào đó và làm xong init**. Không cần lệnh thứ hai.

Đường dẫn mặc định (Enter):

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

Gợi ý: thư mục **save**, không phải cài Steam. Nếu chưa có, mở game một lần.

Xong thì mở **thư mục save đó** trong Cursor. Script sẽ:

1. chép `AGENTS.md`, `.agents\skills`, mẫu và setup vào thư mục save
2. chép `templates\Save0\*.py` vào `Saves\Save0` — **không ghi `save.json`**
3. tạo:

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

Chỉ cài skill, giữ script drone hiện tại:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

File `.py` mới trong `Saves\Save0` cần **cửa sổ cùng tên** trong editor **trong game**. Chỉ có file trên đĩa thì không `import` được.

## Cách dùng

1. Mở thư mục userdata trong Cursor (`AGENTS.md` và `Saves\Save0`).
2. Trong game: `file watcher = enabled`, `tabs to spaces = disabled`. Xem `options.example.txt`.
3. Chạy nông trại từ terminal thư mục đó:

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **Đừng bấm F5.** F5 chỉ chạy cửa sổ đang focus, thường không phải `main`.
5. Khi chạy nông trại **đừng chạy `main_maze`**. Mê cung chỉ farm vàng.
6. Bật file watcher thì `Saves\Save0\*.py` sẵn có sẽ hot-reload. Đổi chiến lược xong dùng `/tfwr-sync-skills` ghi lại `.agents\skills`.

Lệnh hay dùng (cùng thư mục):

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| Lệnh | Ý nghĩa |
| --- | --- |
| `run-main` / `restart` | Chạy `main` bằng API game (không chuột) |
| `parse` | Phân loại `output.txt` |
| `snapshot` | Kho, drone, tốc độ, log |
| `stop` | `StopMainExecution` |

## Skills

| Skill | Khi nào |
| --- | --- |
| `/tfwr-farm` | Sửa script drone (phương ngữ, Tab, module) |
| `/tfwr-strategy` | VALUE, `pick_mode`, hướng dương / bí / xương rồng / khủng long |
| `/tfwr-save` | Save đã mở khoá gì |
| `/tfwr-control` | Chạy `main`, output, snapshot |
| `/tfwr-sync-skills` | Sau khi sửa nông trại, chỉ cập nhật `.agents/skills` |

Chỉ sửa skill trong `.agents/skills/`. Đừng giữ cây thứ hai ở `.claude` / `.grok` / `.cursor`.

## Script nông trại

Mẫu được chép vào **`Saves\Save0` của bạn**. Tên cửa sổ:

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py` là stub cho editor. Đừng `import` trong game.

Đưa script đang chạy ngược lại template git:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## Ghi chú

- Không có file giấy phép. Tự chịu rủi ro.
- Đừng dùng `set_world_size` để mở rộng (sẽ xoá ruộng).
- Đừng gọi `unlock()` trừ khi bạn yêu cầu rõ.
- Thụt dòng bằng **Tab**.
