"""Tests for skills/shannon/scripts/install_skill.py (pure filesystem)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
INSTALL = REPO / "skills" / "shannon" / "scripts" / "install_skill.py"


def _load_install():
    spec = importlib.util.spec_from_file_location("install_shannon_skill", INSTALL)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["install_shannon_skill"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def install_mod():
    return _load_install()


class TestInstallSkill:
    def test_source_has_skill_md(self):
        assert (REPO / "skills" / "shannon" / "SKILL.md").is_file()
        assert (REPO / "skills" / "shannon" / "references" / "hosts.md").is_file()

    def test_plugin_manifest_exists(self):
        plugin = REPO / ".claude-plugin" / "plugin.json"
        assert plugin.is_file()
        text = plugin.read_text(encoding="utf-8")
        assert '"name": "shannon"' in text
        assert "cowork" in text.lower()

    def test_candidate_targets_cover_new_hosts(self, install_mod, tmp_path):
        dests = [str(p) for p in install_mod.candidate_targets(REPO, tmp_path)]
        joined = "\n".join(dests)
        for needle in (
            ".cursor/skills/shannon",
            ".codex/skills/shannon",
            ".opencode/skills/shannon",
            ".omp/skills/shannon",
            ".pi/skills/shannon",
            ".github/skills/shannon",
            ".agent/skills/shannon",
            ".omp/agent/skills/shannon",
            ".pi/agent/skills/shannon",
            ".copilot/skills/shannon",
        ):
            assert needle in joined, needle

    def test_dry_run_repo_local(self, install_mod, capsys, tmp_path):
        # dry-run against real repo should report destinations (or already-present)
        rc = install_mod.main(["--dry-run", "--home", str(tmp_path)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "shannon" in out
        assert "dry-run" in out or "skip self" in out or "already present" in out
        assert ".cursor" in out
        assert ".omp" in out

    def test_copy_into_fake_home_hosts(self, install_mod, tmp_path):
        # Pretend user hosts exist
        (tmp_path / ".claude" / "skills").mkdir(parents=True)
        (tmp_path / ".codex" / "skills").mkdir(parents=True)
        (tmp_path / ".grok" / "skills").mkdir(parents=True)
        (tmp_path / ".config" / "opencode").mkdir(parents=True)
        (tmp_path / ".cursor" / "skills").mkdir(parents=True)
        (tmp_path / ".omp" / "agent" / "skills").mkdir(parents=True)
        (tmp_path / ".pi" / "agent" / "skills").mkdir(parents=True)

        rc = install_mod.main(["--home", str(tmp_path)])
        assert rc == 0
        assert (tmp_path / ".claude" / "skills" / "shannon" / "SKILL.md").is_file()
        assert (tmp_path / ".codex" / "skills" / "shannon" / "SKILL.md").is_file()
        assert (tmp_path / ".grok" / "skills" / "shannon" / "SKILL.md").is_file()
        assert (
            tmp_path / ".config" / "opencode" / "skills" / "shannon" / "SKILL.md"
        ).is_file()
        assert (tmp_path / ".cursor" / "skills" / "shannon" / "SKILL.md").is_file()
        assert (
            tmp_path / ".omp" / "agent" / "skills" / "shannon" / "SKILL.md"
        ).is_file()
        assert (tmp_path / ".pi" / "agent" / "skills" / "shannon" / "SKILL.md").is_file()
        hosts = (
            tmp_path / ".omp" / "agent" / "skills" / "shannon" / "references" / "hosts.md"
        )
        assert hosts.is_file()

    def test_force_creates_missing_user_trees(self, install_mod, tmp_path):
        rc = install_mod.main(["--force", "--home", str(tmp_path)])
        assert rc == 0
        assert (tmp_path / ".copilot" / "skills" / "shannon" / "SKILL.md").is_file()
        assert (tmp_path / ".agents" / "skills" / "shannon" / "SKILL.md").is_file()

    def test_omp_vendor_root_is_enough(self, install_mod, tmp_path):
        (tmp_path / ".omp").mkdir()
        rc = install_mod.main(["--home", str(tmp_path)])
        assert rc == 0
        assert (
            tmp_path / ".omp" / "agent" / "skills" / "shannon" / "SKILL.md"
        ).is_file()

    def test_symlink_mode(self, install_mod, tmp_path):
        (tmp_path / ".claude" / "skills").mkdir(parents=True)
        rc = install_mod.main(["--symlink", "--home", str(tmp_path)])
        assert rc == 0
        dest = tmp_path / ".claude" / "skills" / "shannon"
        assert dest.is_symlink() or (dest / "SKILL.md").is_file()
