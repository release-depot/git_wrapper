#! /usr/bin/env python
"""This module acts as an interface for common git tasks"""

import logging

import git

from git_wrapper.base import GitWrapperBase
from git_wrapper import exceptions


logger = logging.getLogger(__name__)


class GitWrapperRebase(GitWrapperBase):
    """Provides git rebase functionality"""

    def __init__(self, path='', repo=None):
        super(GitWrapperRebase, self).__init__(path=path, repo=repo)

    def to_hash(self, branch_name, hash_):
        """Perform a rebase from a specific reference to another.

           :param str branch_name: The name of the branch or reference to start from
           :param str hash_: The commit hash or reference to rebase to
        """
        logger.debug("Rebasing branch %s to hash %s. Repo currently at commit %s.", branch_name, hash_, self.repo.head.commit)

        if self.repo.is_dirty():
            msg = "Repository %s is dirty. Please clean workspace before proceeding." % self.repo.working_dir
            raise exceptions.DirtyRepositoryException(msg)

        # Does the branch exist?
        try:
            branch = git.repo.fun.name_to_object(self.repo, branch_name)
        except git.exc.BadName as ex:
            msg = "Could not find branch %s." % branch_name
            raise exceptions.ReferenceNotFoundException(msg) from ex

        # Does the hash exists?
        try:
            commit = git.repo.fun.name_to_object(self.repo, hash_)
        except git.exc.BadName as ex:
            msg = "Could not find hash %s." % hash_
            raise exceptions.ReferenceNotFoundException(msg) from ex

        # Checkout
        try:
            self.repo.git.checkout(branch.hexsha)
        except git.GitCommandError as ex:
            msg = "Could not checkout branch %s. Error: %s" % (branch_name, ex)
            raise exceptions.CheckoutException(msg) from ex

        # Rebase
        try:
            self.repo.git.rebase(commit.hexsha)
        except git.GitCommandError as ex:
            msg = "Could not rebase hash %s onto branch %s. Error: %s" % (hash_, branch_name, ex)
            raise exceptions.RebaseException(msg) from ex

        logger.debug("Successfully rebased branch %s (%s) to %s" % (branch_name, branch.hexsha, hash_))

    def abort(self):
        """Abort a rebase."""
        try:
            self.repo.git.rebase('--abort')
        except git.GitCommandError as ex:
            msg = "Rebase abort command failed. Error: %s" % (ex)
            raise exceptions.AbortException(msg) from ex
