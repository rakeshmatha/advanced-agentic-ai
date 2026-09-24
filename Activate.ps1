# Activate the project virtualenv from the repo root.
# PowerShell:  . .\Activate.ps1

$Activate = Join-Path $PSScriptRoot ".venv/bin/Activate.ps1"
if (-not (Test-Path $Activate)) {
    Write-Error "No .venv found. From this folder run: python3 -m venv .venv"
    return
}
. $Activate

# Day 1
function mechanics { python -m day1.lab.mechanics @args }
function prompts { python -m day1.lab.prompts @args }
function embeddings { python -m day1.lab.embeddings @args }
# Day 2
function rag { python -m day2.lab.rag_system @args }
function Invoke-ArchitectureDecision { python -m day2.lab.decision_framework @args }
Set-Alias -Name architecture-decision -Value Invoke-ArchitectureDecision
function Invoke-BuildVsBuy { python -m day2.lab.build_vs_buy @args }
Set-Alias -Name build-vs-buy -Value Invoke-BuildVsBuy
# Day 3
function restmcp { python -m day3.lab.rest_mcp @args }
function singlemulti { python -m day3.lab.single_multi_agent @args }
function assistant { python -m day3.lab.assistant @args }
function sequential { python -m day3.lab.sequential @args }
function router { python -m day3.lab.router @args }
function supervisor { python -m day3.lab.supervisor @args }
function compare { python -m day3.lab.compare @args }
function retail_multi_agent { python -m day3.retail_multi_agent @args }

