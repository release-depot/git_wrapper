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
    def revert(self, hash_):
        """Revert a specified commit.

            :param str hash_: The commit hash or reference to rebase to
        """
        try:
            self.git_repo.git.revert(hash_, no_edit=True)
        except git.GitCommandError as ex:
            msg = "Revert failed for hash {hash_}. Error: {error}".format(hash_=hash_, error=ex)
            raise_from(exceptions.RevertException(msg), ex)
