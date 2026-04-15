#!/bin/bash
if [[ -n "${GL_TOKEN:-}" ]]; then
	glab auth login --hostname "$GITLAB_API_HOST" --api-host "$GITLAB_API_HOST" --api-protocol "https" --git-protocol "https" --token "$GL_TOKEN"

	git config --global credential.helper store
	printf 'protocol=https\nhost=%s\nusername=oauth2\npassword=%s\n\n' "$GITLAB_API_HOST" "$GL_TOKEN" | git credential approve

    echo $GL_TOKEN | docker login -u oauth2 --password-stdin "$GITLAB_REGISTRY_HOST"
    echo $GL_TOKEN | docker login -u oauth2 --password-stdin "$GITLAB_INTERNAL_REGISTRY_HOST"
fi

if [[ -n "${HARBOR_TOKEN:-}" ]]; then
    echo $HARBOR_TOKEN | docker login -u "$HARBOR_USERNAME" --password-stdin "$HARBOR_HOST"
fi

exec "$@"