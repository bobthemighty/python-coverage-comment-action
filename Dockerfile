# See Dockerfile.build for instructions on bumping this.
FROM ewjoachim/python-coverage-comment-action-base:v1
RUN apt install git-lfs

COPY coverage_comment ./coverage_comment
RUN pip install .
