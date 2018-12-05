#! /usr/bin/env python
"""This module acts as an interface for acting on git branches"""

import re
import os

import git
from future.utils import raise_from

from git_wrapper import exceptions
from git_wrapper.utils.decorators import reference_exists


class GitBranch(object):

    def __init__(self, git_repo, logger):
        """Constructor for GitBranch object

            :param repo.GitRepo git_repo: An already constructed GitRepo object to use
            :param logging.Logger logger: A pre-configured Python Logger object
        """
        self.git_repo = git_repo
        self.logger = logger

    def _expand_file_path(self, path):
        """Expand a given path into an absolute path and check for presence.

           :param str path: Path
        """
        full_path = os.path.realpath(os.path.expanduser(path))
        if not os.path.isfile(full_path):
            raise exceptions.FileDoesntExistException('{path} is not a file.'.format(path=full_path))
        return full_path

    def _run_cherry(self, upstream, head, regex):
        """Run the git cherry command and return lines in a dict.

           :param str upstream: Branch name
           :param str head: Branch name
           :param str regex: Regular expression to run on the cherry result
        """
        args = ['-v', upstream, head]
        ret_data = {}
        for line in self.git_repo.git.cherry(*args).split('\n'):
            match = regex.match(line)
            if match is not None:
                ret_data[match.group(1)] = match.group(2)
        return ret_data

    def cherry_on_head_only(self, upstream, head):
        """Get new patches between upstream and head.

           :param str upstream: Branch name
           :param str head: Branch name
        """
        self.logger.debug("Get new patches between upstream (%s) and head (%s)", upstream, head)
        head_only_regex = re.compile(r'^\+\s(.*?)\s(.*)')
        return self._run_cherry(upstream, head, head_only_regex)

    def cherry_equivalent(self, upstream, head):
        """Get patches that are in both upstream and head.

           :param str upstream: Branch name
           :param str head: Branch name
        """
        self.logger.debug("Get patches that are in both upstream (%s) and head (%s)", upstream, head)
        equivalent_regex = re.compile(r'^\-\s(.*?)\s(.*)')
        return self._run_cherry(upstream, head, equivalent_regex)

    @reference_exists("branch_name")
    @reference_exists("hash_")
    def rebase_to_hash(self, branch_name, hash_):
        """Perform a rebase from a specific reference to another.

           :param str branch_name: The name of the branch to rebase on
           :param str hash_: The commit hash or reference to rebase to
        """
        self.logger.debug(
            "Rebasing branch %s to hash %s. Repo currently at commit %s.",
            branch_name, hash_, self.git_repo.repo.head.commit
        )

        if self.git_repo.repo.is_dirty():
            msg = ("Repository {0} is dirty. Please clean workspace "
                   "before proceeding.".format(self.git_repo.repo.working_dir))
            raise exceptions.DirtyRepositoryException(msg)

        # Checkout
        try:
            self.git_repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = "Could not checkout branch {name}. Error: {error}".format(name=branch_name, error=ex)
            raise_from(exceptions.CheckoutException(msg), ex)

        # Rebase
        try:
            self.git_repo.git.rebase(hash_)
        except git.GitCommandError as ex:
            msg = "Could not rebase hash {hash_} onto branch {name}. Error: {error}".format(hash_=hash_, name=branch_name, error=ex)
            raise_from(exceptions.RebaseException(msg), ex)

        self.logger.debug("Successfully rebased branch %s to %s", branch_name, hash_)

    def abort_rebase(self):
        """Aborts a rebase."""
        try:
            self.git_repo.git.rebase('--abort')
        except git.GitCommandError as ex:
            msg = "Rebase abort command failed. Error: {0}".format(ex)
            raise_from(exceptions.AbortException(msg), ex)

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
            self.git_repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = "Could not checkout branch {name}. Error: {error}".format(name=branch_name, error=ex)
            raise_from(exceptions.CheckoutException(msg), ex)

        # Apply the patch file
        try:
            self.git_repo.git.am(full_path)
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
        if self.git_repo.repo.is_dirty():
            msg = ("Repository {repo} contains uncommitted changes. Please clean workspace "
                   "before proceeding.".format(repo=self.git_repo.repo.working_dir))
            raise exceptions.DirtyRepositoryException(msg)

        # Check diff file exists
        full_path = self._expand_file_path(diff_path)

        # Checkout
        try:
            self.git_repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = "Could not checkout branch {name}. Error: {error}".format(name=branch_name, error=ex)
            raise_from(exceptions.CheckoutException(msg), ex)

        # Apply the diff
        try:
            self.git_repo.git.apply(full_path)
        except git.GitCommandError as ex:
            msg = "Could not apply diff on branch {name}. Error: {error}".format(name=branch_name, error=ex)
            raise_from(exceptions.ChangeNotAppliedException(msg), ex)

        # Commit
        self.git_repo.commit.commit(message, signoff)

    def abort_patch_apply(self):
        """Abort applying a patch (git am)."""
        try:
            self.git_repo.git.am('--abort')
        except git.GitCommandError as ex:
            msg = "Failed to abort git am operation. Error: {0}".format(ex)
            raise_from(exceptions.AbortException(msg), ex)

    def reverse_diff(self, diff_path):
        """Reverse a diff that was applied to the workspace.

           :param str diff_path: Path to the diff file
        """
        full_path = os.path.expanduser(diff_path)
        if not os.path.isfile(full_path):
            raise exceptions.FileDoesntExistException('{path} is not a file.'.format(path=full_path))

        try:
            self.git_repo.git.apply(full_path, reverse=True)
        except git.GitCommandError as ex:
            msg = "Reversing diff failed. Error: {0}".format(ex)
            raise_from(exceptions.RevertException(msg), ex)
