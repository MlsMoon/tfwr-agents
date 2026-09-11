# TFWR Agents

**The Farmer Was Replaced**용 Agent 작업 공간입니다.

skill은 정본 하나만 둡니다. 원샷 설치와 농장 스크립트 템플릿이 들어 있습니다. 세이브 데이터는 저장소에 넣지 않습니다.

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

## 포함되는 것

- `AGENTS.md` — 이 폴더를 작업 공간으로 열 때 Cursor / Claude / Grok 규칙
- `.agents/skills/` — **유일한 skill 정본**. 설치 스크립트가 만드는 심볼릭 링크로 발견됨
- `templates/Save0/` — 드론 스크립트 (`main`, 해바라기, 호박, 선인장, 공룡, 미로 등)
- `setup.bat` / `setup.ps1` — 먼저 언어, 그다음 세이브 경로. 복사 후 초기화까지 자동
- `i18n/` — 번역 README와 설치 문구. 저장소 루트는 영어만

## 포함되지 않는 것

- `Saves/` (`save.json` 포함)
- `Backup/`
- `Player.log`, `output.txt`, `options.txt`, Steam 클라우드 파일
- `.claude/skills`, `.grok/skills`, `.cursor/skills` (링크일 뿐, 두 번째 복사본 아님)

## 요구 사항

- 게임을 설치하고 한 번 이상 실행했을 것 (유저 데이터 폴더 필요)
- Windows (`mklink` 사용. 실패하면 **개발자 모드**를 켜세요)
- [Cursor](https://cursor.com) (또는 Claude Code / Grok)에서 **게임 유저 데이터 폴더**를 열 것
- `tfwr_control.py`용 Python 3
- 선택: .NET SDK (헬퍼를 다시 빌드할 때만)

기본 게임 폴더:

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## 초기화 (한 번)

어디든 클론하면 됩니다. 세이브 폴더에 넣을 필요는 없습니다.

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

`setup.bat`이 먼저 **언어**(`en`, `zh-CN`, `ko` 등)를 묻고, 그다음 세이브 경로를 물은 뒤, **이 저장소를 그곳으로 복사하고 초기화까지 자동으로 끝냅니다**. 두 번째 명령은 필요 없습니다.

기본 경로 (Enter):

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

힌트: Steam 설치 폴더가 아니라 세이브 폴더입니다. 없으면 게임을 한 번 실행하세요.

성공하면 그 세이브 폴더를 Cursor에서 여세요. 스크립트는:

1. `AGENTS.md`, `.agents\skills`, 템플릿, setup을 세이브 폴더로 복사
2. `templates\Save0\*.py`를 `Saves\Save0`에 복사 — **`save.json`은 쓰지 않음**
3. 다음 링크를 만듦:

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

skill만 설치하고 현재 드론 파일은 유지:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

`Saves\Save0`에 새 `.py`를 넣었다면 **게임 안** 에디터에서 **같은 이름 창**을 만드세요. 디스크 파일만으로는 `import`할 수 없습니다.

## 사용

1. Cursor에서 유저 데이터 폴더를 엽니다 (`AGENTS.md`와 `Saves\Save0`가 있는 곳).
2. 게임에서 `file watcher = enabled`, `tabs to spaces = disabled`. `options.example.txt` 참고.
3. 그 폴더 터미널에서 농장을 시작합니다:

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **F5를 누르지 마세요.** F5는 포커스된 창만 실행하며, 대개 `main`이 아닙니다.
5. 농장을 돌릴 때 **`main_maze`를 실행하지 마세요.** 미로는 금만 팜합니다.
6. file watcher가 켜져 있으면 기존 `Saves\Save0\*.py`는 핫 리로드됩니다. 전략을 바꾼 뒤에는 `/tfwr-sync-skills`로 `.agents\skills`에 사실을 반영하세요.

자주 쓰는 명령 (같은 폴더):

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| 명령 | 의미 |
| --- | --- |
| `run-main` / `restart` | 게임 API로 `main` 시작 (마우스 없음) |
| `parse` | `output.txt` 분류 (오류 vs `sun_wait` / `dino`) |
| `snapshot` | 인벤토리, 드론, 속도, 로그 |
| `stop` | `StopMainExecution` |

## Skills

| Skill | 언제 |
| --- | --- |
| `/tfwr-farm` | 드론 스크립트 (방언, Tab, 모듈) |
| `/tfwr-strategy` | VALUE, `pick_mode`, 해바라기 / 호박 / 선인장 / 공룡 |
| `/tfwr-save` | 세이브 해금 현황 |
| `/tfwr-control` | `main` 시작, output, 스냅샷 |
| `/tfwr-sync-skills` | 농장 변경 후 `.agents/skills`만 갱신 |

skill은 `.agents/skills/`만 수정하세요. `.claude` / `.grok` / `.cursor`에 두 번째 트리를 두지 마세요.

## 농장 스크립트

템플릿은 **당신의** `Saves\Save0`로 복사됩니다. 필요한 창 이름:

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py`는 에디터용 스텁입니다. 게임에서 `import`하지 마세요.

사용 중인 스크립트를 git 템플릿으로 되돌리기:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## 참고

- 라이선스 파일 없음. 자기 책임으로 사용하세요.
- 확장에 `set_world_size`를 쓰지 마세요 (필드가 비워집니다).
- 명시하지 않으면 `unlock()`하지 마세요.
- 들여쓰기는 **Tab**.
