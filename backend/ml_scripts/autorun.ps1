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


$i = 0
while (1 -eq 1) {
    # Get the config values of the highest scoring iteration from ./analytics/*.json
    $jsonFiles = Get-ChildItem -Path ./analytics/ -Filter *.json

    $bestConfig = $null
    $bestScore = -1

    foreach ($file in $jsonFiles) {
        $content = Get-Content -Path $file.FullName | ConvertFrom-Json
        $currentScore = $content.average_accuracy + $content.score

        if ($currentScore -gt $bestScore) {
            $bestScore = $currentScore
            $bestConfig = $content.config
        }
    }

    Write-Host "Highest scoring config: $($bestConfig | ConvertTo-Json) with score: $bestScore"

    $config = $bestConfig

    # Override so that the embeddings values are changed every fourth run
    $appConfig = Get-Content -Path ./config.json | ConvertFrom-Json
    $config.min_count = $appConfig.min_count
    $config.npmi_scoring = $appConfig.npmi_scoring


    if ($config.npmi_scoring -eq $true) { 
        if ($bestScore -lt 1) {
            $config.threshold = (Get-Random -Minimum -10 -Maximum 10) / 10
        } else {
            $random_shift = (Get-Random -Minimum -3 -Maximum 3) / 10
            $config.threshold = $config.threshold + $random_shift
            if ($config.threshold -lt -1) { $config.threshold = -1 }
            if ($config.threshold -gt 1) { $config.threshold = 1 }
        }
    } else {
        $thresholds = @(0.3, 0.5, 0.8, 1, 1.5, 2, 3, 4)
        if ($bestScore -lt 1) {
            $config.threshold = Get-Random -InputObject $thresholds
        } else {
            $current_threshold_index = $thresholds.IndexOf($config.threshold)
            $random_shift = Get-Random -Minimum -2 -Maximum 2
            if ($current_threshold_index + $random_shift -lt 0) { $random_shift = 0 }
            if ($current_threshold_index + $random_shift -gt $thresholds.Count - 1) { $random_shift = 0 }
            $config.threshold = $thresholds[$current_threshold_index + $random_shift]
        }
    }

    $batch_sizes = @(4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576) # Removed lower multiples of 2
    if ($bestScore -lt 1) {
        $config.batch_size = Get-Random -InputObject $batch_sizes
    } else {
        $current_batch_size_index = $batch_sizes.IndexOf($config.batch_size)
        $random_shift = Get-Random -Minimum -2 -Maximum 2
        if ($current_batch_size_index + $random_shift -lt 0) { $random_shift = 0 }
        if ($current_batch_size_index + $random_shift -gt $batch_sizes.Count - 1) { $random_shift = 0 }
        $config.batch_size = $batch_sizes[$current_batch_size_index + $random_shift]
    }

    $penalties = @("elasticnet", "l1") #Removed "l2" because it was not improving the score
    $config.penalty = Get-Random -InputObject $penalties

    $alphas = @(0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1, 1)
    if ($bestScore -lt 1) {
        $config.alpha = Get-Random -InputObject $alphas
    } else {
        $current_alpha_index = $alphas.IndexOf($config.alpha)
        $random_shift = Get-Random -Minimum -2 -Maximum 2
        if ($current_alpha_index + $random_shift -lt 0) { $random_shift = 0 }
        if ($current_alpha_index + $random_shift -gt $alphas.Count - 1) { $random_shift = 0 }
        $config.alpha = $alphas[$current_alpha_index + $random_shift]
    }

    if ($i % 2 -eq 0) {
        Write-Host "Changing embeddings"
        if ($bestScore -lt 1) {
            $config.min_count = Get-Random -Minimum 1 -Maximum 10
        }
        else {
            $random_shift = Get-Random -Minimum -2 -Maximum 2
            $config.min_count = $config.min_count + $random_shift
            if ($config.min_count -lt 1) { $config.min_count = 1 }
            if ($config.min_count -gt 10) { $config.min_count = 10 }
        }

        if ($config.npmi_scoring -eq $false) { 
            $config.npmi_scoring = $true
            $config.threshold = (Get-Random -Minimum -10 -Maximum 10) / 10
        } else { 
            $config.npmi_scoring = $false
            $config.threshold = Get-Random -InputObject $thresholds
        }
        Write-Host "New config: $($config | ConvertTo-Json)"
        # Save to the ./config.json file
        $config | ConvertTo-Json | Set-Content -Path ./config.json 
        ./run.ps1
    } else {
        Write-Host "Changing training model"
        Write-Host "New config: $($config | ConvertTo-Json)"
        $config | ConvertTo-Json | Set-Content -Path ./config.json
        ./app.py
    }
    if ($i % 10 -eq 0) {
        Write-Host "Saving to git"
        git add .
        git commit -m "Auto commit $($i / 10) for hyperparameter tuning"
        git push
    }
    $i = $i + 1
}

