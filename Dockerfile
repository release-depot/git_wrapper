FROM python:3.6

# Clone an extra copy of the repo, to mess with during the tests
RUN git clone https://github.com/release-depot/git_wrapper /tests/git_wrapper ; git config --global user.name "GitWrapper Integration" ; git config --global user.email "gitwrapper@example.com"

# Copy the current state, to run the tests from
WORKDIR /git_wrapper

COPY . /git_wrapper

RUN pip install -r requirements.txt -r test-requirements.txt
