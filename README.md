# Flora da Corujeira

The plants of A Corujeira as an installable web app: a wall of plant cards with botanical plates, read from one Google Sheet with your own Google login. It works with no signal, from the last copy it read.

The plant data is never in this repo. It stays in the Sheet, behind the Google login, and in a private copy on each device.

## What is where

- `index.html`: Flora itself (the page and its code).
- `shell/`: the app shell, kept apart from Flora so a second lens can share it.
  - `config.js`: the Google client ID and the scope. Read-only in this version.
  - `auth.js`: Google sign-in in the browser.
  - `sheets.js`: the Sheets adapter (read a range, update a range).
  - `store.js`: the offline copy of the last read.
  - `shell.js`: service worker registration and wake-up events.
- `sw.js`: the service worker. It keeps the shell and the plates on the device.
- `manifest.webmanifest`, `icons/`: the app's name, colours and owl icon.
- `plates.json`, `plates/`: the botanical plates and their credits.

## Changing things

- This repo is Flora's only home for code (since 10 Nov 2026). The old Claude artifact is a frozen backup; never edit it.
- After changing any file, raise `VERSION` in `sw.js`. Every device fetches the new files and reloads itself once. Raise `PLATES_VERSION` only when plate images change.
- Editing from the app is switched off by one flag, `CAN_EDIT` in `index.html`. Turning it on also needs `allowWrites` and the wider `spreadsheets` scope in `shell/config.js`.
- To try it on the Mac: `python3 -m http.server 8765` in this folder, then open `http://localhost:8765`.

## Plates

Most plates are public domain, from Wikimedia Commons; each record in `plates.json` names its artist and source page. See `EXPORT.md` for how they were exported.
