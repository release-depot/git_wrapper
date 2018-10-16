#! /usr/bin/env python
"""This module acts as an interface for git repository management tasks"""

import logging
import os
import shutil

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

    def destroy_and_reclone(self):
        """Deletes the current directory and reclone the repository."""
        # Ensure the class was initialised properly
        if not hasattr(self, "repo") or not self.repo:
            raise Exception("No repo given")

        # Get local path for the repo
        local_path = self.repo.working_dir

        logger.info("Preparing to delete and reclone repo {repo}".format(repo=local_path))

        # Get all of the remotes info
        remotes = {}
        for r in self.repo.remotes:
            remotes[r.name] = r.url

        logger.debug("Remotes for {repo}: {remotes}".format(repo=local_path, remotes=' '.join(list(remotes))))

        if len(remotes) == 0:
            msg = "No remotes found for repo {repo}, cannot reclone. Aborting deletion.".format(repo=local_path)
            raise exceptions.RepoCreationException(msg)

        # Select a remote for the clone, 'origin' by default
        if "origin" in remotes.keys():
            default_remote = "origin"
        else:
            default_remote = list(remotes)[0]

        logger.debug("Default remote for cloning set to '{remote}'".format(remote=default_remote))

        # Delete the local repo
        logger.info("Deleting local repo at {path}".format(path=local_path))
        shutil.rmtree(local_path, ignore_errors=True)

        # Clone it again
        self.clone(remotes[default_remote], local_path)

        # Recreate the remotes
        for name, url in remotes.items():
            if name != default_remote:
                try:
                    logger.debug("Adding remote {remote}".format(remote=name))
                    r = self.repo.create_remote(name, url)
                except git.GitCommandError as ex:
                    msg = "Issue with recreating remote {remote}. Error: {error}".format(remote=name, error=ex)
                    raise_from(exceptions.RemoteException(msg), ex)
