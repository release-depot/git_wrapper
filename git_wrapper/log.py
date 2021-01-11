#! /usr/bin/env python
"""This module acts as an interface for acting on git logs"""

from string import Template

from git_wrapper import exceptions
from git_wrapper.utils.decorators import reference_exists


class GitLog(object):

    def __init__(self, git_repo, logger):
        """Constructor for GitLog object

            :param repo.GitRepo git_repo: An already constructed GitRepo object
            :param logging.Logger logger: A pre-configured Python Logger object
        """
        self.git_repo = git_repo
        self.logger = logger

    @reference_exists('hash_from')
    @reference_exists('hash_to')
    def log_diff(self, hash_from, hash_to, pattern="$full_message"):
        """Return a list of strings for log entries between two hashes.

           Any of the following placeholders may be used in the pattern:
             * $hash The full commit hash
             * $short_hash The short commit hash, similar to --abbrev-commit
             * $message The commit message
             * $summary First line of the commit message
             * $full_message Complete commit info with hash, author, message.
               Similar to default "git log" ouput
             * $author Commit author
             * $date Date the commit was authored

           :param str hash_from: A commit hash
           :param str hash_to: A commit hash
           :param str pattern: Formatter containing any of the placeholders above
        """
        range_ = "{0}..{1}".format(hash_from, hash_to)
        commits = self.git_repo.repo.iter_commits(range_)
        if not commits:
            return []

        # Prepare patterns
        author_tpl = Template("$name <$email>")
        full_message_tpl = Template(
            "commit $hash\nAuthor: $author\nDate: $date\n\n$message"
        )

        # Parse the user-provided pattern
        log = []
        line_tpl = Template(pattern)
        for c in commits:
            c_author = author_tpl.safe_substitute(name=c.author.name,
                                                  email=c.author.email)
            c_date = c.authored_datetime.strftime("%a %b %d %H:%M:%S %Y %z")

            placeholders = {"short_hash": c.hexsha[0:7],
                            "hash": c.hexsha,
                            "message": c.message,
                            "summary": c.summary,
                            "author": c_author,
                            "date": c_date}

            full_message = full_message_tpl.safe_substitute(placeholders)
            placeholders["full_message"] = full_message

            line = line_tpl.safe_substitute(placeholders)
            log.append(line)

        return log

    def short_log_diff(self, hash_from, hash_to):
        """Return a list of strings for log entries between two hashes.

           Log entries will be returned in the "<short_hash> <summary>" format.

           :param str hash_from: A commit hash
           :param str hash_to: A commit hash
        """
        return self.log_diff(hash_from, hash_to, "$short_hash $summary")

    @reference_exists('branch')
    def grep_for_commits(self, branch, grep_for, reverse=False, path=None):
        """Returns a list of matching commits shas.
           :param str branch: which branch to grep on
           :param str grep_for: what to grep for
           :param bool reverse: whether to return in reversed order
           :param str path: path to limit the search to, optionally
           :return: A list of commit ids
        """
        commits = []

        params = [branch, "--format=format:%H", "--grep=%s" % grep_for]
        if reverse:
            params += ['--reverse']
        if path:
            if path not in self.git_repo.repo.tree():
                raise exceptions.FileDoesntExistException("Path %s doesn't exist in repo." % path)
            params += [path]

        results = self.git_repo.repo.git.log(*params)

        # git.log returns an empty string if there are no matching commits, don't split in that case
        if len(results) > 0:
            commits = results.split("\n")

        return commits
