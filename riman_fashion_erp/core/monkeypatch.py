"""Runtime monkeypatches to work around known issues in third-party libraries.

This module applies a safe patch to Django's BaseContext.__copy__ if the
installed Django version uses an implementation that can raise AttributeError
when copying contexts (e.g., using copy(super())). The patch preserves
instance attributes and makes a shallow copy of `dicts` to avoid shared-state
mutations between contexts.
"""
from copy import copy
import inspect


def _patched_basecontext_copy(self):
    """A safe shallow copy implementation for BaseContext."""
    duplicate = self.__class__.__new__(self.__class__)
    # Shallow-copy instance attributes to preserve important attributes
    # like 'template' and 'render_context'.
    duplicate.__dict__ = self.__dict__.copy()
    # Ensure dicts is a shallow copy of the list, not the same object
    duplicate.dicts = self.dicts[:]
    return duplicate


def apply_basecontext_copy_patch():
    """Apply the patch only if the current implementation appears problematic."""
    try:
        from django.template.context import BaseContext
    except Exception:
        # Django not available (e.g., outside Django runtime) - nothing to do
        return

    try:
        src = inspect.getsource(BaseContext.__copy__)
    except Exception:
        src = ""

    # Detect an implementation that uses copy(super()) or otherwise looks suspicious
    # Also patch if the implementation does not preserve instance attributes
    # (i.e., it does not copy __dict__), which can lead to missing attributes
    # such as 'template' on copied Context instances.
    if ("copy(super" in src or "copy(super())" in src) or "__dict__" not in src:
        BaseContext.__copy__ = _patched_basecontext_copy
        return True

    return False
