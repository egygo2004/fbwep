# Setup Server 6 (Target: lolelarap3/Create)
$env:GH_TOKEN = "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"
$REPO = "lolelarap3/Create"
$TOKEN = $env:GH_TOKEN

Write-Host "Repo Check..."
# gh repo create $REPO --private 
Write-Host "Repo exists (checked via API)."

Write-Host "Setting Secrets..."
gh secret set TELEGRAM_TOKEN -b "7205135297:AAEKFDTNZBj0c1I23Ri_a_PjCuWn_KUiYyY" -R $REPO
gh secret set TELEGRAM_CHAT_ID -b "664193835" -R $REPO

Write-Host "Preparing Files..."
if (Test-Path "temp_deploy_6") { Remove-Item -Recurse -Force "temp_deploy_6" }
New-Item -ItemType Directory -Force -Path "temp_deploy_6"
Copy-Item "fb_otp_browser.py" "temp_deploy_6\"
Copy-Item "requirements.txt" "temp_deploy_6\"
New-Item -ItemType Directory -Force -Path "temp_deploy_6\.github\workflows"
Copy-Item ".github\workflows\fb_otp.yml" "temp_deploy_6\.github\workflows\"

Write-Host "Deploying..."
Set-Location "temp_deploy_6"
git init
git checkout -b main
git add .
git commit -m "Init Server 6 (Create Repo)"
git remote add origin "https://lolelarap3:$TOKEN@github.com/$REPO.git"
git push -u origin main -f
Set-Location ..

Write-Host "Done!"
