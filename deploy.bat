@echo off
echo ========================================
echo Hi-Tech AI Sales - GitHub Push Script
echo ========================================
echo.

echo Step 1: Initializing Git...
git init

echo.
echo Step 2: Adding files...
git add app frontend requirements.txt Procfile railway.toml runtime.txt DEPLOYMENT.md

echo.
echo Step 3: Committing...
git commit -m "Initial commit - Hi-Tech AI Sales System"

echo.
echo Step 4: Adding remote...
git remote add origin https://github.com/Nerds101001/comments.git

echo.
echo Step 5: Pushing to GitHub...
git branch -M main
git push -u origin main --force

echo.
echo ========================================
echo Done! Check https://github.com/Nerds101001/comments
echo ========================================
echo.
echo Next: Deploy to Railway
echo 1. Go to https://railway.app
echo 2. Sign in with GitHub
echo 3. New Project - Deploy from GitHub
echo 4. Select: Nerds101001/comments
echo 5. Add environment variables
echo 6. Deploy!
echo.
pause
