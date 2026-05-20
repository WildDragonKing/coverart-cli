# Security Policy

## Reporting a vulnerability

If you discover a security issue in `coverart-cli`, please **do not file a public issue**.
Instead, use GitHub's private vulnerability reporting:

- <https://github.com/WildDragonKing/coverart-cli/security/advisories/new>

You will receive an acknowledgement within 7 days. The maintainer keeps no
production deployment, so the realistic scope of a security issue here is
limited to: arbitrary file write under the user's music root, network calls
to unintended hosts, or denial of service via crafted audio files.

## Supported versions

Only the latest minor release is supported with fixes.

## Dependencies

This project pins the minimum version of `mutagen` and otherwise relies on the
Python standard library. Dependency vulnerabilities are tracked via GitHub's
Dependabot.

## Supply chain controls

Security and supply chain integrity are release blockers for this repository.

- Repository Actions default token permissions are read-only. Workflows opt in
  to write or OIDC permissions only at the job that needs them.
- Dependency Review runs on pull requests and fails when new runtime,
  development, or unknown-scope dependencies introduce moderate-or-higher
  vulnerabilities.
- OpenSSF Scorecard runs on `main`, on a weekly schedule, and on demand. Results
  are uploaded to code scanning and published to Scorecard's public API.
- PyPI publishing uses Trusted Publishing with build attestations. Release jobs
  publish only after Release Please creates a GitHub Release/tag and the tagged
  source passes tests.
- Auto-merge requires an explicit `AUTOMERGE_TOKEN` secret. The workflow
  `GITHUB_TOKEN` must not merge PRs because workflow-created events can suppress
  follow-up release workflows.
