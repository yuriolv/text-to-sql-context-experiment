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
# Passada extra só quando o log pede (referências cruzadas ou backref mudaram).
if (Select-String -Path build/main.log -Pattern 'Rerun to get|has changed' -Quiet) { Run pdflatex $latex }

$log = Get-Content build/main.log -Raw
$pages = [regex]::Match($log, 'Output written on[\s\S]{0,300}?\((\d+) pages').Groups[1].Value
$undef = [regex]::Matches($log, "(Reference|Citation) `[^']+' on page \d+ undefined").Count
$warn  = [regex]::Matches($log, '(?m)^(LaTeX|Package \w+) Warning').Count
"PDF: build/main.pdf | paginas: $pages | avisos: $warn | referencias indefinidas: $undef"
