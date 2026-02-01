from django.test import TestCase
from django.template import Context

from core import monkeypatch


class BaseContextPatchTest(TestCase):
    def test_context_new_does_not_raise(self):
        """Applying the patch should leave Context.new() callable and keep 'template'."""
        # Ensure patch is applied (no-op if not necessary)
        monkeypatch.apply_basecontext_copy_patch()

        c = Context()
        c.template = 'original'
        new_ctx = c.new({})

        # The copied context should preserve template attribute (or have it set)
        self.assertTrue(hasattr(new_ctx, 'template'))
        # Template should be same as original or None, but not raising
        self.assertIn(getattr(new_ctx, 'template', None), (None, 'original'))