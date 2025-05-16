#!/usr/bin/env python3
"""
Legion-specific wrapper for libcst's CodemodContext that adds compatibility
with older code that passes 'args' parameter
"""

from libcst.codemod._context import CodemodContext as LibCSTContext


class CodemodContext(LibCSTContext):
    """Wrapper for libcst.codemod.CodemodContext that accepts 'args' parameter for compatibility
    with Legion's codemod scripts.
    """

    def __init__(self, *args, **kwargs):
        # Filter out 'args' if passed to avoid error in parent class
        if "args" in kwargs:
            kwargs.pop("args")
        super().__init__(*args, **kwargs)
