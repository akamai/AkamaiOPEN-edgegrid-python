FROM python:3-alpine3.19
ENV DEBIAN_FRONTEND=noninteractive

# https://github.com/pyenv/pyenv/wiki#suggested-build-environment
RUN apk add --no-cache git bash build-base libffi-dev openssl-dev bzip2-dev zlib-dev xz-dev readline-dev sqlite-dev tk-dev
RUN apk add --no-cache curl
RUN curl https://pyenv.run | bash
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PATH"
RUN pyenv install 3.9 3.10 3.11 3.12 3.13
RUN echo 'eval "$(pyenv init -)"' >> ~/.profile

RUN pip install --no-cache-dir tox
