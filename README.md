# UNFORTUNATELY — what 4,269 art institutions answered

**Study.** One letter of introduction was sent individually to 4,269 art institutions in 91 countries between 13 January and 2 December 2025. Every outgoing message was timestamped; every reply was coded by hand.

**Author.** Pavlo Kulyk · chaotism.art
**Version.** v2026.11.1, 25 November 2026 · DOI [10.5281/zenodo.24282476](https://doi.org/10.5281/zenodo.24282476) (resolves to the latest version)

## What is in this repository

| File | What it is |
|---|---|
| `unfortunately_dataset.csv` | The dataset: 4,269 rows × 79 columns, one row per institution. UTF-8 with BOM (opens directly in Excel). |
| `unfortunately_dataset.xlsx` | The same table as an Excel file. |
| `flagship_reference.csv` | Hand-written reference list of 171 well-known institutions in 15 countries (used for the coverage check). |
| `scripts/` | Python scripts that redraw every chart from the CSV. |
| `charts/` | All 39 charts as PNG and SVG, produced by those scripts. |
| `LICENSE`, `LICENSE-CODE`, `CITATION.cff` | Licences and citation metadata. |

## What is not in the dataset, and why

- **No texts of the letters.** The replies are private correspondence written by identifiable staff. Everything that was computed from the texts is published as ready-made columns instead: lengths (`reply_chars`, `reply_words`, `reply_chars_with_signature`, `auto_reply_chars`) and vocabulary markers (`word_*`). The short coded formulas of each reply (greeting, thank-you phrase, well-wishing phrase, sign-off) are kept, because they are the coding itself.
- **No email addresses**, neither of institutions nor of people.
- Institution names and public websites are kept so the list can be retraced.

## Headline numbers to check your copy against

Sent 4,269 · delivered 3,967 (92.9%) · any reply 388 (9.1%) · human replies 272 (6.4%) · positive feedback 54 (1.3%) · collaborations 0 · median human reply time 23.0 hours · median reply length 327 characters / 54 words · “unfortunately” in 77 of 272 human replies (28.3%) · promises kept 16 of 80 (20%).

Percentages use all 4,269 letters as the base unless a chart says otherwise.

## How to redraw the charts

You need Python 3.10 or newer with the three libraries listed in `scripts/requirements.txt` (pandas, numpy, matplotlib). Then, from this folder:

```bash
python3 scripts/charts_report.py
```

```bash
python3 scripts/charts_article.py
```

The first script draws the 33 charts of the research report (pink); the second draws the 6 charts of the press article (navy). Both read `unfortunately_dataset.csv` and write PNG and SVG files into `charts/`. Nothing is hard-coded: every number on every chart is computed from the CSV when the script runs. To change a chart, edit its block in the script (each block starts with a comment line naming the chart) and run the script again.

## How to check a number yourself

```python
import pandas as pd
d = pd.read_csv("unfortunately_dataset.csv")
human = d[d.human_reply == "YES"]
len(d), (d.delivered == "YES").sum(), len(human)        # 4269, 3967, 272
human.human_reply_hours.median()                        # 23.0
(human.word_unfortunately == "YES").mean()              # 0.283
(d[d.country == "Australia"].human_reply == "YES").mean()   # 0.225
```

In Excel: filter `human_reply` = YES to get the 272 human replies; a pivot table with `country` in rows and `human_reply` in columns gives reply rates by country.

## Which columns build which chart

| Chart file | What it shows | Columns |
|---|---|---|
| `01_funnel` | Funnel | sent → delivered → any_reply → human_reply → positive_feedback (counts of YES) |
| `02_region` | Reply rate by region | group by region: share of human_reply, positive_feedback |
| `03_countries` | Top 15 countries | group by country (15 largest): share of human_reply |
| `04_reasons` | Stated reasons | refusal_reason counts among human replies |
| `05_language, 13_vocab_expanded` | Vocabulary markers | word_* columns, personalised, advice_given, keep_on_file among human replies |
| `06_response_time` | Speed of reply | human_reply_hours (log scale) |
| `07_timeline, 11_volume_vs_rate` | Timeline; volume against rate | sent_at by month; human_reply rate by month of sending; human_reply_at for arrivals |
| `08_dow` | Day of week | weekday of sent_at and of human_reply_at |
| `09_types` | By institution type | group by institution_type (at least 35 letters) |
| `10_source, 16_bounce` | By source; bounce rate | group by source: human_reply, positive_feedback, delivered |
| `12_ooo` | Out-of-office by month | out_of_office = YES, month of auto_reply_at |
| `14_promises` | Promises | auto_reply → promise_made → promise_kept |
| `17_top5` | Flagship coverage | institution names matched against the reference list inside the script (also flagship_reference.csv) |
| `18_lengths, 20_lengths_by_country` | Lengths | auto_reply_chars, reply_chars_with_signature, reply_chars; by country |
| `21 to 29, 32, 33` | Anatomy of a rejection | has_* slots, gtwc_pattern, greeting_*, thank_you_phrase, well_wishing_phrase, closing_phrase, n_structural_slots, reply_words |
| `30, 31` | Formality by country | greeting_honorific, greeting_bucket by country |
| `34_wiki_gap` | Wikipedia coverage by type | index_type, wikipedia_editions (blank is not zero) |
| `35_top_of_field` | Reply rate by prominence | index_type, art_fairs, wikipedia_editions, human_reply |
| `fig1 to fig6` | Six article charts | funnel; human_reply_hours; slots; promise_timeliness and overdue days; country rates; refusal_reason |

## Things to know before analysing

- `wikipedia_editions` blank is **not** zero: blank means no Wikidata entity could be confirmed, so nothing was measured. Zero means a confirmed entity with no article.
- There are two type classifications: `institution_type` (assigned by hand, used in most charts) and `index_type` (8 types, used with the prominence index). They do not coincide exactly: 430 museums by the first, 483 by the second.
- There are two “flagship” notions: `reference_flagship` (119 rows matching the hand-written list) and `quadrant` = flagship (128 rows high on both prominence and capacity).
- Overdue promises are counted as of 16 November 2026 (`promise_days_overdue_asof_2026-11-16`). To recount for another date: that date minus `promise_deadline`, for rows where `promise_timeliness` is “No human reply after fixed deadline”.
- Observation closed on 3 December 2025. One later human reply (22 June 2026, 294 days after the letter) is not included.
- A letter silently filed as spam cannot be told apart from one that was read and ignored; `delivered` = NO records only outright bounces.
- A few rows share a name because they are different institutions (three called “Artspace”) or two addresses of one organisation with separate websites.

## Data dictionary

| Column | Filled rows | Meaning |
|---|---|---|
| `id` | 4,269 | Row number, 1–4269. |
| `institution` | 4,269 | Name of the institution as listed in the source. |
| `url` | 4,254 | Public website. |
| `country` | 4,269 | Country. |
| `city` | 4,269 | City. |
| `region` | 4,269 | Continent-level region (6 values). |
| `institution_type` | 4,269 | Hand-assigned category (Art Gallery, Museum, Art Center …). Used in the 'by institution type' chart. |
| `source` | 4,269 | Directory or list the contact came from. 'Own research' = found by the author's own searching. |
| `sent` | 4,269 | YES for every row (a letter was sent). |
| `sent_at` | 4,269 | Timestamp of the outgoing letter (author's local time). |
| `delivered` | 4,269 | NO if the receiving mail server rejected the letter (bounce). |
| `any_reply` | 4,269 | YES if anything came back, automatic or human. |
| `auto_reply` | 4,269 | YES if an automatic reply was received. |
| `auto_reply_at` | 134 | Timestamp of the automatic reply. |
| `auto_reply_days` | 134 | Delay of the automatic reply, in days. |
| `human_reply` | 4,269 | YES if a person replied. The 272 YES rows are the corpus for all reply-anatomy columns. |
| `personalised` | 272 | Human replies: YES if the reply addresses the sender by name. |
| `human_reply_at` | 272 | Timestamp of the human reply. |
| `human_reply_days` | 272 | Delay of the human reply, in days. |
| `promise_made` | 134 | Automatic replies: YES if the text promises that a person will follow up. |
| `promise_max_days` | 42 | Promised window in days (upper bound), where a window was named. |
| `promise_kept` | 4,269 | YES if a human reply followed a promising automatic reply. |
| `out_of_office` | 4,269 | YES if the automatic reply is an out-of-office / holiday notice. |
| `cooperation_agreed` | 250 | Human replies: did the reply agree to a collaboration (never YES). |
| `positive_feedback` | 272 | Human replies: YES if the reply says something positive about the work. |
| `word_unfortunately` | 337 | YES if the reply contains 'unfortunately' (coded by hand). |
| `word_unsolicited` | 4,269 | Human replies: contains 'unsolicited'. |
| `word_curator` | 4,269 | Human replies: contains a word starting with 'curator'. |
| `refusal_reason_raw` | 128 | Human replies: stated refusal reason (six categories), as coded. |
| `refusal_reason` | 128 | Same six categories; filled only where a reason was explicitly given (128 rows). |
| `advice_given` | 296 | YES if the reply offered advice or redirected to another institution. |
| `keep_on_file` | 36 | YES if the reply promised to keep the proposal on file. |
| `greeting` | 261 | Human replies: the greeting line as written (e.g. 'Dear Pavlo,'). |
| `greeting_formula` | 260 | Greeting word (Dear / Hi / Hello …). |
| `greeting_honorific` | 30 | Honorific used, if any (Mr / Herr / Sir). |
| `greeting_name_used` | 252 | Form of the sender's name used in the greeting. |
| `greeting_punctuation` | 232 | Punctuation after the greeting. |
| `thank_you_phrase` | 238 | Opening thank-you phrase, shortened to its formula. |
| `well_wishing_phrase` | 139 | Well-wishing phrase before the sign-off. |
| `closing_phrase` | 244 | Sign-off phrase. |
| `human_reply_hours` | 272 | Delay of the human reply, in hours. |
| `auto_reply_hours` | 134 | Delay of the automatic reply, in hours. |
| `has_greeting` | 4,269 | Derived: greeting slot filled. |
| `has_thanks` | 4,269 | Derived: thank-you slot filled. |
| `has_wish` | 4,269 | Derived: well-wishing slot filled. |
| `has_closing` | 4,269 | Derived: sign-off slot filled. |
| `n_structural_slots` | 4,269 | Derived: number of the four optional slots filled (0–4). |
| `gtwc_pattern` | 4,269 | Derived: four-letter code of filled slots (G, T, W, C; '·' = empty). |
| `greeting_bucket` | 4,269 | Derived: Dear / Hi-Hey / Hello / Other. |
| `reply_words` | 4,269 | Human replies: length in words, signature stripped. |
| `reply_chars` | 4,269 | Human replies: length in characters, signature stripped. |
| `letter_version` | 4,269 | Version of the outgoing letter (V1–V5), assigned by sending date. |
| `reference_flagship_match` | 119 | Name on the hand-written flagship reference list that this row matches, if any. |
| `reference_flagship` | 4,269 | True for the 119 rows matching flagship_reference.csv. |
| `index_type` | 4,065 | Institution type in the prominence index (8 types; assigned separately from institution_type). |
| `prominence` | 1,827 | Prominence percentile within index_type (blank = not measurable). |
| `capacity` | 4,065 | Capacity percentile within index_type (website size, domain age, mail set-up). |
| `quadrant` | 1,827 | Position on the two axes: flagship / known but small / large, little written about / other (blank = prominence not measurable). |
| `prominence_instrument` | 4,065 | 'record' (public record, mainly Wikipedia) or 'fairs' (art-fair participation). |
| `wikipedia_editions` | 1,237 | Number of Wikipedia language editions with an article. Blank = no Wikidata entity could be confirmed (NOT zero). |
| `art_fairs` | 4,269 | Number of the 20 selective art fairs the institution exhibits at. |
| `word_we_wish` | 272 | Human replies: contains 'we wish'. |
| `word_success` | 272 | Human replies: contains a word starting with 'success'. |
| `word_good_luck` | 272 | Human replies: contains 'good luck'. |
| `word_team` | 272 | Human replies: contains a word starting with 'team'. |
| `word_programme` | 272 | Human replies: contains 'programme' / 'program'. |
| `word_curatorial` | 272 | Human replies: contains 'curatorial'. |
| `word_director` | 272 | Human replies: contains 'director'. |
| `word_committee` | 272 | Human replies: contains 'committee'. |
| `reply_chars_with_signature` | 272 | Human replies: length in characters including the signature block. |
| `auto_reply_chars` | 134 | Automatic replies: length in characters. |
| `promise_timeframe_stated` | 80 | The promised timeframe as worded in the automatic reply (short phrase). |
| `promise_period_group` | 80 | Promised window, grouped. |
| `promise_deadline` | 42 | Deadline implied by the promise, where a window was named. |
| `promise_timeliness` | 80 | Outcome of the promise (5 categories: on time / late / reply without deadline / no reply after deadline / no reply, no deadline). |
| `promise_days_vs_deadline` | 42 | Days between the deadline and the human reply (+ early, − late); for unanswered promises, as originally computed on 5 June 2026. |
| `promise_days_overdue_asof_2026-11-16` | 32 | For the 32 promises with a deadline and no human reply: days overdue on 16 November 2026. |
| `category_2` | 1,808 | Optional second hand-assigned category. |
| `top_level_domain` | 4,254 | Top-level domain of the website. |

## Licence

- Data and charts (`*.csv`, `*.xlsx`, `charts/`): [Creative Commons Attribution 4.0 International](LICENSE) (CC BY 4.0).
- Code (`scripts/`): [MIT](LICENSE-CODE).

## Use of AI tools

The chart scripts in `scripts/` and this documentation were written with the help of an AI coding assistant (Claude, Anthropic). No AI tool was used to classify the replies: the author coded every reply by hand. The author checked the scripts and their output against the data and is responsible for the dataset and for every figure derived from it.

## How to cite

Kulyk, P. (2026). *UNFORTUNATELY: replies of 4,269 art institutions to one letter of introduction* (v2026.11.1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24282476

This DOI always resolves to the latest version. Each version also has a DOI of its own, listed below; cite that one if you need the exact files you used.

Machine-readable metadata is in `CITATION.cff`.

## Versions

| Version | Date | DOI | Changes |
|---|---|---|---|
| v2026.11.1 | 25 November 2026 | assigned by Zenodo | Chart 33 (`33_mangled_names`) redrawn: each card is as wide as its name, so a long name no longer spills into the next card. Data unchanged. |
| v2026.11 | 16 November 2026 | [10.5281/zenodo.24282477](https://doi.org/10.5281/zenodo.24282477) | First public release. |
