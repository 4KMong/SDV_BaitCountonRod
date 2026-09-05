$ErrorActionPreference = "Stop"

$projectPath = Join-Path $PSScriptRoot "4KMong.BaitCountOnRod.csproj"
$manifestPath = Join-Path $PSScriptRoot "manifest.json"
$licensePath = Join-Path $PSScriptRoot "LICENSE"

$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$version = $manifest.Version
$modFolderName = "(4KMong) Bait Count On Rod"

Write-Host "Building Bait Count On Rod $version..."
dotnet build $projectPath -c Release
if ($LASTEXITCODE -ne 0) {
    throw "Build failed."
}

$dllPath = Join-Path $PSScriptRoot "bin\Release\net6.0\BaitCountOnRod.dll"
if (-not (Test-Path $dllPath)) {
    throw "Built DLL not found: $dllPath"
}

$artifactsDir = Join-Path $PSScriptRoot "artifacts"
$stageDir = Join-Path $artifactsDir $modFolderName
$zipPath = Join-Path $artifactsDir "BaitCountOnRod-$version.zip"

if (Test-Path $stageDir) {
    Remove-Item $stageDir -Recurse -Force
}
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

New-Item -ItemType Directory -Path $stageDir -Force | Out-Null
Copy-Item $dllPath (Join-Path $stageDir "BaitCountOnRod.dll")
Copy-Item $manifestPath (Join-Path $stageDir "manifest.json")
Copy-Item $licensePath (Join-Path $stageDir "LICENSE")

Compress-Archive -Path $stageDir -DestinationPath $zipPath -CompressionLevel Optimal

Write-Host "Release package created: $zipPath"
