# Starfall Salvage launch-page draft

Static launch website for version 1.1, deployed with authorized owner-only access at [the private site](https://starfall-salvage.steph4n1.chatgpt.site). The page carries a private-draft banner and `noindex, nofollow`; neither is access control. Preserve owner-only hosting access until public release is explicitly approved.

Edit `index.template.html` for page copy. Repeated release metadata comes from `../release/release-manifest.json`; run `python3 scripts/sync-release.py sync` from the game repository root and then the check/tests documented in [the release workflow](../docs/RELEASE-WORKFLOW.md). Do not edit the generated HTML or duplicate download/screenshot copies directly.

The `dist/` folder is self-contained. Serve it locally, for example:

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

Open the local URL printed by the server. There is no build step, dependency installation, analytics, remote font, or remotely loaded script. The landing-page JavaScript enlarges screenshots in an accessible native dialog. The separate `play/` route includes the official Binjgb JavaScript/WebAssembly player and ROM, all served locally without third-party requests. Download links resolve to local files under `dist/downloads/`.

## Contents and evidence

- Native player ZIP, exact reviewed manual, release notes, credits, and download checksums.
- Eight unaltered 160×144 screenshots from the exact native 1.1 ROM; seven are displayed and one is retained as an additional flight-deck asset. `dist/assets/screenshots.json` records their hashes without local machine paths. The full internal provenance stays outside this page.
- Play in Browser opens `play/index.html`, a byte-identical copy of the nine-file official export in `../release/browser-v1.1`. Its ROM/runtime match the completed local browser campaign. Browser files remain separate from the native ZIP; no ephemeral preview URL is embedded. The original plugin preview and its saved progress remain separate. Saves do not sync across devices. [The site integration check](../docs/SITE-PLAY-VERIFICATION.json) covers the button, controls and ordinary reload → Continue on the local site origin.
- References: [GB Studio web build](https://www.gbstudio.dev/docs/build/) and [SameBoy capabilities](https://sameboy.github.io/features/).

## Before public release

Resolve the original-work licensing and retained-asset provenance review. The complete local browser campaign and fresh-emulator SRAM Continue checks passed; see `../docs/BROWSER-VERIFICATION.json`. Complete hardware, audio, power-off save and final-host browser tests, then update compatibility copy only for the exact combinations actually tested. Run blind player tests to refine onboarding and pacing. Choose a support channel and add it before launch. No typical first-time completion duration is advertised.

If a public browser edition is added later, link only its verified stable URL. Do not copy an ephemeral plugin preview address. Remove the draft banner/noindex only as part of an explicitly authorized public release. Sites identity is recorded in `.openai/hosting.json`; reuse that exact project. The game repository has a check-only GitHub Actions workflow. No automatic deployment is configured. Use the Sites skill to push/package the validated site, save a version and perform the authorized owner-only deployment. Public release requires separate authorization.
