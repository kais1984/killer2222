S3 Storage & Virus Scanning for Document Uploads

Overview
--------
This document explains how to enable remote storage (S3) for uploaded templates and how to enable virus scanning using ClamAV (clamd).

S3 (AWS) Configuration
----------------------
1. Install dependencies:
   - pip install boto3 django-storages
2. Set environment variables (example in .env or your hosting provider):
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_STORAGE_BUCKET_NAME
   - AWS_S3_REGION_NAME (optional)
   - AWS_S3_CUSTOM_DOMAIN (optional)
   - Set DOCUMENTS_USE_S3=True in environment
   - Set DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' in your Django settings
3. Restart your application. Uploaded document files will be stored on S3 automatically using Django's storage abstraction.

Notes:
- When enabling S3, ensure your bucket policy and IAM permissions allow put/get for the application user.
- You can set up lifecycle rules or versioning if you want retention and rollback.

Virus Scanning (ClamAV / clamd)
-------------------------------
1. Install ClamAV on your host (Ubuntu example):
   - sudo apt-get update
   - sudo apt-get install clamav clamav-daemon -y
   - sudo systemctl stop clamav-freshclam
   - sudo freshclam
   - sudo systemctl start clamav-daemon
2. Install Python client:
   - pip install clamd
3. Enable in settings:
   - DOCUMENTS_VIRUS_SCAN=True
4. The system will attempt to use clamd to scan uploaded files. If clamd is not available the scanner will fail-open and uploads will proceed, but you should monitor logs and test scanning in staging when possible.

CI Integration Example
----------------------
We provide a sample GitHub Actions workflow that installs ClamAV and runs a quick scan during CI. This is an optional step to add a security gate in your pipeline.

Caveats and Best Practices
--------------------------
- For production, consider making virus scanning synchronous or asynchronous depending on throughput and SLAs.
- Back up uploaded files and monitor storage costs when using S3.
- Use signed URLs for downloads if you host files on S3 publicly.

Asynchronous Scanning (Celery)
------------------------------
- To offload scanning to workers, use Celery and enable `DOCUMENTS_VIRUS_SCAN=True`.
- Ensure your Celery app is discoverable as `riman_erp.celery.app` (the project already looks for this import).
- The upload flow will enqueue a `scan_uploaded_template` task when Celery is present; without Celery, the system will perform a synchronous scan as a fallback.
- This prevents uploads from being blocked by scan latency in high-throughput environments.
- You can monitor task status via your Celery monitoring tools (Flower, etc.) and implement further actions (quarantine, delete, notify) based on task results.

Contact
-------
If you need help setting up S3 or ClamAV in your environment, reach out and I can assist with a deployment-specific guide.