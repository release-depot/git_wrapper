#! /usr/bin/env python
"""This module acts as an interface for git repository management tasks"""

import logging
import os

import git
from future.utils import raise_from

from git_wrapper.base import GitWrapperBase
from git_wrapper import exceptions


logger = logging.getLogger(__name__)


class GitWrapperClone(GitWrapperBase):
    """Provides git clone functionality"""

    def __init__(self, path='', repo=None):
        # If we're cloning for the first time, we may legitimately not
        # have a path or repo to use yet - so don't initialize just yet
        if path or repo:
            super(GitWrapperClone, self).__init__(path=path, repo=repo)

    def clone(self, clone_from, clone_to):
        """Clone a repository.

           :param str clone_from: The url or path to clone the repo from
           :param str clone_to: The local path to clone to
           :return git.Repo: Returns the newly created repo object
        """
        clone_to = os.path.realpath(os.path.expanduser(clone_to))
        logger.debug("Preparing to clone repository {repo} into directory {dir}".format(repo=clone_from, dir=clone_to))

        try:
            repo = git.repo.base.Repo.clone_from(clone_from, clone_to)
        except git.GitCommandError as ex:
            msg = "Error cloning repository {repo}".format(repo=clone_from)
            raise_from(exceptions.RepoCreationException(msg), ex)

        self.__init__(repo=repo)
        return repo
