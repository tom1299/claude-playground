FROM alpine:3.23

RUN apk add --no-cache \
    curl \
    bash \
    ca-certificates \
    github-cli \
    python3-dev \
    py3-pip \
    && ln -sf /usr/bin/python3 /usr/local/bin/python

RUN curl -Lo /usr/local/bin/kubectl https://dl.k8s.io/release/v1.35.0/bin/linux/amd64/kubectl \
    && chmod +x /usr/local/bin/kubectl

ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=1000

RUN addgroup -g ${USER_GID} ${USERNAME} \
    && adduser -D -u ${USER_UID} -G ${USERNAME} ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}

RUN curl -fsSL https://claude.ai/install.sh | bash && \
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc

RUN wget -qO- https://astral.sh/uv/install.sh | sh

RUN mkdir -p /home/${USERNAME}/.kube

ENV KUBECONFIG=/home/${USERNAME}/.kube/config
