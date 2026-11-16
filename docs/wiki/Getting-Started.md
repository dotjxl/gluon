# Getting started

1. Install Steam on an Apple silicon Mac and make sure Rosetta is available.
2. Download the `.pkg` from the [Gluon release page](https://github.com/dotjxl/gluon/releases). Close Steam and any Wine games, then open the package and follow the prompts. Gluon needs permission to prepare the Steam application that your account owns.
3. Restart Steam. Use **Properties → Compatibility** to select Gluon per game. The compatibility manager also routes eligible Windows games automatically.
4. In **Steam → Settings → Gluon**, use **Preload Wine** to warm startup files before Play. **Automatically update Gluon** checks for stable releases and applies verified updates when Steam and Wine are closed. Both switches start off.

The package uses ad-hoc signing for local integration. See the [installation and recovery reference](../STEAMPLAY.md#installation-and-recovery) for Gatekeeper, permissions, and restoration behavior.

## Check, repair, or remove the installation

Use the command that matches your situation. Close Steam and Wine before running repair or uninstall.

```sh
"$HOME/Library/Application Support/Gluon/bin/gluonctl" status
"$HOME/Library/Application Support/Gluon/bin/gluonctl" repair
"$HOME/Library/Application Support/Gluon/bin/gluon-uninstall"
```

For a custom Steam path or multiple Steam copies, select the application explicitly with `gluonctl install --steam-app "$HOME/Applications/Steam.app"`. Repair normally reuses the recorded copy. Uninstall restores the original Steam application and keeps your games, saves, and Wine prefixes. [Get help with a failed install](Troubleshooting.md#the-package-fails).
