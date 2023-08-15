# Continuous loop to keep trying to generate improved models
# Variables in config.json:
# {
#     "min_count": 1 - 10,
#     "npmi_scoring": true or false
#
#     "threshold": -1 to 1 when npmi_scoring is true, otherwise one of: 0.3, 0.5, 0.8, 1, 1.5, 2, 3, 4, 5, 10
#     "batch_size": multiples of 2: 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, etc.
#     "penalty": "elasticnet", "l1", "l2"
#     "alpha": between 0.00001 and 1
# }

# The base values are set by finding the best iteration in ./analytics/*.json ["score"]
# The training model values can be changed every time, but the first two embeddings values only change every fourth run
# After changing the embeddings values, ./run.ps1 is called which embeds and then creates a new training set
# After changing the training model values, ./app.py is called which trains the model and then scores it, creating an analytics entry
# Every ten times, the data is saved to git and pushed to github
function Find-HighestScoringConfig {
    $jsonFiles = Get-ChildItem -Path ./analytics/ -Filter *.json

    $options = Get-Content -Path ./config_options.json | ConvertFrom-Json
    $bestConfig = $null
    $bestScore = 0

    foreach ($file in $jsonFiles) {
        $content = Get-Content -Path $file.FullName | ConvertFrom-Json
        $currentScore = $content.average_accuracy + $content.score

        if ($currentScore -gt $bestScore) {
            $bestScore = $currentScore
            $bestConfig = $content.config
        }
    }

    return $bestConfig, $bestScore
}

function Get-NextValue {
    param ([Array]$values, [Object]$currentValue)
    $currentIndex = $values.IndexOf($currentValue)
    $shift = Get-Random -Minimum -1 -Maximum 2
    return $values[($currentIndex + $shift + $values.Count) % $values.Count]
}

$i = 0
while (1 -eq 1) {
    $options = Get-Content -Path ./config_options.json | ConvertFrom-Json
    $bestConfig, $bestScore = Find-HighestScoringConfig
    $configPath = "./config.json"
    $config = if (Test-Path -Path $configPath) { Get-Content -Path $configPath | ConvertFrom-Json } else { @{} }

    Write-Host "Best config: $($bestConfig | ConvertTo-Json)"
    Write-Host "Best score: $bestScore"

    $options.ml_model_properties.PSObject.Properties | ForEach-Object {
        $property = $_.Name
        $values = $_.Value
        $config.$property = if ($bestScore -lt 1) { Get-Random -InputObject $values } else { Get-NextValue -values $values -currentValue $config.$property }
    }

    $encodingMethod = if ($bestScore -lt 1) { Get-Random -InputObject @('USE', 'W2V', 'PHR') } else { $config.oracle_text_encoding_method }
    $config.oracle_text_encoding_method = $encodingMethod
    $encodingOptions = $options.oracle_text_encoding.$encodingMethod

    $encodingOptions.PSObject.Properties | ForEach-Object {
        $property = $_.Name
        $values = $_.Value
        switch ($property) {
            "npmi_scoring" { $config.npmi_scoring = Get-NextValue -values $values -currentValue $config.npmi_scoring }
            Default { $config.$property = if ($bestScore -lt 1) { Get-Random -InputObject $values } else { Get-NextValue -values $values -currentValue $config.$property } }
        }
    
        # Special case for PHR and npmi_scoring
        if ($encodingMethod -eq "PHR" -and $property -eq "npmi_scoring") {
            $thresholdProperty = if ($config.npmi_scoring) { "npmi_scoring_true" } else { "npmi_scoring_false" }
            $config.threshold = Get-NextValue -values $encodingOptions.$thresholdProperty.threshold -currentValue $config.threshold
        }
    }

    if ($encodingMethod -ne $config.oracle_text_encoding_method) {
        Write-Host "New config: $($config | ConvertTo-Json)"
        $config | ConvertTo-Json | Set-Content -Path $configPath
        try {
            ./run.ps1
        }
        catch {
            Write-Host "Error: $_"
        }
    } else {
        Write-Host "New config: $($config | ConvertTo-Json)"
        $config | ConvertTo-Json | Set-Content -Path $configPath
        try {
            ./app.py
        }
        catch {
            Write-Host "Error: $_"
        }
    }

    if ($i % 10 -eq 0) {
        Write-Host "Saving to git"
        git add .
        git commit -m "Auto commit $($i / 10) for hyperparameter tuning"
        git push
    }
    $i = $i + 1
}

