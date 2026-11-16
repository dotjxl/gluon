# Graphics and compatibility

| Game API | Gluon runtime path | Limit |
|---|---|---|
| Direct3D 9 | DXVK through MoltenVK | Check rendering in the game, since device creation only covers the start of the graphics stack. |
| Direct3D 10/11 | DXMT through Metal | Support varies with the game and its rendering features. |
| Vulkan | Wine Vulkan loader through MoltenVK | A device or extension probe does not establish complete rendering support. |
| OpenGL | Wine's macOS driver and Apple's OpenGL | Compatibility features removed from Apple's core profile remain unavailable. |

Steam Input, launchers, audio, and Steam overlay behavior vary by game. Windows kernel drivers and kernel anti-cheat are outside this compatibility path.

## Per-game settings

Open **Properties → General → Launch Options**. Keep `%command%` first, then add an option for the affected game. Remove the option to restore the default.

| Option | Use |
|---|---|
| `%command% GLUON_GL_COMPAT_AS_CORE=1` | Try Apple's core OpenGL profile for a game that requests an older compatibility profile. Gluon automatically selects this route for Primordialis on the bundled runtime when that patch is available. |
| `%command% WINE_D3D_CONFIG=renderer=gl` | Ask WineD3D to use OpenGL for a game that loads WineD3D. `renderer=vulkan` selects its Vulkan renderer. |
| `%command% GLUON_OVERLAY=0` | Isolate a game or window problem that appears when the Steam overlay loads. |
| `%command% GLUON_HAPPY_WHEELS_CLASSIC_WINDOW=0` | Restore Happy Wheels' default native presenter. Gluon uses the game's classic window by default to avoid its shared-texture timeout. |

DXVK, DXMT, WineD3D, and MoltenVK each read their own settings. See the [runtime settings reference](../RUNTIME.md#settings) and [graphics verification results](../graphics-cloud-verification.md) for details.
