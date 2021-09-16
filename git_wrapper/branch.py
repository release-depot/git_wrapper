#! /usr/bin/env python
"""This module acts as an interface for acting on git branches"""

import re
import os

import git

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
            msg = f"{full_path} is not a file."
            raise exceptions.FileDoesntExistException(msg)
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

    @reference_exists("start_ref")
    def create(self, name, start_ref, reset_if_exists=False, checkout=False):
        """Create a local branch based on start_ref.

           If the branch exists, do nothing or hard reset it if reset_if_exists
           is set.

           :param str name: New branch's name
           :param str start_ref: Reference (branch, commit, tag, ...) to use as
                                 a starting point.
           :param bool reset_if_exists: Whether to hard reset the branch to
                                        start_ref if the branch already exists.
           :param bool checkout: Whether to checkout the new branch
           :return: True if a new branch was created, None otherwise
        """
        if not self.exists(name):
            self.git_repo.git.branch(name, start_ref)
            if checkout:
                self.git_repo.git.checkout(name)
            return True

        if self.exists(name) and reset_if_exists:
            self.hard_reset_to_ref(name, start_ref, checkout)

        if checkout:
            self.git_repo.git.checkout(name)

    def exists(self, name, remote=None):
        """Checks if a branch exists locally or on the specified remote.

           :param str name: Name of the branch to find
           :param str remote: Remote name to check for the branch, or None
                              if local
        """
        if not remote:
            if name in self.git_repo.repo.branches:
                return True
            else:
                return False
        else:
            if remote not in self.git_repo.remote.names():
                raise exceptions.RemoteException(
                    f"Remote {remote} does not exist."
                )
            if name in self.git_repo.repo.remotes[remote].refs:
                return True
            else:
                return False

    def cherry_on_head_only(self, upstream, head):
        """Get new patches between upstream and head.

           :param str upstream: Branch name
           :param str head: Branch name
        """
        msg = (f"Get new patches between upstream ({upstream}) "
               f"and head ({head})")
        self.logger.debug(msg)
        head_only_regex = re.compile(r'^\+\s(.*?)\s(.*)')
        return self._run_cherry(upstream, head, head_only_regex)

    def cherry_equivalent(self, upstream, head):
        """Get patches that are in both upstream and head.

           :param str upstream: Branch name
           :param str head: Branch name
        """
        msg = (f"Get patches that are in both upstream ({upstream}) "
               f"and head ({head})")
        self.logger.debug(msg)

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
            f"Rebasing branch {branch_name} to hash {hash_}. "
            f"Repo currently at commit {self.git_repo.repo.head.commit}."
        )

        if self.git_repo.repo.is_dirty():
            working_dir = self.git_repo.repo.working_dir
            msg = (f"Repository {working_dir} is dirty. Please clean workspace "
                   "before proceeding.")
            raise exceptions.DirtyRepositoryException(msg)

        # Checkout
        try:
            self.git_repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = f"Could not checkout branch {branch_name}. Error: {ex}"
            raise exceptions.CheckoutException(msg) from ex

        # Rebase
        try:
            self.git_repo.git.rebase(hash_)
        except git.GitCommandError as ex:
            msg = (f"Could not rebase hash {hash_} onto branch {branch_name}. "
                   f"Error: {ex}")
            raise exceptions.RebaseException(msg) from ex

        msg = f"Successfully rebased branch {branch_name} to {hash_}"
        self.logger.debug(msg)

    def abort_rebase(self):
        """Aborts a rebase."""
        try:
            self.git_repo.git.rebase('--abort')
        except git.GitCommandError as ex:
            msg = f"Rebase abort command failed. Error: {ex}"
            raise exceptions.AbortException(msg) from ex

    @reference_exists('branch_name')
    def apply_patch(self, branch_name, path, keep_square_brackets=False):
        """Apply a git patch file on top of the specified branch.

           :param str branch_name: The name of the branch or reference to apply the patch to
           :param str path: Path to a git-formatted patch file (cf. git format-patch)
           :param bool keep_square_brackets: Preserve non-[PATCH] brackets in commit subject
        """
        # Expand file (also needed for git-am) and check it exists
        full_path = self._expand_file_path(path)

        # Checkout
        try:
            self.git_repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = f"Could not checkout branch {branch_name}. Error: {ex}"
            raise exceptions.CheckoutException(msg) from ex

        # Apply the patch file
        try:
            if keep_square_brackets:
                self.git_repo.git.am("--keep-non-patch", full_path)
            else:
                self.git_repo.git.am(full_path)
        except git.GitCommandError as ex:
            msg = (f"Could not apply patch {full_path} on branch "
                   f"{branch_name}. Error: {ex}")
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
        if self.git_repo.repo.is_dirty(untracked_files=True):
            repo = self.git_repo.repo.working_dir
            msg = (f"Repository {repo} contains uncommitted changes. Please "
                   "clean workspace before proceeding.")
            raise exceptions.DirtyRepositoryException(msg)

        # Check diff file exists
        full_path = self._expand_file_path(diff_path)

        # Checkout
        try:
            self.git_repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = f"Could not checkout branch {branch_name}. Error: {ex}"
            raise exceptions.CheckoutException(msg) from ex

        # Apply the diff
        try:
            self.git_repo.git.apply(full_path)
        except git.GitCommandError as ex:
            msg = (f"Could not apply diff {full_path} on branch "
                   f"{branch_name}. Error: {ex}")
            raise exceptions.ChangeNotAppliedException(msg) from ex

        # The diff may have added new files, ensure they are staged
        self.git_repo.git.add(".")

        # Commit
        self.git_repo.commit.commit(message, signoff)

    def abort_patch_apply(self):
        """Abort applying a patch (git am)."""
        try:
            self.git_repo.git.am('--abort')
        except git.GitCommandError as ex:
            msg = f"Failed to abort git am operation. Error: {ex}"
            raise exceptions.AbortException(msg) from ex

    def reverse_diff(self, diff_path):
        """Reverse a diff that was applied to the workspace.

           :param str diff_path: Path to the diff file
        """
        full_path = os.path.expanduser(diff_path)
        if not os.path.isfile(full_path):
            msg = f"{full_path} is not a file."
            raise exceptions.FileDoesntExistException(msg)

        try:
            self.git_repo.git.apply(full_path, reverse=True)
        except git.GitCommandError as ex:
            msg = f"Reversing diff failed. Error: {ex}"
            raise exceptions.RevertException(msg) from ex

    def log_diff(self, hash_from, hash_to, pattern="$full_message"):
        """DEPRECATED. Use GitRepo.log.log_diff instead."""
        self.logger.warning("DEPRECATED. GitRepo.branch.log_diff is deprecated, "
                            "Use GitRepo.log.log_diff instead.")
        return self.git_repo.log.log_diff(hash_from, hash_to, pattern)

    def short_log_diff(self, hash_from, hash_to):
        """DEPRECATED. Use GitRepo.log.short_log_diff instead."""
        self.logger.warning("DEPRECATED. GitRepo.branch.short_log_diff is deprecated, "
                            "Use GitRepo.log.short_log_diff instead.")
        return self.git_repo.log.short_log_diff(hash_from, hash_to)

    def hard_reset(self, branch="master", remote="origin",
                   remote_branch="master", refresh=True):
        """Perform a hard reset of a local branch to a remote branch.

           :param str branch: Local branch to reset
           :param str remote: Remote use as base for the reset
           :param str remote_branch: Remote branch to reset to
           :param bool refresh: Whether to refresh the remote before resetting
        """
        if refresh:
            self.git_repo.remote.fetch(remote)

        remote_ref = f"{remote}/{remote_branch}"
        self.hard_reset_to_ref(branch, remote_ref)

    def hard_reset_to_ref(self, branch, ref, checkout=True):
        """Perform a hard reset of a local branch to any reference.

           :param str branch: Local branch to reset
           :param str ref: Reference (commit, tag, ...) to reset to
           :param bool checkout: Whether to checkout the new branch
        """
        # Ensure the reference maps to a commit
        try:
            commit = git.repo.fun.name_to_object(self.git_repo.repo, ref)
        except git.exc.BadName as ex:
            msg = f"Could not find reference {ref}."
            raise exceptions.ReferenceNotFoundException(msg) from ex

        try:
            # Preserve the reference name if there is one
            orig = self.git_repo.repo.head.ref.name
        except TypeError:
            # Detached head
            orig = self.git_repo.repo.head.commit.hexsha

        # Switch to the branch
        try:
            self.git_repo.git.checkout(branch)
        except git.GitCommandError as ex:
            msg = f"Could not checkout branch {branch}. Error: {ex}"
            raise exceptions.CheckoutException(msg) from ex

        # Reset --hard to that reference
        try:
            self.git_repo.repo.head.reset(commit=commit,
                                          index=True,
                                          working_tree=True)
        except git.GitCommandError as ex:
            msg = (f"Error resetting branch {branch} to {ref}. "
                   f"Error: {ex}")
            raise exceptions.ResetException(msg) from ex

        # Return to the original head if required
        if not checkout:
            try:
                self.git_repo.git.checkout(orig)
            except git.GitCommandError as ex:
                msg = f"Could not checkout {orig}. Error: {ex}"
                raise exceptions.CheckoutException(msg) from ex

    @reference_exists('remote_branch')
    @reference_exists('hash_')
    def remote_contains(self, remote_branch, hash_):
        """Check if a commit hash is present on a remote branch

           :param str remote_branch: Remote branch to check
           :param str hash_: Commit hash to check if present
        """
        # When used with a specific branch name, this command will
        # return either an empty string if the commit isn't present, or
        # the branch name provided
        result = self.git_repo.git.branch(
            "-r", "--contains", hash_, remote_branch
        )
        if result:
            return True
        else:
            return False
