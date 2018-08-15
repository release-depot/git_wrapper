#! /usr/bin/env python
"""This module acts as an interface for common git commit tasks"""

import logging

import git

from git_wrapper.base import GitWrapperBase
from git_wrapper import exceptions
from git_wrapper.utils.decorators import reference_exists


logger = logging.getLogger(__name__)


class GitWrapperCommit(GitWrapperBase):
    """Provides git commit functionality"""

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
