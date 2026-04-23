@echo off
setlocal enabledelayedexpansion

echo.
echo ======================================================
echo  Finishing PR: Vendor Feather Icons & Update Docs
echo ======================================================
echo.

cd /d C:\Users\KAIS\Documents\RIAMAN_FASHION_ERP
if errorlevel 1 (
    echo ERROR: Failed to change directory
    exit /b 1
)

echo Step 1: Checking if patch is already extracted...
if exist "riman_fashion_erp\static\vendor\feather.min.js" (
    echo   ✓ Feather bundle already extracted
) else (
    echo Step 1: Extracting patch...
    powershell -Command "Expand-Archive patches\0003-vendor-feather-and-docs.zip -DestinationPath . -Force"
    if errorlevel 1 (
        echo ERROR: Failed to extract patch
        exit /b 1
    )
    echo   ✓ Patch extracted successfully
)

echo.
echo Step 2: Creating git branch...
cd riman_fashion_erp
git checkout -b vendor/feather-and-docs
if errorlevel 1 (
    echo   (Branch may already exist, attempting checkout)
    git checkout vendor/feather-and-docs
    if errorlevel 1 (
        echo ERROR: Failed to checkout branch
        cd ..
        exit /b 1
    )
)
echo   ✓ Branch created/checked out

echo.
echo Step 3: Staging files...
git add static\vendor\feather.min.js ..\PROFESSIONALIZATION_GUIDE.md scripts\visual_qa.py
if errorlevel 1 (
    echo ERROR: Failed to stage files
    cd ..
    exit /b 1
)
echo   ✓ Files staged

echo.
echo Step 4: Committing changes...
git commit -m "chore: vendor feather.min.js, update docs, and improve visual QA vendor check"
if errorlevel 1 (
    echo ERROR: Failed to commit
    cd ..
    exit /b 1
)
echo   ✓ Changes committed

echo.
echo Step 5: Pushing to origin...
git push -u origin vendor/feather-and-docs
if errorlevel 1 (
    echo ERROR: Failed to push
    echo   (Check credentials and network access)
    cd ..
    exit /b 1
)
echo   ✓ Pushed to origin

echo.
echo Step 6: Creating PR (if gh CLI available)...
gh pr create --title "vendor(feather): add official feather.min.js and docs icon updates" --body "Vendors the official Feather Icons bundle, replaces Font Awesome examples with Feather in documentation, and improves the visual QA vendor check." --base main
if errorlevel 1 (
    echo   (GitHub CLI not available or PR creation failed)
    echo   You can create the PR manually at: https://github.com/your-org/your-repo/compare/main...vendor/feather-and-docs
)

cd ..
echo.
echo ======================================================
echo  ✓ All steps completed!
echo ======================================================
echo.
pause
