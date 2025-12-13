# Fast Docker Builds

## Quick Build Command

For fastest builds with BuildKit cache mounts:

```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose -f infra/docker-compose.yml build [service-name]
```

Or use the helper script:

```bash
./scripts/fast_build.sh [service1] [service2]
```

## Build Times

- **First build**: ~160-400 seconds (downloads all packages)
- **Subsequent builds (no changes)**: ~5 seconds (Docker layer cache)
- **Subsequent builds (requirements.txt changed)**: ~30-60 seconds (pip cache helps)

## What Makes It Fast

1. **BuildKit cache mounts**: Pip packages cached between builds
2. **Docker layer caching**: Unchanged layers reused
3. **Optimized Dockerfile**: Heavy dependencies cached separately

## Examples

```bash
# Build all services
./scripts/fast_build.sh

# Build specific services
./scripts/fast_build.sh decision learner

# Or manually
export DOCKER_BUILDKIT=1 && export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose -f infra/docker-compose.yml build decision learner
```

