@echo off
echo ========================================
echo Deploying Settings Fix to Railway
echo ========================================
echo.

echo Step 1: Adding modified files to Git...
git add frontend/index.html
git add SETTINGS_FIX_COMPLETE.md
git add BEFORE_AFTER_SETTINGS.md
git add DEPLOY_SETTINGS_FIX.md
git add deploy_settings_fix.bat

echo.
echo Step 2: Committing changes...
git commit -m "Fix: Settings page now loads real data from database - Removed hardcoded DEFAULT_SETTINGS - Fixed AI provider (NVIDIA not Claude) - Fixed WhatsApp display - Enhanced logging - Added refresh button"

echo.
echo Step 3: Pushing to Railway (triggers auto-deployment)...
git push origin main

echo.
echo ========================================
echo Deployment initiated!
echo ========================================
echo.
echo Railway will auto-deploy in 2-3 minutes.
echo.
echo Next steps:
echo 1. Wait 3-4 minutes for deployment to complete
echo 2. Go to: https://web-production-fa001.up.railway.app
echo 3. Hard refresh: Ctrl+Shift+R
echo 4. Open Settings tab
echo 5. Check console (F12) for: "Loaded settings from API"
echo.
echo Check deployment status at: https://railway.app
echo.
pause
