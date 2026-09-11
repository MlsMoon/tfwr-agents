# TFWR Agents

**The Farmer Was Replaced** 用の Agent ワークスペースです。

skill は正本を 1 つだけ持ちます。ワンショット導入と農場スクリプトのテンプレート付き。セーブデータはリポジトリに入りません。

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

## 含まれるもの

- `AGENTS.md` — このフォルダをワークスペースにしたときの Cursor / Claude / Grok 向けルール
- `.agents/skills/` — **唯一の skill 正本**。セットアップが作るシンボリックリンク経由で各ツールが読む
- `templates/Save0/` — ドローンスクリプト（`main`、ひまわり、カボチャ、サボテン、恐竜、迷路など）
- `setup.bat` / `setup.ps1` — skill とスクリプトをゲームフォルダへコピーし、リンクを作成

## 含まれないもの

- `Saves/`（`save.json` を含む）
- `Backup/`
- `Player.log`、`output.txt`、`options.txt`、Steam クラウドファイル
- `.claude/skills`、`.grok/skills`、`.cursor/skills`（リンクのみ。コピーではない）

## 必要条件

- ゲームをインストールし、一度は起動していること（ユーザーデータフォルダが必要）
- Windows（`mklink` を使用。失敗したら**開発者モード**を有効化）
- [Cursor](https://cursor.com)（または Claude Code / Grok）で**ゲームのユーザーデータフォルダ**を開く
- `tfwr_control.py` 用の Python 3
- 任意：.NET SDK（ヘルパーを再ビルドするときだけ）

既定のゲームフォルダ：

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## 初期化（ワンショット）

どこにクローンしても構いません。セーブフォルダに置く必要はありません。

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

`setup.bat` が**セーブパスの入力を求め**、**このリポジトリをそこにコピーして初期化まで自動で終わらせます**。二回目のコマンドは不要です。

既定パス（Enter だけ）：

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

ヒント：Steam のインストールフォルダではなくセーブフォルダです。無いときは先にゲームを一度起動。

成功したら、そのセーブフォルダを Cursor で開きます。スクリプトは：

1. `AGENTS.md`、`.agents\skills`、テンプレート、setup をセーブフォルダへコピー
2. `templates\Save0\*.py` を `Saves\Save0` へコピー — **`save.json` は書き込まない**
3. 次のリンクを作成：

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

skill だけ入れて、今のドローンファイルは残す：

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

`Saves\Save0` に新しい `.py` を足したら、**ゲーム内**エディタで**同名ウィンドウ**を作ってください。ディスク上のファイルだけでは `import` できません。

## 使い方

1. Cursor でユーザーデータフォルダを開く（`AGENTS.md` と `Saves\Save0` がある場所）。
2. ゲーム側：`file watcher = enabled`、`tabs to spaces = disabled`。`options.example.txt` を参照。
3. そのフォルダのターミナルで農場を起動：

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **F5 を押さない**。F5 はフォーカス中のウィンドウだけを実行し、多くの場合 `main` ではない。
5. 農場を回すときは **`main_maze` を実行しない**。迷路は金専用。
6. file watcher がオンなら既存の `Saves\Save0\*.py` はホットリロードされる。戦略を変えたら `/tfwr-sync-skills` で `.agents\skills` に事実を戻す。

よく使うコマンド（同じフォルダ）：

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| コマンド | 意味 |
| --- | --- |
| `run-main` / `restart` | ゲーム API で `main` を開始（マウス不要） |
| `parse` | `output.txt` を分類（エラー vs `sun_wait` / `dino`） |
| `snapshot` | 所持品、ドローン、速度、ログ |
| `stop` | `StopMainExecution` |

## Skills

| Skill | 用途 |
| --- | --- |
| `/tfwr-farm` | ドローンスクリプト（方言、Tab、モジュール） |
| `/tfwr-strategy` | VALUE、`pick_mode`、ひまわり / カボチャ / サボテン / 恐竜 |
| `/tfwr-save` | セーブのアンロック状況 |
| `/tfwr-control` | `main` 起動、output、スナップショット |
| `/tfwr-sync-skills` | 農場変更後、`.agents/skills` だけ更新 |

skill の編集は `.agents/skills/` だけ。`.claude` / `.grok` / `.cursor` に二本目を作らない。

## 農場スクリプト

テンプレートは**あなたの** `Saves\Save0` にコピーされます。必要なウィンドウ名：

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py` はエディタ用スタブです。ゲーム内で `import` しないでください。

稼働中のスクリプトを git テンプレートへ戻す：

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## 注意

- ライセンスファイルはありません。自己責任で使ってください。
- 拡張に `set_world_size` を使わない（フィールドがクリアされる）。
- 明示しない限り `unlock()` しない。
- インデントは **Tab**。
