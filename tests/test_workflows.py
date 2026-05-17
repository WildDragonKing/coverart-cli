"""Tests for GitHub Actions workflow configuration changes.

Covers the PR that:
- Removed .coderabbit.yaml
- Removed .github/workflows/auto-enable-automerge.yml
- Modified .github/workflows/dependabot-automerge.yml:
    * Downgraded dependabot/fetch-metadata from @v3 to @v2
    * Removed the "Approve PR" step
"""
from __future__ import annotations

from pathlib import Path

import yaml

# Repo root is two levels above this test file (tests/ -> repo root)
REPO_ROOT = Path(__file__).parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
DEPENDABOT_AUTOMERGE = WORKFLOWS_DIR / "dependabot-automerge.yml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_workflow(path: Path) -> dict:
    """Parse a YAML workflow file and return its contents."""
    return yaml.safe_load(path.read_text())


def _step_names(workflow: dict, job: str) -> list[str]:
    """Return a list of step names for the given job."""
    return [
        step.get("name", "") for step in workflow["jobs"][job]["steps"]
    ]


def _step_by_name(workflow: dict, job: str, name: str) -> dict | None:
    """Return the step dict matching *name*, or None if absent."""
    for step in workflow["jobs"][job]["steps"]:
        if step.get("name") == name:
            return step
    return None


# ---------------------------------------------------------------------------
# Tests: deleted files no longer exist
# ---------------------------------------------------------------------------

class TestDeletedFiles:
    def test_coderabbit_yaml_removed(self) -> None:
        """'.coderabbit.yaml' must have been deleted by this PR."""
        assert not (REPO_ROOT / ".coderabbit.yaml").exists(), (
            ".coderabbit.yaml still exists but should have been deleted"
        )

    def test_auto_enable_automerge_workflow_removed(self) -> None:
        """'auto-enable-automerge.yml' must have been deleted by this PR."""
        assert not (WORKFLOWS_DIR / "auto-enable-automerge.yml").exists(), (
            "auto-enable-automerge.yml still exists but should have been deleted"
        )


# ---------------------------------------------------------------------------
# Tests: dependabot-automerge.yml structure after PR changes
# ---------------------------------------------------------------------------

class TestDependabotAutomergeWorkflow:
    """Structural tests for the modified dependabot-automerge.yml."""

    def setup_method(self) -> None:
        self.wf = _load_workflow(DEPENDABOT_AUTOMERGE)

    def test_workflow_file_exists(self) -> None:
        assert DEPENDABOT_AUTOMERGE.exists()

    # --- fetch-metadata action version ---

    def test_fetch_metadata_action_uses_v2(self) -> None:
        """dependabot/fetch-metadata must be pinned to @v2 (downgraded from @v3)."""
        step = _step_by_name(self.wf, "automerge", "Fetch Dependabot metadata")
        assert step is not None, "Step 'Fetch Dependabot metadata' not found"
        assert step["uses"] == "dependabot/fetch-metadata@v2"

    def test_fetch_metadata_action_not_v3(self) -> None:
        """Regression: @v3 must not be used after the downgrade."""
        step = _step_by_name(self.wf, "automerge", "Fetch Dependabot metadata")
        assert step is not None
        assert step["uses"] != "dependabot/fetch-metadata@v3", (
            "fetch-metadata was downgraded from v3 to v2; v3 must not appear"
        )

    # --- Approve PR step must be gone ---

    def test_approve_pr_step_removed(self) -> None:
        """The 'Approve PR' step must not exist after the PR change."""
        step = _step_by_name(self.wf, "automerge", "Approve PR")
        assert step is None, (
            "'Approve PR' step still present; it should have been removed"
        )

    def test_no_gh_pr_review_approve_command(self) -> None:
        """No step should run 'gh pr review --approve' after the removal."""
        for step in self.wf["jobs"]["automerge"]["steps"]:
            run_cmd = step.get("run", "")
            assert "gh pr review --approve" not in run_cmd, (
                f"Step '{step.get('name')}' still contains 'gh pr review --approve'"
            )

    # --- Auto-merge step must still be present ---

    def test_enable_automerge_step_present(self) -> None:
        """'Enable auto-merge (squash)' step must remain after the PR."""
        step = _step_by_name(self.wf, "automerge", "Enable auto-merge (squash)")
        assert step is not None, "'Enable auto-merge (squash)' step is missing"

    def test_automerge_uses_squash_strategy(self) -> None:
        """The auto-merge command must use the squash strategy."""
        step = _step_by_name(self.wf, "automerge", "Enable auto-merge (squash)")
        assert step is not None
        assert "--squash" in step["run"]

    def test_automerge_uses_auto_flag(self) -> None:
        """The auto-merge command must include --auto."""
        step = _step_by_name(self.wf, "automerge", "Enable auto-merge (squash)")
        assert step is not None
        assert "--auto" in step["run"]

    # --- Job guard: only runs for dependabot[bot] ---

    def test_job_restricted_to_dependabot_actor(self) -> None:
        """The automerge job must only run when the actor is dependabot[bot]."""
        condition = self.wf["jobs"]["automerge"].get("if", "")
        assert "dependabot[bot]" in condition

    # --- Trigger configuration ---
    # Note: PyYAML (YAML 1.1) parses the bare `on:` key as boolean True,
    # so the trigger block is accessed via self.wf[True].

    def test_trigger_is_pull_request_target(self) -> None:
        assert "pull_request_target" in self.wf[True]

    def test_trigger_includes_opened_type(self) -> None:
        types = self.wf[True]["pull_request_target"]["types"]
        assert "opened" in types

    def test_trigger_includes_synchronize_type(self) -> None:
        types = self.wf[True]["pull_request_target"]["types"]
        assert "synchronize" in types

    # --- Permissions ---

    def test_permissions_contents_write(self) -> None:
        assert self.wf["permissions"]["contents"] == "write"

    def test_permissions_pull_requests_write(self) -> None:
        assert self.wf["permissions"]["pull-requests"] == "write"

    # --- Step ordering: fetch-metadata before auto-merge ---

    def test_fetch_metadata_step_before_automerge_step(self) -> None:
        """fetch-metadata must be fetched before the auto-merge command runs."""
        names = _step_names(self.wf, "automerge")
        assert "Fetch Dependabot metadata" in names
        assert "Enable auto-merge (squash)" in names
        assert names.index("Fetch Dependabot metadata") < names.index(
            "Enable auto-merge (squash)"
        )

    # --- Exactly two steps (no leftover approve step) ---

    def test_exactly_two_steps_in_automerge_job(self) -> None:
        """After removing 'Approve PR', the job must have exactly 2 steps."""
        steps = self.wf["jobs"]["automerge"]["steps"]
        assert len(steps) == 2, (
            f"Expected 2 steps after removing 'Approve PR', got {len(steps)}: "
            f"{[s.get('name') for s in steps]}"
        )

    # --- GH_TOKEN used for auto-merge (not any hardcoded value) ---

    def test_automerge_step_uses_github_token(self) -> None:
        step = _step_by_name(self.wf, "automerge", "Enable auto-merge (squash)")
        assert step is not None
        gh_token = step.get("env", {}).get("GH_TOKEN", "")
        assert "secrets.GITHUB_TOKEN" in gh_token

    # --- fetch-metadata step passes github-token ---

    def test_fetch_metadata_step_passes_github_token(self) -> None:
        step = _step_by_name(self.wf, "automerge", "Fetch Dependabot metadata")
        assert step is not None
        token = step.get("with", {}).get("github-token", "")
        assert "secrets.GITHUB_TOKEN" in token
