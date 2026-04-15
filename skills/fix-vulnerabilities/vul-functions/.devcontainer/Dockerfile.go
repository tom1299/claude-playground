# Dockerfile.go - Extends base image with Go development tooling
# Example build:
# docker build -f Dockerfile.go -t agent.go:latest \
#   --build-arg http_proxy=$http_proxy \
#   --build-arg https_proxy=$https_proxy \
#   --build-arg no_proxy=$no_proxy .
FROM agent.base:latest

ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG USER_NAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=1000
ARG GO_VERSION=1.26.2

ENV DEBIAN_FRONTEND=noninteractive

USER 0

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libc6-dev \
    make \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

ARG GO_CHECKSUM=990e6b4bbba816dc3ee129eaeaf4b42f17c2800b88a2166c265ac1a200262282
RUN curl -fsSL -o /tmp/go.tar.gz "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" \
    && echo "${GO_CHECKSUM}  /tmp/go.tar.gz" | sha256sum -c - \
    && rm -rf /usr/local/go \
    && tar -C /usr/local -xzf /tmp/go.tar.gz \
    && rm /tmp/go.tar.gz

ENV GOROOT=/usr/local/go
ENV GOPATH=/home/${USER_NAME}/go
ENV GOCACHE=/home/${USER_NAME}/.cache/go-build
ENV PATH=/usr/local/go/bin:/home/${USER_NAME}/go/bin:${PATH}

RUN mkdir -p "${GOPATH}" "${GOCACHE}" \
    && chown -R ${USER_UID}:${USER_GID} /home/${USER_NAME}

RUN /usr/local/go/bin/go install golang.org/x/tools/gopls@latest \
    && /usr/local/go/bin/go install github.com/go-delve/delve/cmd/dlv@latest \
    && /usr/local/go/bin/go install gotest.tools/gotestsum@latest \
    && /usr/local/go/bin/go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest \
    && /usr/local/go/bin/go install honnef.co/go/tools/cmd/staticcheck@latest

USER ${USER_NAME}
WORKDIR /workspace

CMD ["sleep", "infinity"]
