#! /usr/bin/env python
"""This module acts as an interface for acting on git remotes"""

import git
from future.utils import raise_from

from git_wrapper import exceptions


class GitRemote(object):

    def __init__(self, git_repo, logger):
        """Constructor for GitRemote object

            :param repo.GitRepo git_repo: An already constructed GitRepo object to use
            :param logging.Logger logger: A pre-configured Python Logger object
        """
        self.git_repo = git_repo
        self.logger = logger

    def names(self):
        """Returns a list of remotes for a given repo

            :return list: A list of utf-8 encoded remote names
        """
        return [x.name for x in self.git_repo.repo.remotes]

    def add(self, name, url):
        """Adds a remote to the given repo

            :param str name: The name for the remote
            :param str url: The url to use for the remote
            :return bool: True if the remote was added, False otherwise
        """
        self.logger.debug("Adding remote %s (%s) to repo %s", name, url, self.git_repo.repo.working_dir)
        ret_status = False

        try:
            remote = self.git_repo.repo.create_remote(name, url)
        except git.CommandError as ex:
            self.logger.debug("Failed to create new remote %s (%s). Error: %s", name, url, ex)
            return ret_status

        try:
            remote.update()
            ret_status = True
        except git.CommandError as ex:
            self.logger.debug("Failed to update new remote %s (%s), removing it. Error: %s", name, url, ex)
            self.git_repo.repo.delete_remote(remote)

        return ret_status

    def fetch(self, remote="origin"):
        """Refresh the specified remote

           :param str remote: Remote to fetch
        """
        try:
            remote = self.git_repo.repo.remote(remote)
        except ValueError:
            msg = "Remote {remote} does not exist on repo {repo}".format(
                remote=remote,
                repo=self.git_repo.repo.working_dir
            )
            raise exceptions.ReferenceNotFoundException(msg)

        try:
            remote.fetch()
        except git.GitCommandError as ex:
            msg = (
                "Could not fetch remote {remote} ({url}). "
                "Error: {error}".format(remote=remote.name,
                                        url=remote.url,
                                        error=ex)
            )
            raise_from(exceptions.RemoteException(msg), ex)

    def fetch_all(self):
        """Refresh all the repo's remotes.

           All the remotes will be fetched even if one fails ; in this case a
           single exception containing the list of failed remotes is returned.
        """
        remotes = self.names()

        errors = []
        for remote in remotes:
            try:
                self.fetch(remote)
            except exceptions.RemoteException:
                self.logger.exception("Error fetching remote %s", remote)
                errors.append(remote)

        if errors:
            msg = "Error fetching these remotes: {0}".format(", ".join(errors))
            raise exceptions.RemoteException(msg)
