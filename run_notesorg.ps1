Write-Host 'Launching NotesOrg API (DI) - from any directory'
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$src = Join-Path $scriptPath 'src'
$env:PYTHONPATH = $src
python -m notesorg.api
