# Security Policy

## Supported Versions

Floating Assistant is a personal project developed and maintained by a single developer. Only the latest version on the `main` branch receives security fixes.

| Version        | Supported          |
| -------------- | ------------------- |
| Latest (`main`) | ✅ |
| Older commits / releases | ❌ |

## Reporting a Vulnerability

If you find a security issue, please **do not open a public GitHub issue** for it. Instead:

1. Use GitHub's **[private vulnerability reporting](../../security/advisories/new)** feature for this repository (Security tab → "Report a vulnerability"), **or**
2. Open a regular issue titled `[SECURITY] <short description>` **without** including exploit details, and I will follow up to get more information privately.

Please include, if possible:
- A clear description of the issue and its potential impact.
- Steps to reproduce it (proof-of-concept code is welcome).
- The affected file(s)/commit.

You can expect an initial response within a few days. This is a solo-maintained project, so response times may vary — thank you for your patience.

## Scope & Known Risk Areas

Floating Assistant runs with the privileges of the logged-in Windows user and can:

- Toggle Wi-Fi / Bluetooth radios, lock/restart/shutdown/sleep the PC.
- Launch **any executable path the user explicitly adds** through the "Add App" feature.
- Read/write `data/settings.json` in the application folder.

Things that are **in scope** for a security report:
- A way to make the app execute an arbitrary program *without* the user explicitly adding it via the UI.
- Privilege escalation beyond the current user's own permissions.
- Injection via settings/config files that leads to code execution.

Things that are generally **out of scope**:
- The fact that a user can intentionally add and launch their own programs — that's the intended feature, scoped to files the user themselves selects via the file picker.
- Issues that require the attacker to already have full control of the victim's Windows user account.

## Disclosure

Once a reported vulnerability is confirmed and fixed, a note will be added to the project's release notes / changelog crediting the reporter (unless you prefer to remain anonymous).
