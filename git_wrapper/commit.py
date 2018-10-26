#! /usr/bin/env python
"""This module acts as an interface for common git commit tasks"""

import os

import git
from future.utils import raise_from

from git_wrapper.base import GitWrapperBase
from git_wrapper import exceptions
from git_wrapper.utils.decorators import reference_exists


class GitWrapperCommit(GitWrapperBase):
    """Provides git commit functionality"""

    def _expand_file_path(self, path):
        full_path = os.path.realpath(os.path.expanduser(path))
        if not os.path.isfile(full_path):
            raise exceptions.FileDoesntExistException('{path} is not a file.'.format(path=full_path))
        return full_path

    def commit(self, message, signoff=False):
        """Create a commit for changes to tracked files in the repo.
           Equivalent to `git commit -a -m <message>`.

           :param str message: The commit message
           :param bool signoff: Whether to add signed-off-by to commit message
        """
        if not message or not isinstance(message, str):
            self.logger.debug("Cannot create commit without commit message.")
            raise exceptions.CommitMessageMissingException('No commit message text provided.')

        # Add tracked files to the index
        self.repo.git.add(update=True)
        changes = self.repo.git.diff(name_only=True, staged=True)
        if not changes:
            self.logger.info("No changes to commit.")
            return False

        # Commit the changes
        self.logger.debug("Preparing to commit changes to the following files: %s", changes)
        commit = self.repo.git.commit(message=message, all=True, signoff=signoff)
        self.logger.info("Committed changes as commit %s", commit)

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
            msg = "Could not checkout branch {name}. Error: {error}".format(name=branch_name, error=ex)
            raise_from(exceptions.CheckoutException(msg), ex)

        # Apply the patch file
        try:
            self.repo.git.am(full_path)
        except git.GitCommandError as ex:
            msg = "Could not apply patch {path} on branch {name}. Error: {error}".format(path=full_path, name=branch_name, error=ex)
            raise_from(exceptions.ChangeNotAppliedException(msg), ex)

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
            msg = "Repository {repo} contains uncommitted changes. Please clean workspace before proceeding.".format(repo=self.repo.working_dir)
            raise exceptions.DirtyRepositoryException(msg)

        # Check diff file exists
        full_path = self._expand_file_path(diff_path)

        # Checkout
        try:
            self.repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = "Could not checkout branch {name}. Error: {error}".format(name=branch_name, error=ex)
            raise_from(exceptions.CheckoutException(msg), ex)

        # Apply the diff
        try:
            self.repo.git.apply(full_path)
        except git.GitCommandError as ex:
            msg = "Could not apply diff on branch {name}. Error: {error}".format(name=branch_name, error=ex)
            raise_from(exceptions.ChangeNotAppliedException(msg), ex)

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
            msg = "Revert failed for hash {hash_}. Error: {error}".format(hash_=hash_, error=ex)
            raise_from(exceptions.RevertException(msg), ex)

    def abort(self):
        """Abort applying a patch (git am)."""
        try:
            self.repo.git.am('--abort')
        except git.GitCommandError as ex:
            msg = "Failed to abort git am operation. Error: {0}".format(ex)
            raise_from(exceptions.AbortException(msg), ex)

    def reverse(self, diff_path):
        """Reverse a diff that was applied to the workspace.

           :param str diff_path: Path to the diff file
        """
        full_path = os.path.expanduser(diff_path)
        if not os.path.isfile(full_path):
            raise exceptions.FileDoesntExistException('{path} is not a file.'.format(path=full_path))

        try:
            self.repo.git.apply(full_path, reverse=True)
        except git.GitCommandError as ex:
            msg = "Reversing diff failed. Error: {0}".format(ex)
            raise_from(exceptions.RevertException(msg), ex)
