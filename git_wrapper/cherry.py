#! /usr/bin/env python
'''This module acts as an interface for common git tasks'''

import re

from git_wrapper.base import GitWrapperBase


class GitWrapperCherry(GitWrapperBase):
    '''Provides git cherry functionality'''

    def __init__(self, path='', repo=None):
        '''Constructor for GitWrapperCherry'''
        super(GitWrapperCherry, self).__init__(path=path, repo=repo)
        self._head_only_regex = re.compile(r'^\+\s(.*?)\s(.*)')
        self._equivalent_regex = re.compile(r'^\-\s(.*?)\s(.*)')

    def _run_cherry(self, upstream, head, regex):
        '''Run the git cherry command and return lines in a dict'''
        args = ['-v', upstream, head]
        ret_data = {}
        for line in super(GitWrapperCherry, self).repo.git.cherry(*args).split('\n'):
            match = regex.match(line)
            if match is not None:
                ret_data[match.group(1)] = match.group(2)
        return ret_data

    def on_head_only(self, upstream, head):
        '''Get new patches between upstream and head'''
        return self._run_cherry(upstream, head, self._head_only_regex)

    def equivalent(self, upstream, head):
        ''' Get patches that are in both upstream and head'''
        return self._run_cherry(upstream, head, self._equivalent_regex)
