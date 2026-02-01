import io
import logging
import zipfile
from django.conf import settings

logger = logging.getLogger(__name__)

def detect_file_type(file_obj):
    """Return a guessed file extension from file content (pdf, docx, xlsx, html, txt, other).
    Reads initial bytes without consuming the stream for later use.
    """
    try:
        pos = None
        if hasattr(file_obj, 'tell') and hasattr(file_obj, 'seek'):
            pos = file_obj.tell()
            file_obj.seek(0)

        head = file_obj.read(8192)
        if isinstance(head, str):
            head_bytes = head.encode('utf-8', errors='ignore')
        else:
            head_bytes = head or b''

        # PDF
        if head_bytes.startswith(b'%PDF'):
            return 'pdf'

        # ZIP-based formats: docx, xlsx, pptx
        if head_bytes.startswith(b'PK'):
            # Try to open as zip and look for specific directories
            try:
                # Ensure we operate on a bytes buffer
                if not isinstance(file_obj, (io.BytesIO,)):
                    # Read full content safely
                    file_obj.seek(0)
                    data = file_obj.read()
                    zf = zipfile.ZipFile(io.BytesIO(data))
                else:
                    file_obj.seek(0)
                    zf = zipfile.ZipFile(file_obj)

                names = zf.namelist()
                if any(n.startswith('word/') for n in names):
                    return 'docx'
                if any(n.startswith('xl/') for n in names):
                    return 'xlsx'
                if any(n.startswith('ppt/') for n in names):
                    return 'pptx'
            except Exception:
                pass

        # HTML
        low = head_bytes.lower()
        if low.lstrip().startswith(b'<!doctype html') or b'<html' in low[:2000]:
            return 'html'

        # Text heuristic: mostly printable ASCII
        if len(head_bytes) > 0:
            printable = sum(1 for b in head_bytes if 32 <= b <= 126 or b in (9,10,13))
            if printable / max(1, len(head_bytes)) > 0.9:
                return 'txt'

        return 'other'
    finally:
        if hasattr(file_obj, 'seek') and pos is not None:
            try:
                file_obj.seek(pos)
            except Exception:
                pass


def scan_file(file_obj):
    """Optional virus scanning hook. Returns (True, None) when clean, (False, reason) when infected or scanner error.
    Attempts to use "clamd" if available. If DOCUMENTS_VIRUS_SCAN is False, this is a no-op that returns clean.
    """
    if not getattr(settings, 'DOCUMENTS_VIRUS_SCAN', False):
        return True, None

    try:
        import clamd
        cd = clamd.ClamdNetworkSocket()
        # Ensure pointer at start
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        data = file_obj.read()
        result = cd.instream(io.BytesIO(data))
        # result example: {'stream': ('OK', None)} or {'stream': ('FOUND', 'Eicar-Test-Signature')}
        for k, v in result.items():
            status, reason = v
            if status == 'OK':
                return True, None
            else:
                return False, reason
    except Exception as e:
        logger.warning('Virus scanning not available or failed: %s', e)
        # Fail-open: treat as clean when scanner is unavailable
        return True, None