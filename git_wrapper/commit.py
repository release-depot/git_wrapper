#! /usr/bin/env python
"""This module acts as an interface for acting on git commits"""

import git
from future.utils import raise_from

from git_wrapper import exceptions
from git_wrapper.utils.decorators import reference_exists


class GitCommit(object):

    def __init__(self, git_repo, logger):
        """Constructor for GitCommit object

            :param repo.GitRepo git_repo: An already constructed GitRepo object to use
            :param logging.Logger logger: A pre-configured Python Logger object
        """
        self.git_repo = git_repo
        self.logger = logger

    @reference_exists('sha')
    def describe(self, sha):
        """Return tag and commit info for a given sha

           :param str sha: The SHA1 of the commit to describe
           :return dict: A dict with tag and patch data
        """
        ret_data = {'tag': '', 'patch': ''}
        try:
            output = self.git_repo.git.describe('--all', sha).split('-g')
        except git.CommandError as ex:
            msg = "Error while running describe command on sha {sha}: {error}".format(sha=sha, error=ex)
            raise_from(exceptions.DescribeException(msg), ex)

        if output:
            tag = output[0]
            # Lightweight tags have a tag/ prefix when returned
            if tag.startswith('tag/'):
                tag = tag[4:]
            ret_data['tag'] = tag
            if len(output) > 1:
                ret_data['patch'] = output[1]
        return ret_data

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
        self.git_repo.git.add(update=True)
        changes = self.git_repo.git.diff(name_only=True, staged=True)
        if not changes:
            self.logger.info("No changes to commit.")
            return False

        # Commit the changes
        self.logger.debug("Preparing to commit changes to the following files: %s", changes)
        commit = self.git_repo.git.commit(message=message, all=True, signoff=signoff)
        self.logger.info("Committed changes as commit %s", commit)

    @reference_exists('hash_')
    def revert(self, hash_, message=None):
        """Revert a specified commit.

            :param str hash_: The commit hash or reference to rebase to
            :param str message: Extra info to be included in commit message
        """
        try:
            self.git_repo.git.revert(hash_, no_edit=True)
        except git.GitCommandError as ex:
            msg = "Revert failed for hash {hash_}. Error: {error}".format(
                hash_=hash_, error=ex)
            raise_from(exceptions.RevertException(msg), ex)

        if message:
            commit = git.repo.fun.name_to_object(self.git_repo.repo, hash_)
            self.git_repo.git.commit(
                "--amend",
                "-m", 'Revert "{0}"'.format(commit.summary),
                "-m", "This reverts commit {0}.".format(commit.hexsha),
                "-m", message
            )

    @reference_exists('reference_B')
    @reference_exists('reference_A')
    def same(self, reference_A, reference_B):
        """Determine whether two references refer to the same commit.

            :param str reference_A: A commit ref (sha, tag, branch name, ...)
            :param str reference_B: A commit ref (sha, tag, branch name, ...)
            :return bool: True if the references point to the same commit,
                          False if not
        """
        commitA = git.repo.fun.name_to_object(self.git_repo.repo, reference_A)
        commitB = git.repo.fun.name_to_object(self.git_repo.repo, reference_B)

        if commitA.hexsha == commitB.hexsha:
            return True
        else:
            return False

    @reference_exists('branch_name')
    @reference_exists('sha')
    def cherrypick(self, sha, branch_name):
        """Apply given sha on given branch

           :param str sha: The SHA1 of the commit to cherry-pick
           :param str branch_name: The branch to apply it to
        """
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

        # Cherry-pick
        try:
            self.git_repo.git.cherry_pick(sha)
        except git.GitCommandError as ex:
            msg = "Could not cherry-pick commit {sha} on {name}. Error: {error}".format(name=branch_name, sha=sha, error=ex)
            raise_from(exceptions.ChangeNotAppliedException(msg), ex)

        self.logger.debug("Successfully cherry-picked commit %s on %s", sha, branch_name)

    def abort_cherrypick(self):
        """Aborts a cherrypick."""
        try:
            self.git_repo.git.cherry_pick('--abort')
        except git.GitCommandError as ex:
            msg = "Cherrypick abort command failed. Error: {0}".format(ex)
            raise_from(exceptions.AbortException(msg), ex)
