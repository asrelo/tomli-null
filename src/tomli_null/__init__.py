# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Taneli Hukkinen

__all__ = ("loads", "load", "TOMLDecodeError")
__version__ = "0.1.0"  # DO NOT EDIT THIS LINE MANUALLY. LET bump2version UTILITY DO IT

from ._parser import TOMLDecodeError, load, loads

# Pretend this exception was created here.
TOMLDecodeError.__module__ = __name__
