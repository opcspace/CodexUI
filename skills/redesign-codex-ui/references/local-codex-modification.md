# Local Codex Modification

Classify the target before editing. Do not assume that “local Codex” is a writable source project.

## Mode A: source checkout

Use this mode when the target contains application source, package scripts, and editable UI entry points.

1. Read repository instructions and inspect worktree status.
2. Run `audit_codex_ui.py` from the target root.
3. Export the selected preset with `export_theme_bundle.py`, map it into the existing token system, or create `.codex-ui-adapter.json` from `assets/codex-ui-adapter.template.json` for an HTML-based checkout.
4. Integrate through the existing global stylesheet, theme provider, or component library. For the adapter path, add `data-codex-ip-portrait` to the real portrait image and run `apply_theme_to_source.py`; it patches the HTML entry, writes live CSS, copies the identity asset, and records a reversible backup.
5. Add a theme selector and persistence only when requested.
6. Run the repository's lint, typecheck, tests, build, and rendered screenshot checks.

Prefer this mode. It preserves reviewable diffs, normal builds, and rollback.

### Adapter contract and proof

The adapter is intentionally explicit: it names the HTML entry, generated stylesheet, asset directory, portrait marker, and real selectors for canvas, sidebar, main surface, cards, and composer. Never guess selectors in an unknown checkout. Run `apply_theme_to_source.py --dry-run` first, then apply and open the target in a browser. A successful JSON export alone is not proof; the rendered page must expose `body[data-codex-skin]`, load the generated stylesheet and portrait, and show computed theme colors.

Restore the latest mutation with:

```bash
python3 <skill-dir>/scripts/apply_theme_to_source.py --target <target-project> --restore
```

## Mode B: supported theme or custom-CSS hook

Use this mode when the application exposes a documented theme directory, plugin API, extension API, DevTools override, or custom stylesheet setting.

1. Confirm the hook is designed for persistent customization.
2. Export a scoped theme bundle.
3. Install only into the documented user-writable location.
4. Record the app version and hook version.
5. Test restart, update, disable, and uninstall behavior.

Never treat a temporary DevTools edit as a persistent installation.

## Mode C: signed installed application

Use this mode when `detect_local_codex.py` finds a signed application bundle, sealed resources, or `app.asar` without an official customization hook.

Default behavior:

- inspect read-only;
- export the theme bundle;
- report the exact sealed resource and signature status;
- ask for explicit authorization before creating a separate modified copy;
- never edit the primary installed application in place;
- never overwrite user data or authentication state.

If the user authorizes a side-loaded copy, use a separate application name, bundle identifier, data directory, and backup. Expect updates, notarization, and code signing to break or replace modifications. Re-run functional and security checks after every app update.

## Safety gates

Stop before mutation when any of these are true:

- only a production signed bundle is available and no side-loaded copy was authorized;
- the app is running and the requested step requires replacing its resources;
- there is no backup or reproducible patch;
- the integration point would bypass approval, permission, authentication, or update security;
- the user's identity assets lack a confirmed publishing or commercial-use status.

Report the concrete path, signature state, and missing authorization. Do not hide the blocker behind “unsupported.”

## Rollback contract

For every persistent modification, retain:

- original app/source version;
- selected preset and identity profile;
- patch or source diff;
- files added and changed;
- build and test commands;
- uninstall or rollback instructions.
