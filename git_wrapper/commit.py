#! /usr/bin/env python
"""This module acts as an interface for acting on git commits"""

import git

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
            msg = f"Error while running describe command on sha {sha}: {ex}"
            raise exceptions.DescribeException(msg) from ex

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
        msg = f"Preparing to commit changes to the following files: {changes}"
        self.logger.debug(msg)
        commit = self.git_repo.git.commit(message=message, all=True, signoff=signoff)
        self.logger.info(f"Committed changes as commit {commit}")

    @reference_exists('hash_')
    def revert(self, hash_, message=None):
        """Revert a specified commit.

            :param str hash_: The commit hash or reference to rebase to
            :param str message: Extra info to be included in commit message
        """
        try:
            self.git_repo.git.revert(hash_, no_edit=True)
        except git.GitCommandError as ex:
            msg = f"Revert failed for hash {hash_}. Error: {ex}"
            raise exceptions.RevertException(msg) from ex

        if message:
            commit = git.repo.fun.name_to_object(self.git_repo.repo, hash_)
            self.git_repo.git.commit(
                "--amend",
                "-m", f"Revert '{commit.summary}'",
                "-m", f"This reverts commit {commit.hexsha}.",
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
            working_dir = self.git_repo.repo.working_dir
            msg = (f"Repository {working_dir} is dirty. Please clean "
                   "workspace before proceeding.")
            raise exceptions.DirtyRepositoryException(msg)

        # Checkout
        try:
            self.git_repo.git.checkout(branch_name)
        except git.GitCommandError as ex:
            msg = f"Could not checkout branch {branch_name}. Error: {ex}"
            raise exceptions.CheckoutException(msg) from ex

        # Cherry-pick
        try:
            self.git_repo.git.cherry_pick(sha)
        except git.GitCommandError as ex:
            msg = (f"Could not cherry-pick commit {sha} on {branch_name}. "
                   f"Error: {ex}")
            raise exceptions.ChangeNotAppliedException(msg) from ex

        msg = f"Successfully cherry-picked commit {sha} on {branch_name}"
        self.logger.debug(msg)

    def abort_cherrypick(self):
        """Aborts a cherrypick."""
        try:
            self.git_repo.git.cherry_pick('--abort')
        except git.GitCommandError as ex:
            msg = f"Cherrypick abort command failed. Error: {ex}"
            raise exceptions.AbortException(msg) from ex
