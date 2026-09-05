# Bait Count On Rod

A lightweight Stardew Valley SMAPI mod that shows the equipped bait icon and remaining bait count directly on the fishing rod icon in menus.

## Features

- Shows the currently equipped bait on the fishing rod icon.
- Shows the remaining bait stack count using Stardew Valley's tiny-digit style.
- Supports normal bait and colored/specific bait variants.
- Hides the overlay when vanilla menu stack drawing is hidden.
- Uses a small sprite cache and clears it when game content assets are invalidated, improving compatibility with content-replacing mods.

## Requirements

- Stardew Valley 1.6+
- SMAPI 4.0.0+

## Installation

1. Install SMAPI.
2. Download the latest release.
3. Extract the `(4KMong) Bait Count On Rod` folder into your Stardew Valley `Mods` folder.
4. Launch the game through SMAPI.

The installed mod folder contains only:

- `BaitCountOnRod.dll`
- `manifest.json`

## Updates

The mod supports update checks through both distribution channels:

- Nexus Mods: https://www.nexusmods.com/stardewvalley/mods/41957
- GitHub Releases: https://github.com/4KMong/SDV_BaitCountonRod/releases

## Automated builds

GitHub Actions builds the mod automatically on pushes, pull requests, and manual workflow runs.

- Normal builds create a downloadable `BaitCountOnRod-<version>.zip` artifact.
- Pushing a version tag such as `v1.0.1` creates the matching GitHub Release automatically.
- The tag version must match the `<Version>` value in `4KMong.BaitCountOnRod.csproj`.
- The generated release ZIP contains only the mod folder with `BaitCountOnRod.dll` and the processed `manifest.json`.

The project version is maintained in `4KMong.BaitCountOnRod.csproj`. The source `manifest.json` uses `%ProjectVersion%`, which is replaced with the project version during packaging.

## Building locally

The project uses `Pathoschild.Stardew.ModBuildConfig` and targets .NET 6.

On a development PC with Stardew Valley installed:

```powershell
./build-release.ps1
```

The script builds the project in Release configuration and creates the same two-file mod package in the `artifacts` folder.

## License

MIT License. See [LICENSE](LICENSE).
