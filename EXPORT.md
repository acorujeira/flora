# Flora export (step 0 of the app port)

Exported 10 Nov 2026 from the Flora da Corujeira artifact (version 1794277146-2b1c). The artifact itself is untouched.

- `index.html`: exported as the artifact page as published. It has since been ported: the Google Sheets connector calls are replaced by the Sheets adapter in `shell/`.
- `plates.json`: the 127 records from the artifact's `plates` collection, keyed by scientific-name slug. Every `/_blob/<id>` is replaced by a relative path.
- `plates/<slug>.webp`: one image per record. Crataegus laevigata also has `-habit.webp` and `-habit-bare.webp`.
- All 13 plates Eska supplied are included, the seven of uncertain copyright among them (Eska, 10 Nov 2026: fine for this non-commercial repo).

The Sheet id appears in `index.html`. That is expected; the data stays behind the Google login.
