FROM ubuntu:latest

RUN apt -y update
RUN apt install -y build-essential
RUN apt install -y libgmp3-dev
RUN apt install -y python3
RUN apt install -y git
RUN apt install -y curl
RUN apt install -y zlib1g-dev
RUN apt install -y libssl-dev
RUN apt install -y libffi-dev

RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"

ENV PYTHON_VERSION=3.7.12
RUN pyenv install ${PYTHON_VERSION}
RUN pyenv global ${PYTHON_VERSION}

RUN pip3 install ecdsa fastecdsa sympy