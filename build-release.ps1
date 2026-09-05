$ErrorActionPreference = "Stop"

$projectPath = Join-Path $PSScriptRoot "4KMong.BaitCountOnRod.csproj"
$manifestPath = Join-Path $PSScriptRoot "manifest.json"

[xml]$project = Get-Content $projectPath
$version = $project.Project.PropertyGroup.Version | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($version)) {
    throw "Project version not found in 4KMong.BaitCountOnRod.csproj."
}

$modFolderName = "(4KMong) Bait Count On Rod"

Write-Host "Building Bait Count On Rod $version..."
dotnet build $projectPath -c Release
if ($LASTEXITCODE -ne 0) {
    throw "Build failed."
}

$dllPath = Join-Path $PSScriptRoot "bin/Release/net6.0/BaitCountOnRod.dll"
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

$manifestText = Get-Content $manifestPath -Raw
$manifestText = $manifestText.Replace("%ProjectVersion%", $version)
Set-Content -Path (Join-Path $stageDir "manifest.json") -Value $manifestText -Encoding utf8NoBOM

Compress-Archive -Path $stageDir -DestinationPath $zipPath -CompressionLevel Optimal

Write-Host "Release package created: $zipPath"
Write-Host "Package contents:"
Write-Host "  $modFolderName/BaitCountOnRod.dll"
Write-Host "  $modFolderName/manifest.json"
