# Steam Cloud and saves

Steam handles cloud downloads, uploads, preferences, and conflict dialogs. For games with Windows profile save rules, Gluon prepares the expected paths before Steam begins its launch sync. Games with Steam API Cloud or save rules rooted in the game's installation use Steam's native paths. [Steam Cloud integration](../STEAM-CLOUD.md).

## Find the active prefix

A plain-Wine game usually stores its prefix at `<Steam library>/steamapps/compatdata/<appid>/pfx-wine`. Find the library under **Steam → Settings → Storage**. The matching `launch-<appid>.log` records the exact prefix path for a launch, including custom library paths. [Log locations](Troubleshooting.md#find-the-relevant-log).

The prefix contains the Windows drive and user profiles. The game's publisher determines its save path. Gluon can expose `pfx` or `steamuser` aliases onto the existing profile so Wine and Steam can find the same files. Recovery can also retain a retired Gluon Proton prefix under a `.gluon-retired-pfx-*` name. Preserve those directories and recovery copies while investigating. [Save preservation](../STEAM-CLOUD.md#save-preservation).

## Diagnose missing or conflicting saves

1. Close the game. Record the Cloud message and App ID.
2. Run `cloud status` and inspect `~/Library/Application Support/Gluon/steamplay/cloud.log`.
3. Identify the active prefix and back up the known save folders before moving anything.
4. If status reports conflicting profiles, unexpected links, or an incomplete backup, keep both copies and include the exact error in a support report. If prompted by Steam to choose a conflicting copy, compare the dates and each device's known progress first.

Replace `123456` with your game's App ID.

```sh
"$HOME/Library/Application Support/Gluon/bin/gluonctl" cloud status 123456
```

`cloud prepare` is a repair command for a known game while Steam and Wine are fully closed. Ordinary play performs preparation automatically. [CLI reference](CLI-Reference.md#automatic-steam-cloud) · [Support](../../SUPPORT.md).
