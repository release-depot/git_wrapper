=====
Usage
=====

To use git_wrapper in a project::

    from git_wrapper.repo import GitRepo


    repo = GitRepo('/path/to/repo')

    repo.branch.rebase_to_hash('my_branch', 'my_commit')

    repo.commit.revert('my_commit')

    repo.remote.names()
