# Starfall Salvage launch-page draft

Local-only static launch page for version 1.1. No hosting registration or deployment has been performed. The page carries a private-draft banner and `noindex, nofollow`; neither is access control. Keep hosting private until publication is explicitly approved.

The `dist/` folder is self-contained. Serve it locally, for example:

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

Open the local URL printed by the server. There is no build step, dependency installation, analytics, remote font, or third-party script. The only JavaScript enlarges screenshots in an accessible native dialog. Download links resolve to local files under `dist/downloads/`.

## Contents and evidence

- Native player ZIP, exact reviewed manual, release notes, credits, and download checksums.
- Eight unaltered 160×144 screenshots from the exact native 1.1 ROM; seven are displayed and one is retained as an additional flight-deck asset. `dist/assets/screenshots.json` records their hashes without local machine paths. The full internal provenance stays outside this page.
- Installation routes and tested/untested status are explicit. Browser playback is described as separate, with no invented public play URL. The original browser export and ongoing human preview are untouched.
- References: [GB Studio web build](https://www.gbstudio.dev/docs/build/) and [SameBoy capabilities](https://sameboy.github.io/features/).

## Before public release

Resolve the original-work licensing and retained-asset provenance review. Complete the agreed hardware, audio, cold-save and browser tests, then update compatibility copy only for the exact combinations actually tested. Run blind player tests to refine onboarding and pacing. Choose a support channel and add it before launch. No typical first-time completion duration is advertised.

If a public browser edition is added later, link only its verified stable URL. Do not copy an ephemeral plugin preview address. Remove the draft banner/noindex only as part of an explicitly authorized public release. No publishing scripts or automatic deployments are configured here.
