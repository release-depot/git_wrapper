#! /usr/bin/env python
"""Decorator utilities"""

import inspect

import git
import wrapt

from git_wrapper import exceptions


def reference_exists(ref):
    @wrapt.decorator
    def wrapper(func, instance, args, kwargs):
        all_args = inspect.getcallargs(func, *args, **kwargs)
        try:
            repo = all_args['self'].git_repo.repo
            git.repo.fun.name_to_object(repo, all_args[ref])
        except git.exc.BadName as ex:
            msg = f"Could not find {ref} {all_args[ref]}."
            raise exceptions.ReferenceNotFoundException(msg) from ex
        return func(*args, **kwargs)
    return wrapper
