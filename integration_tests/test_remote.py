from git_wrapper.repo import GitRepo


def test_prune_tags(repo_root, clone_repo_root):
    repo = GitRepo(repo_root)
    cloned_repo = GitRepo.clone(f"file://{repo_root}", clone_repo_root)

    cloned_repo.tag.create("test_tag", "master")
    assert "test_tag" in cloned_repo.tag.names()

    cloned_repo.tag.push("test_tag", "origin")
    assert "test_tag" in repo.tag.names()

    cloned_repo.git.push("origin", "--delete", "test_tag")
    assert "test_tag" not in repo.tag.names()
    assert "test_tag" in cloned_repo.tag.names()
    cloned_repo.remote.fetch("origin", prune=True, prune_tags=True)
    assert "test_tag" not in cloned_repo.tag.names()


def test_no_prune(repo_root, clone_repo_root):
    repo = GitRepo(repo_root)
    cloned_repo = GitRepo.clone(f"file://{repo_root}", clone_repo_root)

    cloned_repo.tag.create("test_tag", "master")
    assert "test_tag" in cloned_repo.tag.names()

    cloned_repo.tag.push("test_tag", "origin")
    assert "test_tag" in repo.tag.names()

    repo.tag.delete("test_tag")
    assert "test_tag" not in repo.tag.names()

    cloned_repo.remote.fetch("origin")
    assert "test_tag" in cloned_repo.tag.names()


def test_prune_branches(repo_root, clone_repo_root):
    repo = GitRepo(repo_root)
    cloned_repo = GitRepo.clone(f"file://{repo_root}", clone_repo_root)

    cloned_repo.branch.create("test_branch", "master")
    cloned_repo.tag.create("testing_tag", "master")
    assert "test_branch" in [b.name for b in cloned_repo.repo.branches]
    assert "testing_tag" in cloned_repo.tag.names()

    # throughout the test, we'll make sure we never delete test_tag in the cloned repo

    cloned_repo.git.push("origin", "test_branch")
    cloned_repo.git.push("origin", "testing_tag")
    assert "test_branch" in [b.name for b in repo.repo.branches]
    assert "origin/test_branch" in cloned_repo.repo.references

    repo.git.branch("-D", "test_branch")
    repo.tag.delete("testing_tag")
    assert "test_branch" not in [b.name for b in repo.repo.branches]
    assert "testing_tag" not in repo.tag.names()
    assert "origin/test_branch" in cloned_repo.repo.references

    assert "testing_tag" in cloned_repo.tag.names()
    cloned_repo.remote.fetch("origin", prune=True)
    assert "origin/test_branch" not in cloned_repo.repo.references
    assert "testing_tag" in cloned_repo.tag.names()


def test_prune_both(repo_root, clone_repo_root):
    repo = GitRepo(repo_root)
    cloned_repo = GitRepo.clone(f"file://{repo_root}", clone_repo_root)

    cloned_repo.branch.create("test_branch", "master")
    cloned_repo.tag.create("testing_tag", "master")
    assert "test_branch" in [b.name for b in cloned_repo.repo.branches]
    assert "testing_tag" in cloned_repo.tag.names()

    cloned_repo.git.push("origin", "test_branch")
    cloned_repo.git.push("origin", "testing_tag")
    assert "test_branch" in [b.name for b in repo.repo.branches]
    assert "testing_tag" in repo.tag.names()
    assert "origin/test_branch" in cloned_repo.repo.references

    repo.git.branch("-D", "test_branch")
    repo.tag.delete("testing_tag")
    assert "test_branch" not in [b.name for b in repo.repo.branches]
    assert "testing_tag" not in repo.tag.names()
    assert "origin/test_branch" in cloned_repo.repo.references
    assert "testing_tag" in cloned_repo.tag.names()

    cloned_repo.remote.fetch("origin", prune=True, prune_tags=True)
    assert "origin/test_branch" not in cloned_repo.repo.references
    assert "testing_tag" not in cloned_repo.tag.names()
