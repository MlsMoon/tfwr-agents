# TFWR Agents

Área de trabalho de Agent para **The Farmer Was Replaced**.

Uma única árvore canônica de skills, instalador em um passo e modelos de scripts. O save não entra no repositório.

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

## O que vem

- `AGENTS.md` — regras para Cursor / Claude / Grok quando esta pasta é o workspace
- `.agents/skills/` — **a única cópia das skills**. Os editores as veem pelos links do setup
- `templates/Save0/` — scripts do drone (`main`, girassol, abóbora, cacto, dinossauro, labirinto, …)
- `setup.bat` / `setup.ps1` — copia skills e scripts para a pasta do jogo e cria os links

## O que não vem

- `Saves/` (incluindo `save.json`)
- `Backup/`
- `Player.log`, `output.txt`, `options.txt`, arquivos do Steam Cloud
- `.claude/skills`, `.grok/skills`, `.cursor/skills` (só links, não uma segunda cópia)

## Requisitos

- Jogo instalado e aberto pelo menos uma vez (pasta de userdata)
- Windows (`mklink`; ative o **Modo de desenvolvedor** se falhar)
- [Cursor](https://cursor.com) (ou Claude Code / Grok) aberto na **pasta de userdata**
- Python 3 para `tfwr_control.py`
- Opcional: SDK do .NET, só para recompilar o helper

Pasta padrão:

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## Inicializar (um passo)

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

O script:

1. acha a pasta de userdata (ou `-GameRoot`)
2. copia `AGENTS.md` e `.agents\skills` (pula se você já estiver lá)
3. copia `templates\Save0\*.py` para `Saves\Save0` — **nunca grava `save.json`**
4. cria:

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

Caminho próprio:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -GameRoot "D:\path\TheFarmerWasReplaced"
```

Só skills, manter seus scripts atuais:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

Um `.py` novo em `Saves\Save0` precisa de uma **janela com o mesmo nome** no editor **do jogo**. Arquivo no disco sozinho não é módulo importável.

## Uso

1. Abra a pasta de userdata no Cursor (`AGENTS.md` e `Saves\Save0`).
2. No jogo: `file watcher = enabled`, `tabs to spaces = disabled`. Veja `options.example.txt`.
3. Inicie a fazenda no terminal dessa pasta:

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **Não aperte F5.** F5 roda a janela em foco, muitas vezes não é `main`.
5. Para a fazenda **não execute `main_maze`**. O labirinto só farma ouro.
6. Com file watcher, os `Saves\Save0\*.py` existentes recarregam. Depois de mudar a estratégia, `/tfwr-sync-skills` em `.agents\skills`.

Comandos úteis (mesma pasta):

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| Comando | Significado |
| --- | --- |
| `run-main` / `restart` | Inicia `main` pela API do jogo (sem mouse) |
| `parse` | Classifica `output.txt` |
| `snapshot` | Inventário, drones, velocidade, log |
| `stop` | `StopMainExecution` |

## Skills

| Skill | Quando |
| --- | --- |
| `/tfwr-farm` | Scripts do drone (dialeto, Tab, módulos) |
| `/tfwr-strategy` | VALUE, `pick_mode`, girassol / abóbora / cacto / dino |
| `/tfwr-save` | Desbloqueios do save |
| `/tfwr-control` | Iniciar `main`, output, snapshot |
| `/tfwr-sync-skills` | Depois de mudar a fazenda, atualizar só `.agents/skills` |

Edite skills só em `.agents/skills/`. Não mantenha uma segunda árvore em `.claude` / `.grok` / `.cursor`.

## Scripts da fazenda

Os modelos vão para o **seu** `Saves\Save0`. Nomes de janela:

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py` é stub do editor. Não faça `import` no jogo.

Exportar seus scripts vivos para os modelos git:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## Notas

- Sem arquivo de licença. Use por sua conta e risco.
- Não use `set_world_size` para expandir (limpa o campo).
- Não chame `unlock()` a menos que peça explicitamente.
- Indentação com **Tab**.
