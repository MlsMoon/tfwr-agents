# TFWR Agents

Ruang kerja Agent untuk **The Farmer Was Replaced**.

Satu pohon skill kanonik, pemasang sekali jalan, dan templat skrip. Data save tidak masuk repositori.

**[English](README.md)** ·
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

## Isi

- `AGENTS.md` — aturan Cursor / Claude / Grok saat folder ini jadi workspace
- `.agents/skills/` — **satu-satunya salinan skill**. Editor melihatnya lewat symlink dari setup
- `templates/Save0/` — skrip drone (`main`, matahari, labu, kaktus, dinosaurus, labirin, …)
- `setup.bat` / `setup.ps1` — menyalin skill + skrip ke folder game dan membuat tautan

## Tidak termasuk

- `Saves/` (termasuk `save.json`)
- `Backup/`
- `Player.log`, `output.txt`, `options.txt`, berkas Steam Cloud
- `.claude/skills`, `.grok/skills`, `.cursor/skills` (hanya tautan, bukan salinan kedua)

## Syarat

- Game terpasang dan pernah dijalankan (folder userdata ada)
- Windows (`mklink`; nyalakan **Mode pengembang** jika gagal)
- Buka [Cursor](https://cursor.com) (atau Claude Code / Grok) pada **folder userdata**
- Python 3 untuk `tfwr_control.py`
- Opsional: .NET SDK, hanya untuk membangun ulang helper

Folder bawaan:

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## Inisialisasi (sekali)

Clone di mana saja. Tidak perlu sudah di folder save.

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

`setup.bat` **akan minta jalur save**, **menyalin repo ke sana, lalu menyelesaikan init sendiri**. Tidak perlu perintah kedua.

Jalur bawaan (Enter):

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

Petunjuk: folder **save**, bukan instal Steam. Jika belum ada, jalankan game sekali.

Lalu buka **folder save itu** di Cursor. Skrip akan:

1. menyalin `AGENTS.md`, `.agents\skills`, templat, dan setup ke folder save
2. menyalin `templates\Save0\*.py` ke `Saves\Save0` — **tidak menulis `save.json`**
3. membuat:

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

Hanya skill, pertahankan skrip drone Anda:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

`.py` baru di `Saves\Save0` butuh **jendela bernama sama** di editor **dalam game**. Berkas di disk saja tidak bisa di-`import`.

## Pemakaian

1. Buka folder userdata di Cursor (`AGENTS.md` dan `Saves\Save0`).
2. Di game: `file watcher = enabled`, `tabs to spaces = disabled`. Lihat `options.example.txt`.
3. Jalankan kebun dari terminal folder itu:

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **Jangan tekan F5.** F5 menjalankan jendela yang fokus, sering bukan `main`.
5. Untuk kebun **jangan jalankan `main_maze`**. Labirin hanya farm emas.
6. Dengan file watcher, `Saves\Save0\*.py` yang sudah ada di-hot-reload. Setelah ubah strategi, `/tfwr-sync-skills` ke `.agents\skills`.

Perintah berguna (folder yang sama):

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| Perintah | Arti |
| --- | --- |
| `run-main` / `restart` | Mulai `main` lewat API game (tanpa mouse) |
| `parse` | Klasifikasi `output.txt` |
| `snapshot` | Inventori, drone, kecepatan, log |
| `stop` | `StopMainExecution` |

## Skills

| Skill | Kapan |
| --- | --- |
| `/tfwr-farm` | Skrip drone (dialek, Tab, modul) |
| `/tfwr-strategy` | VALUE, `pick_mode`, matahari / labu / kaktus / dino |
| `/tfwr-save` | Apa yang terbuka di save |
| `/tfwr-control` | Jalankan `main`, output, snapshot |
| `/tfwr-sync-skills` | Setelah ubah kebun, perbarui hanya `.agents/skills` |

Sunting skill hanya di `.agents/skills/`. Jangan pelihara pohon kedua di `.claude` / `.grok` / `.cursor`.

## Skrip kebun

Templat disalin ke **`Saves\Save0` Anda**. Nama jendela:

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py` adalah stub editor. Jangan di-`import` di game.

Ekspor skrip hidup kembali ke templat git:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## Catatan

- Tidak ada berkas lisensi. Pakai dengan risiko sendiri.
- Jangan `set_world_size` untuk memperluas (lapangan dikosongkan).
- Jangan `unlock()` kecuali Anda memintanya.
- Indentasi pakai **Tab**.
