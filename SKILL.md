---
name: research-newspaper
description: Produce a source-grounded daily research newspaper in any field, with illustrated HTML issues, organization timelines, technology guides, comparative reviews, statistics, and persistent trend/forecast memory. Use for “出版一下今天的报纸”, publish today's newspaper, or updates to an existing research newspaper.
---

# Research Newspaper

Turn the user's research interests into a cumulative newspaper, not a list of headlines. Trigger phrase: **出版一下今天的报纸**. Reuse the selected newspaper's saved profile on later invocations.

This skill is provider-neutral: use the current agent's browsing, file-editing, execution and optional browser tools. It requires no particular model, API key, plugin, agent framework or subscription. Actual execution needs web access for new research, a writable workspace, and Python 3.10+ for the bundled renderer/database. If a host cannot discover SKILL.md, have its agent read this file explicitly. A trigger phrase alone cannot install or load a skill in an arbitrary host.

## Start or continue

Locate the newspaper requested by the user; read its `profile.json`, `AGENTS.md`, catalog, latest issue, reviews and research journal. If several newspapers match, ask which one. Never merge unrelated directions silently.

On first use, ask for the missing **research field and questions the reader cares about** in one concise question. Infer language/timezone from trusted user context or ask if unknown. Suggest independent classification axes appropriate to the field; get the user's choice before applying unfamiliar categories. Model/method, contribution type and application setting are useful axes; do not force robotics tags onto other fields.

Initialize a **new** directory with:

```text
python scripts/init_report.py --output /absolute/path/to/newspaper --topic "research field" --focus "reader's questions" --timezone Asia/Shanghai --date YYYY-MM-DD
```

Paths to scripts are relative to this skill. Existing newspapers are edited in place, not reinitialized. The bootstrap creates editable source data; running build.py emits four self-contained HTML files containing five views (organization flow shares index.html). Read [data contract](references/data-contract.md) when writing records.

## Publish today's issue

1. Determine today in the profile timezone from trusted client date/time. Read prior trend versions and forecast reviews **before** researching. Record coverage gaps, overdue forecasts and previous reasoning errors that need follow-up.
2. Research recent primary papers, official projects, repositories and institutional releases. Default to the latest seven days, using recent/history items only when useful and visibly labelled. Search beyond evidence that supports the reader's idea. Use independent source/team clusters; mirrors, press copies and shared benchmarks are not independent confirmation.
3. Verify source event date, first publication versus revision/availability, affiliations, benchmark protocol and resource availability. Deduplicate stable work IDs. Keep discovery/review dates separate. If sources cannot be checked, report that limit; do not fabricate today's news. No credible additions is a valid issue.
4. For each paper, obtain its original Abstract and translate it in full into the reader's language; preserve qualifications, numbers, negative results and availability claims. Save the original, translation, exact source version and verification date separately from editorial summaries. Check official articles for companion papers; if no Abstract is available, explain its absence instead of inventing one. Write meaningful baseline comparisons, practical value, experimental conditions/techniques, likely improvement source, uncertainty and cost using the [review guide](references/review-and-memory.md). Benchmarks, datasets, infrastructure and viewpoints have value without defeating a model. Missing comparisons stay unknown, not invented.
5. Include an original credited figure where it clarifies the work, using a lawful accessible local copy. Preserve original URL/caption/credit; otherwise show an explicit text fallback. Do not use generated figures as experimental evidence. Add/update organization profiles and technology explanations; distinguish method adoption from related ideas and speculation.
6. Add classifications, abstract records and reviews for every catalog item, update organization evidence links, then append `data/editions/YYYY-MM-DD.json`. The daily work-detail dialog must include the original-Abstract translation, English/original-language text, baselines, fair usefulness judgment, comparison conditions, attribution and costs. Statistics must reuse the daily page's work-card and detail renderer, including figures and source/team/technology links; do not confine reviews to statistics or maintain a second copy. Keep previous issues unchanged. On a second run the same day, check the existing issue: a no-change rerun is a no-op; a material correction/supplement uses a new ID such as `YYYY-MM-DD-r2.json` and matching `id`, preserving original `date`. Do not overwrite a registered issue.
7. Reconcile trends, counterevidence and forecasts with today's findings. Append new statement versions and evaluation records; never rewrite registered predictions to improve apparent accuracy. See [review and memory](references/review-and-memory.md). Forecasts are optional; do not invent one merely to populate the page.
8. Run `python build.py` **without Python optimization flags**, then `python check_report.py`. Verify the rendered daily, organization, technology, statistics and trend pages if a supported browser is available: open the same work from the daily and statistics cards and confirm matching abstract/review details; check original-text expansion, missing-Abstract labels, old issue selection, filters, empty results, evidence links, phone width, images and script errors. Otherwise state the visual verification limit; do not claim screenshots or tests you did not run.
9. Deliver the newspaper path/link, new versus background counts, meaningful findings and verification limits. Preserve source JSON and SQLite for tomorrow. Serving locally is optional (`python serve.py`); publication to GitHub, a LAN endpoint or hosting and scheduled execution require user authorization. “Publish today's newspaper” means produce the local issue unless a destination is configured and authorized.

## Durable memory

The build appends work/review revisions (including sourced Abstracts), immutable issues, statement versions, forecasts, evaluations and complete snapshots to SQLite. JSON remains the editable authoring source; the database preserves previous content. Never delete the database to bypass a conflict. Reuse unchanged IDs; revise immutable records with a new ID and explanation. For existing newspapers, follow the [data contract's migration guidance](references/data-contract.md); a display/metadata correction alone does not require inventing a new daily issue or changing old forecasts.

Improve judgments through source diversity, competing explanations, explicit failure conditions and prospective error review, not through article counts alone. This is a maintained research procedure, not automatic model training or an autonomous background service. Each later invocation performs the procedure using the saved memory.
