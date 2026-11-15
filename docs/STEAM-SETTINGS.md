# Gluon in Steam Settings

Steam > Settings (Preferences on older macOS clients) > Gluon contains **Use
Gluon for 32-bit Mac games**. It starts enabled and takes effect when saved.
Existing per-game compatibility choices, including another tool or No
Compatibility Tool, take precedence.

Steam uses the Windows version automatically when it offers a Windows launch
for your selected branch and marks the Mac build as legacy. Gluon uses the
catalogue's 64-bit Mac compatibility flags, so it can choose Windows before the
old Mac files are installed. An explicit 64-bit or Apple Silicon declaration or
an installed 64-bit Mach-O overrides the legacy flag. For a game with incomplete
Steam metadata and no installed Mac binary, this policy can choose Windows even
if the publisher shipped a 64-bit Mac build without marking it in Steam.
Per-game compatibility choices still take precedence.

The reader also identifies installed 32-bit executables and recognizes Valve
wrappers such as Half-Life's `hl.sh` without executing them. Gluon warms its
catalogue at startup and refreshes it when Steam updates its metadata.

Positive observations survive Steam replacing the Mac depots with Windows depots.
The helper saves bounded evidence in `Gluon/state/mac32-evidence.json`, using atomic
writes and a process lock. Each observation is tied to the selected Mac branch,
Mac launch configuration, architecture declarations, and the Mac/shared depot
manifest identities (including resolvable shared-depot references). Windows-only
depot updates and global build IDs do not invalidate it. Mac/shared depot or launch
changes, a branch switch, or any new 64-bit evidence immediately revoke it. An
observation is tied to the installed depot manifests before it is recorded, so
old leftover files cannot attest a newly advertised Mac version. It is exposed to
automatic routing only after it has been persisted;
unversioned Mac content and corrupt or unwritable evidence stay conservative.

A Windows launch fallback also handles games whose common platform flags advertise
macOS but whose launch catalogue defines only Windows executables, such as
Spacewar. It does not classify a Windows PE as a native Mac32 executable and does
not depend on this toggle. A native Mac launch on any branch, Mac-specific depot,
Mac64/Apple Silicon flag, unresolved shared-depot platform or unknown launch
command prevents that correction. Explicit per-game choices still win.

The preference lives in `Gluon/steamplay/auto-mac32` and persists across
installer upgrades. Steam's bridge saves changes immediately. The Compatibility
page reports the result and shares the updated preference with other Steam
windows on the same origin.

**Preload Wine** is off by default. When enabled, Gluon warms the packaged Wine
runtime at low priority after Steam starts. It also warms once when first
enabled. The warmup uses a disposable prefix and exits on its own. Existing
games and custom runtimes keep their own startup and shutdown behavior.

`steamplay/check-settings.py` runs on GitHub macOS runners or on a prepared fixture checkout. It exercises the
built appinfo helper with disposable metadata and Mach-O fixtures, production
preference persistence across process restarts, the actual resolver/Cloud hook
against a fake manager, and the exact Settings UI script against a JSX/DOM bridge.
The existing upstream gate fixtures continue to require exact anchors for both
supported Settings shapes and refuse drifted Steam UI files.

Steam's game page shows **32-bit Mac only · Requires a legacy Mac runtime**
when its catalogue indicates a 32-bit Mac game with no other platform build.
For these games, Gluon can call the experimental
[mac32 runner](https://github.com/Shagulka/mac32) once it is installed:

```sh
"$HOME/Library/Application Support/Gluon/bin/gluonctl" legacy-mac check "/path/to/Game.app"
"$HOME/Library/Application Support/Gluon/bin/gluonctl" legacy-mac run "/path/to/Game.app"
```

Pass `--runner /path/to/mac32` if the executable is outside the default
install locations. Run `check` first to look for missing system functions.
The runner supports a subset of Intel Mac apps, and Steam-owned games still
need an active Steam account where required by the game. This command is
separate from Steam's Play button. For titles that need an older Mac system,
[Mojave was the last macOS release with native 32-bit support](https://support.apple.com/en-us/103076).
[Valve has ended Steam support for Mojave](https://help.steampowered.com/en/faqs/view/743F-2E0E-C9A5-C375).
