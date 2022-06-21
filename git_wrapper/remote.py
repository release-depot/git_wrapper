#! /usr/bin/env python
"""This module acts as an interface for acting on git remotes"""

import git

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
        working_dir = self.git_repo.repo.working_dir
        self.logger.debug(f"Adding remote {name} ({url}) to repo {working_dir}")
        ret_status = False

        try:
            remote = self.git_repo.repo.create_remote(name, url)
        except git.CommandError as ex:
            self.logger.debug(f"Failed to create new remote {name} ({url}). "
                              f"Error: {ex}")
            return ret_status

        try:
            remote.update()
            ret_status = True
        except git.CommandError as ex:
            self.logger.debug(f"Failed to update new remote {name} ({url}), "
                              f"removing it. Error: {ex}")
            self.git_repo.repo.delete_remote(remote)

        return ret_status

    def fetch(self, remote="origin", prune=False, prune_tags=False):
        """Refresh the specified remote.

           Optionally, specify prune to be True to allow
           for the removal of local branches that don't
           exist on the remote. If you also wish to remove
           local tags that don't exist on the remote, specify
           prune_tags to be True.

           :param str remote: Remote to fetch
           :param bool prune: True if you want to prune
           :param bool prune_tags: True if you want to prune local tags (only works if prune is True)
        """
        try:
            remote = self.git_repo.repo.remote(remote)
        except ValueError:
            repo = self.git_repo.repo.working_dir
            msg = f"Remote {remote} does not exist on repo {repo}"
            raise exceptions.ReferenceNotFoundException(msg)

        try:
            if prune_tags and not prune:
                self.logger.info("prune_tags was ignored because prune is False")
                remote.fetch()
            else:
                remote.fetch(prune=prune, prune_tags=prune_tags)
        except git.GitCommandError as ex:
            msg = (f"Could not fetch remote {remote.name} ({remote.url}). "
                   f"Error: {ex}")
            raise exceptions.RemoteException(msg) from ex

    def fetch_all(self, prune=False, prune_tags=False):
        """Refresh all the repo's remotes.

           All the remotes will be fetched even if one fails ; in this case a
           single exception containing the list of failed remotes is returned.

           Optionally, specify prune to be True to allow
           for the removal of local branches that don't
           exist on the remotes. If you also wish to remove
           local tags that don't exist on the remotes, specify
           prune_tags to be True.

           :param bool prune: True if you want to prune
           :param bool prune_tags: True if you want to prune local tags (only works if prune is True)
        """
        remotes = self.names()

        errors = []
        for remote in remotes:
            try:
                self.fetch(remote, prune, prune_tags)
            except exceptions.RemoteException:
                self.logger.exception(f"Error fetching remote {remote}")
                errors.append(remote)

        if errors:
            msg = f"Error fetching these remotes: {', '.join(errors)}"
            raise exceptions.RemoteException(msg)
