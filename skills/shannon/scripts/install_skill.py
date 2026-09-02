#!/usr/bin/env python3
"""Install the Shannon skill into host agent skill directories.

Copies (or symlinks) skills/shannon → Claude / Codex / Grok / OpenCode /
Cursor / Oh-My-Pi / Pi / Copilot / agents trees so TUIs and remote control
planes load the same handrail.

Usage
-----
  python3 skills/shannon/scripts/install_skill.py
  python3 skills/shannon/scripts/install_skill.py --symlink
  python3 skills/shannon/scripts/install_skill.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


# Project-local trees (always written). T1/T3 Code discover Claude/Codex/
# Cursor/Grok/OpenCode/.agents skills rather than a vendor-specific dir.
PROJECT_RELATIVE: tuple[tuple[str, ...], ...] = (
    (".claude", "skills", "shannon"),
    (".grok", "skills", "shannon"),
    (".agents", "skills", "shannon"),
    (".agent", "skills", "shannon"),
    (".cursor", "skills", "shannon"),
    (".codex", "skills", "shannon"),
    (".opencode", "skills", "shannon"),
    (".omp", "skills", "shannon"),
    (".pi", "skills", "shannon"),
    (".github", "skills", "shannon"),
)

# User-level trees (written when the host config already exists, or --force).
USER_RELATIVE: tuple[tuple[str, ...], ...] = (
    (".claude", "skills", "shannon"),
    (".codex", "skills", "shannon"),
    (".grok", "skills", "shannon"),
    (".cursor", "skills", "shannon"),
    (".agents", "skills", "shannon"),
    (".agent", "skills", "shannon"),
    (".config", "opencode", "skills", "shannon"),
    (".opencode", "skills", "shannon"),
    (".omp", "agent", "skills", "shannon"),
    (".pi", "agent", "skills", "shannon"),
    (".copilot", "skills", "shannon"),
)


def repo_root() -> Path:
    # skills/shannon/scripts/thisfile → repo
    return Path(__file__).resolve().parents[3]


def skill_source(root: Path) -> Path:
    return root / "skills" / "shannon"


def candidate_targets(root: Path, home: Path) -> list[Path]:
    """Ordered install destinations (project first, then user hosts)."""
    paths = [root.joinpath(*parts) for parts in PROJECT_RELATIVE]
    paths.extend(home.joinpath(*parts) for parts in USER_RELATIVE)
    # Sibling FlexAIDdS when present
    flex = home / "Projects" / "FlexAIDdS"
    if flex.is_dir():
        paths.append(flex / ".agents" / "skills" / "shannon")
        paths.append(flex / ".claude" / "skills" / "shannon")
        paths.append(flex / ".grok" / "skills" / "shannon")
        paths.append(flex / ".cursor" / "skills" / "shannon")
        paths.append(flex / ".omp" / "skills" / "shannon")
    return paths


def _is_under(path: Path, root: Path) -> bool:
    try:
        return path.is_relative_to(root)
    except AttributeError:
        return os.path.commonpath([str(path), str(root)]) == str(root)
    except ValueError:
        return False


def should_install(path: Path, root: Path, *, force_user: bool) -> bool:
    """Write project-local trees always; user hosts only when already present."""
    if _is_under(path, root):
        return True
    if force_user:
        return True
    if path.parent.exists() or path.parent.parent.exists():
        return True
    # ~/.omp or ~/.pi is enough to create agent/skills underneath.
    vendor_roots = {
        ".claude",
        ".codex",
        ".grok",
        ".cursor",
        ".agents",
        ".agent",
        ".opencode",
        ".omp",
        ".pi",
        ".copilot",
    }
    for ancestor in list(path.parents)[:6]:
        if ancestor.name in vendor_roots and ancestor.exists():
            return True
        if (
            ancestor.name == "opencode"
            and ancestor.parent.name == ".config"
            and ancestor.exists()
        ):
            return True
    return False


def install_one(
    src: Path,
    dest: Path,
    *,
    symlink: bool,
    dry_run: bool,
) -> str:
    # Dry-run always reports the planned destination first (even if already linked).
    if dry_run:
        try:
            same = dest.exists() and dest.resolve() == src.resolve()
        except OSError:
            same = False
        if same:
            return f"dry-run (already present) → {dest}"
        return f"dry-run → {dest}"
    if dest.exists() or dest.is_symlink():
        try:
            if dest.resolve() == src.resolve():
                return f"skip self {dest}"
        except OSError:
            pass
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        if dest.is_symlink() or dest.is_file():
            dest.unlink()
        else:
            shutil.rmtree(dest)
    if symlink:
        dest.symlink_to(src, target_is_directory=True)
        return f"symlink {dest} → {src}"
    shutil.copytree(src, dest)
    return f"copy → {dest}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Install Shannon skill into agent hosts")
    ap.add_argument("--symlink", action="store_true", help="symlink instead of copy")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="create host trees if missing")
    ap.add_argument("--home", default=str(Path.home()), help="override home (tests)")
    args = ap.parse_args(argv)

    root = repo_root()
    src = skill_source(root)
    if not (src / "SKILL.md").is_file():
        print(f"missing skill source: {src}", file=sys.stderr)
        return 1

    home = Path(args.home).expanduser()
    results = []
    for dest in candidate_targets(root, home):
        if not should_install(dest, root, force_user=args.force):
            results.append(f"skip (no host tree): {dest}")
            continue
        msg = install_one(src, dest, symlink=args.symlink, dry_run=args.dry_run)
        results.append(msg)

    for line in results:
        print(line)
    # Success if we installed, dry-ran, or confirmed already-present (skip self).
    ok = any(
        line.startswith(("copy", "symlink", "dry-run", "skip self"))
        for line in results
    )
    return 0 if ok else 1


if __name__ == "__main__":
    # Python 3.9 compat: is_relative_to may be missing — handled above.
    raise SystemExit(main())
