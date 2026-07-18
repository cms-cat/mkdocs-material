#!/usr/bin/env python3
"""Resolve the next repository release version from the core package pin."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path


COMPONENT = r"(?:0|[1-9][0-9]*)"
CORE_REQUIREMENT = re.compile(
    rf"^mkdocs[-_]material\s*==\s*({COMPONENT})\.({COMPONENT})\.({COMPONENT})$",
    re.IGNORECASE,
)
CORE_REFERENCE = re.compile(r"^mkdocs[-_]material\b", re.IGNORECASE)
RELEASE_TAG = re.compile(
    rf"^({COMPONENT})\.({COMPONENT})\.({COMPONENT})(?:\.({COMPONENT}))?$"
)

CoreVersion = tuple[int, int, int]
ReleaseVersion = tuple[int, int, int, int]


class VersionResolutionError(ValueError):
    """Raised when release version inputs are invalid or inconsistent."""


def read_core_version(requirements_path: Path) -> CoreVersion:
    """Read the single, exact mkdocs-material pin from a requirements file."""

    requirement_lines = []
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        requirement = line.partition("#")[0].strip()
        if requirement and CORE_REFERENCE.match(requirement):
            requirement_lines.append(requirement)

    if not requirement_lines:
        raise VersionResolutionError(
            f"{requirements_path} does not contain an mkdocs-material pin"
        )
    if len(requirement_lines) > 1:
        raise VersionResolutionError(
            f"{requirements_path} contains multiple mkdocs-material requirements"
        )

    match = CORE_REQUIREMENT.fullmatch(requirement_lines[0])
    if not match:
        raise VersionResolutionError(
            "mkdocs-material must be pinned as mkdocs-material==X.Y.Z"
        )

    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def parse_release_tag(tag: str) -> ReleaseVersion | None:
    """Parse a repository release tag, ignoring unrelated tag formats."""

    match = RELEASE_TAG.fullmatch(tag.strip())
    if not match:
        return None

    major, minor, patch, subpatch = match.groups()
    return int(major), int(minor), int(patch), int(subpatch or 0)


def format_core_version(version: CoreVersion) -> str:
    return ".".join(str(component) for component in version)


def resolve_release_version(
    core_version: CoreVersion, published_tags: Iterable[str]
) -> str:
    """Resolve the next release from the core pin and published stable tags."""

    published_versions = [
        version
        for tag in published_tags
        if (version := parse_release_tag(tag)) is not None
    ]
    formatted_core = format_core_version(core_version)
    if not published_versions:
        return formatted_core

    latest_release = max(published_versions)
    latest_core = latest_release[:3]
    if core_version < latest_core:
        raise VersionResolutionError(
            f"mkdocs-material {formatted_core} is older than the latest published "
            f"release base {format_core_version(latest_core)}"
        )
    if core_version > latest_core:
        return formatted_core

    return f"{formatted_core}.{latest_release[3] + 1}"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--requirements",
        type=Path,
        default=Path("requirements.txt"),
        help="requirements file containing the mkdocs-material pin",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        core_version = read_core_version(args.requirements)
        release_version = resolve_release_version(core_version, sys.stdin)
    except (OSError, VersionResolutionError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"version={release_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
