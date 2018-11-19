#! /usr/bin/env python
"""This module acts as an interface for acting on git branches"""

import re

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

    def _run_cherry(self, upstream, head, regex):
        """Run the git cherry command and return lines in a dict"""
        args = ['-v', upstream, head]
        ret_data = {}
        for line in self.git_repo.git.cherry(*args).split('\n'):
            match = regex.match(line)
            if match is not None:
                ret_data[match.group(1)] = match.group(2)
        return ret_data

    def cherry_on_head_only(self, upstream, head):
        """Get new patches between upstream and head"""
        self.logger.debug("Get new patches between upstream (%s) and head (%s)", upstream, head)
        head_only_regex = re.compile(r'^\+\s(.*?)\s(.*)')
        return self._run_cherry(upstream, head, head_only_regex)

    def cherry_equivalent(self, upstream, head):
        """Get patches that are in both upstream and head"""
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
