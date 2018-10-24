#! /usr/bin/env python
"""This module acts as an interface for common git tasks"""

import logging

import git
from future.utils import raise_from

from git_wrapper.base import GitWrapperBase
from git_wrapper import exceptions
from git_wrapper.utils.decorators import reference_exists


logger = logging.getLogger(__name__)


class GitWrapperRebase(GitWrapperBase):
    """Provides git rebase functionality"""

    @reference_exists("branch_name")
    @reference_exists("hash_")
    def to_hash(self, branch_name, hash_):
        """Perform a rebase from a specific reference to another.

           :param str branch_name: The name of the branch to rebase on
           :param str hash_: The commit hash or reference to rebase to
        """
        logger.debug("Rebasing branch %s to hash %s. Repo currently at commit %s.", branch_name, hash_, self.repo.head.commit)

        if self.repo.is_dirty():
            msg = "Repository {0} is dirty. Please clean workspace before proceeding.".format(self.repo.working_dir)
            raise exceptions.DirtyRepositoryException(msg)

        # Checkout
        try:
            self.repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = "Could not checkout branch {name}. Error: {error}".format(name=branch_name, error=ex)
            raise_from(exceptions.CheckoutException(msg), ex)

        # Rebase
        try:
            self.repo.git.rebase(hash_)
        except git.GitCommandError as ex:
            msg = "Could not rebase hash {hash_} onto branch {name}. Error: {error}".format(hash_=hash_, name=branch_name, error=ex)
            raise_from(exceptions.RebaseException(msg), ex)

        logger.debug("Successfully rebased branch %s to %s", branch_name, hash_)

    def abort(self):
        """Abort a rebase."""
        try:
            self.repo.git.rebase('--abort')
        except git.GitCommandError as ex:
            msg = "Rebase abort command failed. Error: {0}".format(ex)
            raise_from(exceptions.AbortException(msg), ex)
