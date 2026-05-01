# SPDX-License-Identifier: PSF-2.0

import os
import sys
import unittest

is_wasi = sys.platform == "wasi"


def skip_if_unlimited_stack_size(test):
    """Skip decorator for tests not run when an unlimited stack size is configured.

    Tests using support.infinite_recursion([...]) may otherwise run into
    an infinite loop, running until the memory on the system is filled and
    crashing due to OOM.

    See https://github.com/python/cpython/issues/143460.
    """
    if is_wasi or os.name == "nt":
        return test

    import resource

    curlim, maxlim = resource.getrlimit(resource.RLIMIT_STACK)
    unlimited_stack_size_cond = curlim == maxlim and curlim in (
        -1,
        0xFFFF_FFFF_FFFF_FFFF,
    )
    reason = "Not run due to unlimited stack size"
    return unittest.skipIf(unlimited_stack_size_cond, reason)(test)
