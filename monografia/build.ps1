# Compila a monografia localmente com MiKTeX (pdflatex + bibtex).
# Uso, a partir da raiz do repositório ou de monografia/:
#   powershell -ExecutionPolicy Bypass -File monografia/build.ps1
# Saída: monografia/build/main.pdf (pasta ignorada pelo git).
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force build | Out-Null

$latex = @('-interaction=nonstopmode', '-halt-on-error', '-file-line-error', '-output-directory=build', 'main.tex')

function Run($exe, $argv) {
  & $exe @argv | Out-File -Encoding utf8 -Append build/build.log
  if ($LASTEXITCODE -ne 0) { throw "$exe falhou (código $LASTEXITCODE); veja build/build.log e build/main.log" }
}

Remove-Item build/build.log -ErrorAction SilentlyContinue
Run pdflatex $latex
Run bibtex @('build/main')
Run pdflatex $latex
Run pdflatex $latex

$log = Get-Content build/main.log -Raw
$pages = [regex]::Match($log, 'Output written on .*?\((\d+) pages').Groups[1].Value
$undef = [regex]::Matches($log, "(Reference|Citation) `[^']+' on page \d+ undefined").Count
$warn  = [regex]::Matches($log, '(?m)^(LaTeX|Package \w+) Warning').Count
"PDF: build/main.pdf | paginas: $pages | avisos: $warn | referencias indefinidas: $undef"
