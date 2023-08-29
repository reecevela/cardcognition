# Get array of oracle_texts from ..\random_oracle_texts.json
# Overwrite ..\failed_oracle_texts.json with failed antlr parse attempts
# Overwrite ..\passed_oracle_texts.json with passed antlr parse attempts

$oracle_texts = Get-Content -Path ..\random_oracle_texts.json | ConvertFrom-Json

$failed_oracle_texts = @()

foreach ($oracle_text in $oracle_texts) {
    try {
        antlr4-parse .\MTG.g4 abilities $oracle_text
    }
    catch {
        $failed_oracle_texts += $oracle_text
    }
}

$failed_oracle_texts | ConvertTo-Json | Out-File -FilePath ..\failed_oracle_texts.json
$passed_oracle_texts = $oracle_texts | Where-Object { $failed_oracle_texts -notcontains $_ }

$passed_oracle_texts | ConvertTo-Json | Out-File -FilePath ..\passed_oracle_texts.json