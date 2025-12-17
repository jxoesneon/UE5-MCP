# Security Policy

## Supported Versions

This repository is currently **specification-first**. Until a runnable implementation exists, “supported versions” refers to the documentation/spec set on the default branch.

If/when releases are published, this section will be updated to describe supported release lines and security update timelines.

## Reporting a Vulnerability

Because this project is intended to automate powerful editor-time actions (UE5/Blender), treat it as security-sensitive.

Please **do not** open public issues for vulnerabilities that could enable any of the following:

- remote code execution
- credential or secret exfiltration
- unauthorized remote control of UE/Blender
- destructive automation (project corruption, asset deletion, mass edits)

Preferred reporting path:

1. Use **GitHub Security Advisories** for private disclosure (if enabled on the repository).
2. If advisories are not enabled, contact the maintainers privately via a channel listed in the repository’s About/Contact information.

When reporting, include:

- impact and affected surface (transport, policy, adapter, config)
- reproduction steps (minimal)
- proof-of-concept (if safe to share)
- suggested remediation

## Security Expectations (Design-Level)

Even before code exists, the specification set assumes:

- **policy gating** for destructive actions
- **least privilege** for tokens and environment access
- **local-only defaults** for transport, unless explicitly configured
- **audit artifacts** for every run (inputs, plan, steps, outputs)
