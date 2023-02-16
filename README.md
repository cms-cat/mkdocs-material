# mkdocs-material

[![Publish Image](https://github.com/cms-cat/mkdocs-material/actions/workflows/publish-docker.yml/badge.svg)](https://github.com/cms-cat/mkdocs-material/actions/workflows/publish-docker.yml)

Wrapper project to build `linux/amd64`, `linux/arm64` and `linux/arm/v7` Docker images of [mkdocs-material](https://github.com/squidfunk/mkdocs-material).

Please refer to the official [Material for MkDocs documentation](https://squidfunk.github.io/mkdocs-material/getting-started/?h=arm64#with-docker) for further information.

## Usage

The image can be pulled via:

```bash
docker pull ghcr.io/cms-cat/mkdocs-material:latest
```

From an existing MkDocs installation directory:

```bash
docker run --rm -it -p 8000:8000 -v $PWD:/docs ghcr.io/cms-cat/mkdocs-material:latest
```
