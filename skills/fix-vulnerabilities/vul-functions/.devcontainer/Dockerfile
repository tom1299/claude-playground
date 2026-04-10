# Build behind proxy using proxy env vars from host:
# docker build --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy --build-arg no_proxy=$no_proxy .
FROM moby/buildkit:v0.29.0 AS buildkit

FROM ubuntu:24.04

ARG http_proxy
ARG https_proxy
ARG no_proxy

ENV BUILDKIT_HOST=tcp://buildkitd:1234
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    dnsutils \
    git \
    iputils-ping \
    iputils-tracepath \
    jq \
    netcat-openbsd \
    tar \
    telnet \
    traceroute \
    && rm -rf /var/lib/apt/lists/*

ARG GH_VERSION=2.89.0
ARG GH_CHECKSUM=d0422caade520530e76c1c558da47daebaa8e1203d6b7ff10ad7d6faba3490d8
RUN curl -fsSL -o /tmp/gh.tar.gz \
      "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz" \
    && echo "${GH_CHECKSUM}  /tmp/gh.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/gh.tar.gz -C /usr/local --strip-components=1 \
    && rm /tmp/gh.tar.gz

ARG GLAB_VERSION=1.91.0
ARG GLAB_CHECKSUM=31c5dd4b6f5752e4355997b3c4742c9245a7abbb60f39e58bcc4e582843e4869
RUN curl -fsSL -o /tmp/glab.tar.gz \
      "https://gitlab.com/gitlab-org/cli/-/releases/v${GLAB_VERSION}/downloads/glab_${GLAB_VERSION}_linux_amd64.tar.gz" \
    && echo "${GLAB_CHECKSUM}  /tmp/glab.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/glab.tar.gz -C /usr/local/bin --strip-components=1 bin/glab \
    && rm /tmp/glab.tar.gz

ARG YQ_VERSION=v4.52.5
ARG YQ_CHECKSUM=75d893a0d5940d1019cb7cdc60001d9e876623852c31cfc6267047bc31149fa9
RUN curl -fsSL -o /tmp/yq \
      "https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64" \
    && echo "${YQ_CHECKSUM}  /tmp/yq" | sha256sum -c - \
    && install -m 755 /tmp/yq /usr/local/bin/yq \
    && rm /tmp/yq

ARG COPILOT_VERSION=v1.0.21
ARG COPILOT_CHECKSUM=a6fc494a3dd5a76246fb33424baf08abb5b4cb6889fff28cf295155c28b1cf77
RUN curl -fsSL -o /tmp/copilot.tar.gz \
      "https://github.com/github/copilot-cli/releases/download/${COPILOT_VERSION}/copilot-linux-x64.tar.gz" \
    && echo "${COPILOT_CHECKSUM}  /tmp/copilot.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/copilot.tar.gz -C /usr/local/bin \
    && rm /tmp/copilot.tar.gz

ARG DOCKER_VERSION=27.5.1
ARG DOCKER_CHECKSUM=4f798b3ee1e0140eab5bf30b0edc4e84f4cdb53255a429dc3bbae9524845d640
RUN curl -fsSL -o /tmp/docker.tgz \
      "https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz" \
    && echo "${DOCKER_CHECKSUM}  /tmp/docker.tgz" | sha256sum -c - \
    && tar -xzf /tmp/docker.tgz -C /usr/local/bin --strip-components=1 docker/docker \
    && rm /tmp/docker.tgz

COPY --from=buildkit /usr/bin/buildctl /usr/bin/buildctl

RUN groupadd copilot && useradd -g copilot -m -d /home/copilot copilot \
    && mkdir -p /workspace \
    && chown -R copilot:copilot /home/copilot /workspace

USER copilot
WORKDIR /workspace

CMD ["sleep", "infinity"]
