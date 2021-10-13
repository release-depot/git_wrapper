## git\_wrapper

[![pypi](https://img.shields.io/pypi/v/git_wrapper.svg)](https://pypi.python.org/pypi/git_wrapper)
[![tests](https://github.com/release-depot/git_wrapper/actions/workflows/test.yml/badge.svg)](https://github.com/release-depot/git_wrapper/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/git-wrapper/badge/?version=latest)](https://git-wrapper.readthedocs.io/en/latest/?badge=latest)

Python wrapper around GitPython

-   Free software: MIT license

## Notes

This library only supports python 3. Some features may still work with
python 2.7 but not all of the syntax and features may be compatible.

## Development

git\_wrapper supports both standard python virtual environment setups
and pipenv, which is integrated into our Makefile. To set up a
pipenv-based development enironment, you can simply run:

    make dev

This will install our dev environment for the package via pipenv. It is
installed with \--user, so it does not affect your site-packages. Pipenv
creates a unique virtualenv for us, which you can activate via:

    pipenv shell

See the [pipenv documentation](https://docs.pipenv.org/) for more
detail.

#### Documentation

To build the documentation on your checkout, simply run:

    make docs

#### Building

If you wish to build a local package for testing at any time, you can
simply run:

    make dist

this will build a package with a .dev extension that you can install for
testing and verification.

## Contributions

All new code should include tests that exercise the code and prove that
it works, or fixes the bug you are trying to fix. Any Pull Request
without tests will not be accepted. See CONTRIBUTING.rst for more
details.

#### Pushing a new release

1.  Tag the commit that will be the new release and push the new tag to
    the repo.
2.  Github Actions will then automatically build and publish a new
    release with updated documentation.
