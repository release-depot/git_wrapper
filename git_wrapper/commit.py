#! /usr/bin/env python
"""This module acts as an interface for common git commit tasks"""

import logging
import os

import git

from git_wrapper.base import GitWrapperBase
from git_wrapper import exceptions
from git_wrapper.utils.decorators import reference_exists


logger = logging.getLogger(__name__)


class GitWrapperCommit(GitWrapperBase):
    """Provides git commit functionality"""

    def _expand_file_path(self, path):
        full_path = os.path.realpath(os.path.expanduser(path))
        if not os.path.isfile(full_path):
            raise exceptions.FileDoesntExistException('%s is not a file.' % full_path)
        return full_path

    def commit(self, message, signoff=False):
        """Create a commit for changes to tracked files in the repo.
           Equivalent to `git commit -a -m <message>`.

           :param str message: The commit message
           :param bool signoff: Whether to add signed-off-by to commit message
        """
        if not message or not isinstance(message, str):
            logger.debug("Cannot create commit without commit message.")
            raise exceptions.CommitMessageMissingException('No commit message text provided.')

        # Add tracked files to the index
        self.repo.git.add(update=True)
        changes = self.repo.git.diff(name_only=True, staged=True)
        if not changes:
            logger.info("No changes to commit.")
            return False

        # Commit the changes
        logger.debug("Preparing to commit changes to the following files: %s" % changes)
        commit = self.repo.git.commit(message=message, all=True, signoff=signoff)
        logger.info("Committed changes as commit %s" % commit)

    @reference_exists('branch_name')
    def apply_patch(self, branch_name, path):
        """Apply a git patch file on top of the specified branch.

           :param str branch_name: The name of the branch or reference to apply the patch to
           :param str path: Path to a git-formatted patch file (cf. git format-patch)
        """
        # Expand file (also needed for git-am) and check it exists
        full_path = self._expand_file_path(path)

        # Checkout
        try:
            self.repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = "Could not checkout branch %s. Error: %s" % (branch_name, ex)
            raise exceptions.CheckoutException(msg) from ex

        # Apply the patch file
        try:
            self.repo.git.am(full_path)
        except git.GitCommandError as ex:
            msg = "Could not apply patch %s on branch %s. Error: %s" % (path, branch_name, ex)
            raise exceptions.ChangeNotAppliedException(msg) from ex

    @reference_exists('branch_name')
    def apply_diff(self, branch_name, diff_path, message, signoff=False):
        """Apply a diff on top of the specified branch.

           :param str branch_name: The name of the branch or reference to apply the diff to
           :param str diff_path: Path to the diff file
           :param str message: Commit message
           :param bool signoff: Whether to add signed-off-by to commit message
        """
        # Ensure we don't commit more than we mean to
        if self.repo.is_dirty():
            msg = "Repository %s contains uncommitted changes. Please clean workspace before proceeding." % self.repo.working_dir
            raise exceptions.DirtyRepositoryException(msg)

        # Check diff file exists
        full_path = self._expand_file_path(diff_path)

        # Checkout
        try:
            self.repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = "Could not checkout branch %s. Error: %s" % (branch_name, ex)
            raise exceptions.CheckoutException(msg) from ex

        # Apply the diff
        try:
            self.repo.git.apply(full_path)
        except git.GitCommandError as ex:
            msg = "Could not apply diff on branch %s. Error: %s" % (branch_name, ex)
            raise exceptions.ChangeNotAppliedException(msg) from ex

        # Commit
        self.commit(message, signoff)

    @reference_exists('hash_')
    def revert(self, hash_):
        """Revert a specified commit.

            :param str hash_: The commit hash or reference to rebase to
        """
        try:
            self.repo.git.revert(hash_, no_edit=True)
        except git.GitCommandError as ex:
            msg = "Revert failed for hash %s. Error: %s" % (hash_, ex)
            raise exceptions.RevertException(msg) from ex

    def abort(self):
        """Abort applying a patch (git am)."""
        try:
            self.repo.git.am('--abort')
        except git.GitCommandError as ex:
            msg = "Failed to abort git am operation. Error: %s" % ex
            raise exceptions.AbortException(msg) from ex

    def reverse(self, diff_path):
        """Reverse a diff that was applied to the workspace.

           :param str diff_path: Path to the diff file
        """
        full_path = os.path.expanduser(diff_path)
        if not os.path.isfile(full_path):
            raise exceptions.FileDoesntExistException('%s is not a file.' % full_path)

        try:
            self.repo.git.apply(full_path, reverse=True)
        except git.GitCommandError as ex:
            msg = "Reversing diff failed. Error: %s" % ex
            raise exceptions.RevertException(msg) from ex
