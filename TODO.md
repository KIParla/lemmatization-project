# Lemmatization TODO

Snapshot of progress across the four modules currently in scope (KIP, KIPasti, ParlaBO, ParlaTO).
Regenerate this file's counts/lists whenever `wip/`, `patches/` or the modules' `tsv/` change — it's a snapshot, not a live view.

## Workflow

Each conversation moves through four states (see `docs/modules/ROOT/pages/pipeline.adoc`):

1. **Not started** — never pulled out of the module's `tsv/` into `wip/<module>/<code>.csv`.
2. **In progress** — a `.csv` exists in `wip/<module>/`, but no matching patch exists yet in `patches/<module>/`.
3. **Patch ready** — `patches/<module>/<code>.vert.tsv.patch` + `.vert.tsv.recap.md` exist, not yet applied to the module's `dev`.
4. **Integrated** — transcription corrections applied and `lemma`/`upos` (with the `syntactic` rows) present in the module's `tsv/` on `dev`, `eaf` and linear files regenerated.

## Cross-cutting checks

### Truncated words to check manually

- [ ] percento — 104 occurrences as single token `percento` (22 files) vs. 93 as separate `per` + `cento` tokens (checked 2026-07-20)

## Summary

| Module | Total conversations | Integrated | Patch ready | In progress | Not started |
|---|---|---|---|---|---|
| KIP | 121 | 22 | 27 | 0 | 72 |
| KIPasti | 63 | 0 | 5 | 0 | 58 |
| ParlaBO | 85 | 0 | 2 | 0 | 83 |
| ParlaTO | 67 | 0 | 2 | 0 | 65 |
| **Total** | **336** | **22** | **36** | **0** | **278** |

## Integrated

Applied on KIP `dev` (commits of `moduli/KIP`; "—" = nothing to do for that step):

| Conversation | Date | Transcription corrections | Lemma, upos, syntactic rows | eaf and linear |
|---|---|---|---|---|
| BOA1001 | 2026-10-28 | `b505d91` | `8a27e82` | `b505d91` |
| BOA1002 | 2026-10-29 | `a14c76e` | `47c2555` | `ff396f0` |
| BOA1003 | 2026-10-29 | `14d3b01` | `47c2555` | `ff396f0` |
| BOA1004 | 2026-10-29 | `d7d5d42`, `1545d75` | `47c2555` | `ff396f0` |
| BOA1005 | 2026-10-30 | `a3f487f` | `54f767e` | `f682d55` |
| BOA1006 | 2026-10-30 | `03c9d1f` | `54f767e` | `f682d55` |
| BOA1007 | 2026-10-30 | `83c4acf` | `54f767e` | `f682d55` |
| BOA1008 | 2026-10-30 | — | `54f767e` | — |
| BOA1009 | 2026-10-30 | `4c32806` | `d43655b` | `62c1ffd` |
| BOA1010 | 2026-10-30 | `3e5dfa6` | `dea2d38` | `3725f87` |
| BOA1012 | 2026-11-01 | `f1e1fc8` | `64848fd` | `3d1cac7` |
| BOA1014 | 2026-11-01 | `415d5af` | `64848fd` | `3d1cac7` |
| BOA1015 | 2026-11-01 | `c3be461` | `804d79f` | `d914303` |
| BOA1017 | 2026-11-01 | — | `64848fd` | — |
| BOA1025 | 2026-11-01 | `6db7a59` | `64848fd` | `3d1cac7` |
| BOA3001 | 2026-11-01 | `78775cf` | `ff23e61` | `6bb111a` |
| BOA3004 | 2026-11-01 | `0828b93` | `ff23e61` | `6bb111a` |
| BOA3010 | 2026-11-01 | `ad2c5af` | `3a3501d` | `28d41ea` |
| BOA3011 | 2026-11-01 | `dbb0741` | `18e3d37` | `c18e8dc` |
| BOA3012 | 2026-11-01 | — | `18e3d37` | — |
| BOA3013 | 2026-11-01 | `516410e` | `18e3d37` | `c18e8dc` |
| BOA3015 | 2026-11-01 | `63ed8ca` | `18e3d37` | `c18e8dc` (+ `6cb4dc4`) |

BOA3004: `525-0` is now a `((ride))`; the overlap group 136 now has the whole-token overlap `X(136)` on it, check it. The overlaps of the deleted `6-3` (guesses) have to be assigned by hand.

BOA1015: `23-2` (a pause that was between `venti` and `cinque`, now merged into `venticinque`) comes after the word; the overlaps of the deleted `24-7` and `176-13` have to be assigned by hand.

BOA1009: the overlaps of `17-1` (group 6, whose other member `18-0` is gone) and of the deleted `156-4`, `157-0`, `157-1` still have to be assigned by hand in the tsv.

### Integrated, with an update patch to apply on `dev`

These conversations are already on KIP `dev` (transcription, lemma and upos), but `wip/` has been corrected afterwards (incomprehensible words normalised to lemma `x`, upos `X`; pauses; `Truncated`/`SpaceAfter`), so `make_patch.py` produced a new single patch for each. The recap says what changes.

| Conversation | Patch | What changes |
|---|---|---|
| BOA1001 | `patches/KIP/BOA1001.vert.tsv.patch` | `721-2` `xxx`: upos `NOUN` → `X` |
| BOA3001 | `patches/KIP/BOA3001.vert.tsv.patch` | 3 words `x~` → `x` (lemma `x`, upos `X`, no `Interrupted=Yes`); pause `[(.)]` form → `(.)` |
| BOA3010 | `patches/KIP/BOA3010.vert.tsv.patch` | `1154-7` `c'`: `Truncated=Yes` → `SpaceAfter=No` |
| BOA3011 | `patches/KIP/BOA3011.vert.tsv.patch` | `179-0` `xxxxx`: lemma `xxx` → `x` |

BOA1017 has the same kind of update (`244-1` `xx`: `SYM` → `X`) but no patch yet: its `patches/KIP/BOA1017.review.csv` has edits not yet carried into `wip/`; regenerate after running `make_patch.py` on it.

## Patch ready (apply next)

Items still to check by hand in each recap (`da verificare`) and timestamp conflicts. Patches with 0 items can be applied straight away.
Where there are two patches, apply `<code>.vert.tsv.patch` (transcription) first and then `<code>.vert.tsv.pos.patch` (lemma, upos, syntactic rows), see `docs/modules/ROOT/pages/patching.adoc`.

| Conversation | Module | To check | Conflicts | Patches |
|---|---|---|---|---|
| BOA3016 | KIP | 0 | 0 | patch + pos.patch |
| BOC1008 | KIP | 0 | 0 | patch + pos.patch |
| BOD1001 | KIP | 0 | 0 | patch + pos.patch |
| BOD1005 | KIP | 0 | 0 | patch + pos.patch |
| KPC001 | KIPasti | 0 | 0 | patch + pos.patch |
| KPC008 | KIPasti | 0 | 0 | patch + pos.patch |
| PTA002 | ParlaTO | 0 | 0 | patch + pos.patch |
| PTB005 | ParlaTO | 0 | 0 | patch + pos.patch |
| BOC1001 | KIP | 1 | 0 | patch + pos.patch |
| BOC1005 | KIP | 1 | 0 | patch + pos.patch |
| BOD1011 | KIP | 1 | 0 | patch + pos.patch |
| KPC003 | KIPasti | 1 | 0 | patch + pos.patch |
| KPN014 | KIPasti | 1 | 0 | patch + pos.patch |
| TOA3010 | KIP | 1 | 0 | patch + pos.patch |
| TOC1006 | KIP | 1 | 0 | patch + pos.patch |
| TOD1005 | KIP | 1 | 0 | patch + pos.patch |
| BOA1011 | KIP | 2 | 0 | patch + pos.patch |
| BOA3018 | KIP | 2 | 0 | patch + pos.patch |
| BOD1003 | KIP | 2 | 0 | patch + pos.patch |
| BOD1004 | KIP | 2 | 0 | patch + pos.patch |
| TOA3008 | KIP | 2 | 0 | patch + pos.patch |
| TOD1008 | KIP | 3 | 0 | patch + pos.patch |
| BOD2005 | KIP | 4 | 0 | patch + pos.patch |
| KPC004 | KIPasti | 5 | 0 | patch + pos.patch |
| TOD1002 | KIP | 5 | 1 | patch + pos.patch |
| BOC1009 | KIP | 6 | 0 | patch + pos.patch |
| PBC007 | ParlaBO | 22 | 0 | patch + pos.patch |
| BOA3021 | KIP | 23 | 0 | patch + pos.patch |
| BOD2007 | KIP | 31 | 0 | patch + pos.patch |
| TOD1016 | KIP | 33 | 0 | patch + pos.patch |
| BOD2018 | KIP | 38 | 0 | patch + pos.patch |
| PBB004 | ParlaBO | 46 | 7 | patch + pos.patch |
| BOD2009 | KIP | 53 | 0 | patch + pos.patch |
| BOA3017 | KIP | 72 | 12 | patch + pos.patch |
| TOA1006 | KIP | 105 | 0 | patch + pos.patch |
| TOD1005bis | KIP | 109 | 4 | patch + pos.patch |

## In progress (finish these next)

Nothing pending — every `wip/` CSV has a patch or is already integrated.

## Not started

### KIP (72)

BOA1013, BOA1016, BOA1018, BOA3002, BOA3003, BOA3006, BOA3007, BOA3019, BOA3020, BOC1002, BOC1003, BOC1004, BOC1006, BOC1007, BOD1006, BOD1007, BOD1009, BOD1010, BOD2001, BOD2003, BOD2006, BOD2008, BOD2010, BOD2011, BOD2013, BOD2014, BOD2015, BOD2016, BOD2017, BOD2019, TOA1001, TOA1002, TOA1003, TOA1004, TOA1005, TOA3001, TOA3002, TOA3003, TOA3004, TOA3005, TOA3006, TOA3007, TOA3009, TOA3011, TOA3012, TOA3013, TOA3014, TOC1001, TOC1002, TOC1003, TOC1004, TOC1005, TOC1007, TOD1014, TOD1015, TOD1017, TOD2001, TOD2002, TOD2003, TOD2004, TOD2005, TOD2006, TOD2007, TOD2008, TOD2009, TOD2010, TOD2011, TOD2012, TOD2013, TOD2014, TOD2015, TOD2016

### KIPasti (58)

KPC002, KPC005, KPC006, KPC007, KPC009, KPC011, KPN001, KPN002, KPN003, KPN004, KPN005, KPN006, KPN007, KPN009, KPN010, KPN011, KPN012, KPN013, KPN015, KPN016, KPN017, KPN018, KPN019, KPN020, KPN021, KPN022, KPN023, KPN024, KPN025, KPN026, KPN027, KPN028, KPN029, KPN030, KPN031, KPS001, KPS002, KPS003, KPS004, KPS005, KPS006, KPS007, KPS008, KPS009, KPS010, KPS011, KPS012, KPS013, KPS014, KPS015, KPS016, KPS017, KPS018, KPS021, KPS022, KPS023, KPS024, KPS025

### ParlaBO (83)

PBA001, PBA002, PBA003, PBA004, PBA005, PBA006, PBA007, PBA008, PBA009, PBA010, PBA011, PBA012, PBA013, PBA014, PBA015, PBA016, PBA017, PBA018, PBA019, PBA020, PBA021, PBA025, PBA026, PBA027, PBA028, PBA029, PBA030, PBB001, PBB002, PBB003, PBB005, PBB006, PBB007, PBB008, PBB009, PBB010, PBB011, PBB012, PBB013, PBB014, PBB015, PBB016, PBB017, PBB018, PBB019, PBB020, PBB021, PBB022, PBB023, PBB024, PBB025, PBB026, PBB027, PBB028, PBB029, PBB030, PBB031, PBB032, PBB033, PBC001, PBC002, PBC003, PBC004, PBC005, PBC006, PBC008, PBC009, PBC010, PBC011, PBC012, PBC013, PBC014, PBC015, PBC016, PBC017, PBC018, PBC019, PBC020, PBC021, PBC022, PBC023, PBC024, PBC025

### ParlaTO (65)

PTA001, PTA003, PTA005, PTA006, PTA007, PTA012, PTA013, PTA015, PTA016, PTA017, PTA018, PTB001, PTB002, PTB003, PTB004, PTB007, PTB008, PTB009, PTB014, PTB015, PTB018, PTB019, PTB020, PTB021, PTB022, PTB023, PTB024, PTB025, PTB026, PTD001, PTD003, PTD004, PTD005, PTD006, PTD007, PTD008, PTD009, PTD010, PTD011, PTD012, PTD013, PTD014, PTD015, PTD016, PTD017, PTD019, PTD020, PTD021, PTD022, TOD2001, TOD2002, TOD2003, TOD2004, TOD2005, TOD2006, TOD2007, TOD2008, TOD2009, TOD2010, TOD2011, TOD2012, TOD2013, TOD2014, TOD2015, TOD2016

*(Note: TOD20xx codes appear in both KIP's and ParlaTO's `metadata/conversations.tsv` — that's the source data, not a bug in this list.)*


## Migliorie
- verbi pronominali con pronome staccato (tipo me ne vado)
- lemmi delle lettere dell'alfabeto? (a bi ci ipsilon lambda)