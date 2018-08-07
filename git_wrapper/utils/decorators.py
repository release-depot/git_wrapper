#! /usr/bin/env python
"""Decorator utilities"""

import functools
import inspect

import git

from git_wrapper import exceptions


def reference_exists(ref):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            all_args = sig.bind(*args, **kwargs).arguments
            try:
                git.repo.fun.name_to_object(all_args['self'].repo, all_args[ref])
            except git.exc.BadName as ex:
                msg = "Could not find %s %s." % (ref, all_args[ref])
                raise exceptions.ReferenceNotFoundException(msg) from ex
            return func(*args, **kwargs)
        return wrapper
    return decorator
