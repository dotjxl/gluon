# CLI reference

The standard installation puts `gluonctl` in `~/Library/Application Support/Gluon/bin/`. Quote the path because it contains spaces. Use the installed tool under the macOS account that owns the Steam application.

```sh
GLUON_CTL="$HOME/Library/Application Support/Gluon/bin/gluonctl"
"$GLUON_CTL" --help
"$GLUON_CTL" status
```

## Installation and maintenance

| Command | What it does |
|---|---|
| `status` | Shows the tracked Steam application, client build and validation state, Gluon version when recorded, runtime, and whether automatic updates are enabled. |
| `install [--steam-app PATH]` | Installs the staged Steam Play integration and prepares the applicable runtime and Cloud paths. |
| `repair [--steam-app PATH]` | Runs the installation recovery and validation flow. Use it if setup was interrupted or the tracked Steam app needs repair. |
| `sync --dry-run` | Previews pending runtime activation and eligible Steam integration repair. |
| `sync` | Applies eligible staged runtime and Steam integration changes while idle. The background agent normally performs this step. |
| `sync --log` | Writes the sync result to `logs/agent.log` in the Gluon data folder. |
| `migrate` | Restores recorded legacy Gluon changes. It preserves originals and recovery backups. This is for migration or recovery work. |
| `uninstall` | Restores tracked Steam applications and legacy settings. The `gluon-uninstall` wrapper also removes Gluon's per-user program files and its background agent. |

Close Steam and Wine before installation, repair, or uninstall. `--steam-app` selects the exact application when you have multiple copies or a custom location. Start with [Getting started](Getting-Started.md#check-repair-or-remove-the-installation) for the usual commands.

## Automatic Steam Cloud

| Command | What it does |
|---|---|
| `cloud status APPID` | Reports preparation state or the saved reason a game's Cloud path could not be prepared. |
| `cloud prepare APPID` | Repairs a game's preparation while Steam and Wine are closed. Use it after diagnosing the relevant error. |

`APPID` is the numeric Steam ID from the game's store URL. [Steam Cloud and saves](Steam-Cloud-and-Saves.md).

## Legacy Mac games

`legacy-mac check PATH` inspects an installed Mac app with the separately installed mac32 runner. `legacy-mac run PATH` starts it with that runner. Add `--runner PATH` if mac32 lives outside the usual locations. [Legacy Mac compatibility](Graphics-and-Compatibility.md#legacy-mac-games).

## Development commands

`console COMMAND [--wait SECONDS]` sends a Steam console command through an active local Steam development bridge. The Steam integration invokes the internal `preload` command. Use the Preload Wine switch in Steam Settings to enable it. [Settings and launch options](Settings-and-Launch-Options.md#steam-preferences).
