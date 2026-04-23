This archive contains the changes to vendor Feather Icons and improve visual QA.

Included files:
- riman_fashion_erp/static/vendor/feather.min.js
- PROFESSIONALIZATION_GUIDE.md
- riman_fashion_erp/scripts/visual_qa.py

How to apply locally (from repository root):

1. Unzip the archive into your repo root (overwriting existing files):
   - PowerShell: Expand-Archive patches\0003-vendor-feather-and-docs.zip -DestinationPath . -Force
   - Or right-click -> Extract All in Explorer

2. Create a branch and commit & push:

   git checkout -b vendor/feather-and-docs
   git add riman_fashion_erp/static/vendor/feather.min.js PROFESSIONALIZATION_GUIDE.md riman_fashion_erp/scripts/visual_qa.py
   git commit -m "chore: vendor feather.min.js, update docs, and improve visual QA vendor check"
   git push -u origin vendor/feather-and-docs

3. Create a PR:
   - If you use GitHub CLI: gh pr create --title "vendor(feather): add official feather.min.js and docs icon updates" --body "Vendors official Feather Icons bundle, replaces Font Awesome examples with Feather in docs, and hardens the visual QA vendor check." --base main
   - Or open the GitHub web UI and create a PR from branch `vendor/feather-and-docs` to `main`.

Notes:
- If `git` or `gh` are not in PATH on your machine, run these commands from Git Bash or a terminal where they are available.
- The Playwright screenshots were saved to `riman_fashion_erp/qa-screenshots/` for your review.
