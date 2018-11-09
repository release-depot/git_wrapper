#! /usr/bin/env python
"""This module acts as an interface for git repository management tasks"""

import os
import shutil

import git
from future.utils import raise_from

from git_wrapper.repo import GitRepo
from git_wrapper import exceptions


class GitWrapperClone(GitRepo):
    """Provides git clone functionality"""

    def __init__(self, path='', repo=None, logger=None):
        # If we're cloning for the first time, we may legitimately not
        # have a path or repo to use yet - so don't initialize just yet
        if path or repo:
            super(GitWrapperClone, self).__init__(path=path, repo=repo, logger=logger)
        else:
            self._setup_logger(logger)

    def clone(self, clone_from, clone_to):
        """Clone a repository.

           :param str clone_from: The url or path to clone the repo from
           :param str clone_to: The local path to clone to
           :return git.Repo: Returns the newly created repo object
        """
        clone_to = os.path.realpath(os.path.expanduser(clone_to))
        self.logger.debug("Preparing to clone repository %s into directory %s", clone_from, clone_to)

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

        self.logger.info("Preparing to delete and reclone repo %s", local_path)

        # Get all of the remotes info
        remotes = {}
        for r in self.repo.remotes:
            remotes[r.name] = r.url

        self.logger.debug("Remotes for %s: %s", local_path, ' '.join(list(remotes)))

        if len(remotes) == 0:
            msg = "No remotes found for repo {repo}, cannot reclone. Aborting deletion.".format(repo=local_path)
            raise exceptions.RepoCreationException(msg)

        # Select a remote for the clone, 'origin' by default
        if "origin" in remotes.keys():
            default_remote = "origin"
        else:
            default_remote = list(remotes)[0]

        self.logger.debug("Default remote for cloning set to '%s'", default_remote)

        # Delete the local repo
        self.logger.info("Deleting local repo at %s", local_path)
        shutil.rmtree(local_path, ignore_errors=True)

        # Clone it again
        self.clone(remotes[default_remote], local_path)

        # Recreate the remotes
        for name, url in remotes.items():
            if name != default_remote:
                try:
                    self.logger.debug("Adding remote %s", name)
                    r = self.repo.create_remote(name, url)
                except git.GitCommandError as ex:
                    msg = "Issue with recreating remote {remote}. Error: {error}".format(remote=name, error=ex)
                    raise_from(exceptions.RemoteException(msg), ex)
