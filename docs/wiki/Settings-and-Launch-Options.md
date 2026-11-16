# Settings and launch options

## Steam preferences

Open **Steam → Settings → Gluon**. Older client menus may call Settings **Preferences**.

| Preference | Default | Behavior |
|---|---|---|
| Use Gluon for 32-bit Mac games | On | Selects the available Windows launch for an eligible legacy Mac game. Explicit per-game choices take priority. |
| Preload Wine | Off | Warms Wine executables and startup libraries after Steam opens. macOS reads ahead on files from the last launched Steam game. |
| Automatically update Gluon | Off | Checks for stable Gluon releases and applies verified updates once Steam and Wine have closed. |

Gluon uses Steam's catalogue and available installed-file evidence to choose the Windows route. Positive evidence of a 64-bit Mac build takes priority over a legacy label. The **32-bit Mac only** notice applies when the catalogue shows a legacy Mac version with no other platform build. [Legacy Mac and catalogue details](../STEAM-SETTINGS.md) · [Graphics and compatibility](Graphics-and-Compatibility.md#legacy-mac-games).

## Change one game

Under **Properties → General → Launch Options**, put the setting after `%command%`. Use one setting at a time when isolating a problem. Remove it to return to the configured default.

```text
%command% GLUON_OVERLAY=0
```

You can also put `NAME=value` lines in `~/Library/Application Support/Gluon/settings.env` or `~/Library/Application Support/Gluon/games/<appid>.env`. Gluon applies global settings, then the game's settings file, then recognized Steam Launch Options. The App ID is the number in the Steam store URL. [Full runtime settings reference](../RUNTIME.md#settings).

| Setting | When to use it |
|---|---|
| `GLUON_OVERLAY=0` | Isolate a problem that appears when Steam's overlay loads. |
| `GLUON_FOCUS=0` | Disable Wine's automatic focus handoff for this game. |
| `GLUON_CAFFEINATE=0` | Allow normal display and idle sleep during this game. |
| `GLUON_GL_COMPAT_AS_CORE=1` | Try Apple's OpenGL core profile for a game requesting an older compatibility profile. |
| `WINE_D3D_CONFIG=renderer=gl` | Select OpenGL for a game using WineD3D. Use `renderer=vulkan` to select Vulkan. |
| `GLUON_HAPPY_WHEELS_CLASSIC_WINDOW=0` | Use Happy Wheels' own default presenter. Gluon normally selects its classic window to avoid the shared-texture timeout. |

DXVK, DXMT, WineD3D, and MoltenVK each read their own settings. Identify the game's active backend first. [Graphics and compatibility](Graphics-and-Compatibility.md).
