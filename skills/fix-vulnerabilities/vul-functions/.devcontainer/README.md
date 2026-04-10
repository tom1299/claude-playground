# Container Setup

## Usage

Start all services:

```bash
DNS_SERVER=10.33.255.21 docker-compose up
```

Rebuild the copilot image without cache:

```bash
DNS_SERVER=10.33.255.21 docker-compose build --no-cache copilot
```

Attach to the copilot container:

```bash
docker exec -it copilot bash
```

## DNS Configuration

DNS is configured in two places:

- **DinD**: Set the `DNS_SERVER` environment variable when running `docker-compose up` (see above). It is passed to the `dind` service via `dind-entrypoint.sh`.
- **BuildKit**: Edit `buildkitd.toml` to change the nameservers used during builds:

  ```toml
  [dns]
    nameservers = ["10.33.255.21"]
  ```

  This file is mounted into the `buildkitd` container at `/etc/buildkit/buildkitd.toml`.

## Test
Run the test script to verify that all services start correctly and that BuildKit can resolve DNS:

```bash
DNS_SERVER=10.33.255.21 ./test.sh
```

## TODO
* Make DNS configuration simpler
* Remove no sandbox option from BuildKit
* BuildKit: seccomp unconfined for privileged ? Which is better