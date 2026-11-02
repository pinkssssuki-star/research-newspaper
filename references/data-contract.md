# Data contract (renderer v1)

All paths are relative to an initialized newspaper. UTF-8 JSON; stable IDs; ISO `YYYY-MM-DD` dates. `datePrecision: "month"` permits a source event `YYYY-MM`, not an invented day. `catalog.asOf` is the trusted current local date. Keep source event calendar/timezone notes. On initial setup replace placeholder taxonomy values after user confirmation; leave keys `model`, `workType`, `embodiment` for renderer compatibility. Their UI meanings are research object/method, contribution type, application setting.

## Authoring files

- `profile.json`: title, topic, readerFocus, timezone, language, windowDays, historyDays, outputPolicy, trigger. Adapt UI wording/language when needed; source date semantics stay unchanged.
- `data/catalog.json`: schemaVersion=1, title, asOf, timezone, datePolicy, organizations[], technologies[], works[].
- `data/classifications.json`: `{workId: {model: [taxonomy labels], workType: [...], embodiment: [...], basis: "what the paper actually proposes/tests"}}`. Every work has each axis, multiple labels allowed. A work can evaluate a model without introducing it.
- `data/reviews-*.json`: each file is `{workId: review}`. Each work appears exactly once across these files. See review fields below.
- `data/abstracts.json`: `{workId: abstractRecord}` for every work. Store the original Abstract and its full translation separately from editorial summaries; see the Abstract fields below.
- `data/organization-profiles.json`: `{organizationId: profile}`. An organization may be an identified author/project group; do not invent affiliation.
- `data/editions/YYYY-MM-DD.json`: date, label, windowStart, featuredIds[], headline, deck, notes:[{label,text}], optional coverage:{verifiedAt,sourcesChecked:[],scope}. For a same-day supplement use an immutable `id` (e.g. `2026-11-01-r2`), `revision:2`, and a new file with that ID; keep the original date. An empty featuredIds list is valid: explain the absence of verified additions in notes. Do not republish old work as new merely to fill an issue.
- `data/research-journal.json`: startedOn, statements[], forecasts[], evaluations[], workflow:[{title,text}], labDirections[]. Lists may be empty; never invent a forecast or trend.
- `data/research.sqlite3`: generated append-only history. Do not edit/delete to resolve a validation error. Source JSON is the current authoring state; SQLite retains earlier revisions and full snapshots. Same-day corrected reviews append a new hash; immutable records need new IDs.

## Work

Required fields used by the five-page renderer:

```json
{
  "id": "stable-id", "short": "Short title", "title": "Full original title",
  "date": "2026-11-01", "dateType": "first publication",
  "firstPublishedAt": "2026-11-01", "orgIds": ["team-id"],
  "tags": ["research topic"], "headline": "Reader-facing headline",
  "summary": "Concise source-grounded summary", "facts": ["Verified observation"],
  "limits": "Evidence boundary", "relevance": "Connection to reader questions",
  "sources": [{"label": "Primary source", "url": "https://example.org/paper"}],
  "affiliationNote": "Verified affiliation or unknown", "evidenceType": "preprint",
  "resources": "Availability and reproduction status",
  "discoveredAt": "2026-11-01", "verifiedAt": "2026-11-01", "techIds": []
}
```

This example describes structure, not an actual work. Optional image: `{local:"assets/figure.jpg",sourceUrl:"https://…",caption:"…",credit:"…",fit:"contain"}`. The local file must exist, be an actual safe web image, and have the matching extension. Paths must remain inside the newspaper. Never copy another topic's figure or silently disable TLS verification to fetch one. Without a verified lawful image, omit image and use the text fallback.

## Review

`reviewedAt`, `depth`, `editorialSummaryZh` (editorial explanation, not an Abstract translation), `baselines:[{name,setting,result,sourceUrl}]`, `resultSummary`, `verdict`, `conditions:[{factor,observation,impact}]`, `attribution:{main,evidence,confidence,unresolved}`, `cost`, `bestBaselineReason`, `sources:[{label,url,locator}]`.

All fields are strings except lists/objects shown above. Baselines may be empty when no controlled comparator is verified. Use "全文核验" only after actual full-paper review; "官方材料" for official documents/selected tables; state abstract-only limits explicitly. Evidence and usefulness need not both be high. See review-and-memory.md for causal attribution.

## Abstract

For a retrieved paper use `{status:"translated", original:"complete source Abstract", translationZh:"complete faithful translation", sourceUrl:"https://…", sourceLabel:"paper and exact version / Abstract location", verifiedAt:"YYYY-MM-DD"}`. Optional `note` explains a source discrepancy or necessary translator note; keep it outside the translation. Original text can be expanded in the work dialog. The existing Chinese template uses the `*Zh` field names; for other reader languages, store the selected-language text and adapt the visible labels consistently.

Match the Abstract to the paper version being reported/reviewed. An older version must be explicitly identified if it is the only accessible source. Preserve numbers, units, uncertainty, scope, negative results and distinctions such as "will release" versus "released". Do not replace a translation with a short synopsis, add editorial criticism inside it, or silently fill broken source macros. Prefer a verified rendering of the same version and explain differences. Respect applicable source licences and attribution requirements.

For official announcements without a paper Abstract use `{status:"not_applicable", note:"what the cited source contains and why no Abstract is supplied", verifiedAt:"YYYY-MM-DD"}` after checking for companion papers. For a paper whose Abstract cannot be verified use `status:"unavailable"`, a reason and a source URL when known. Neither status permits a fabricated translation or an editorial summary labelled as Abstract.

The build joins `abstracts[workId]` into `reviews[workId].abstract` for all pages and append-only SQLite revisions. `catalog.summary` is the brief card description; `review.editorialSummaryZh` is editorial context; `review.abstract.translationZh` is the original-Abstract translation. The daily and statistics pages use the same `src/work-view.js` and `src/work-view.css` for cards and complete details. Statistics retains filters/charts while showing the shared cards; reviews must be reachable in the daily page's own dialog too.

SQLite's mutable `build_state` pointer selects the current content-addressed snapshot, including when a correction restores earlier content; revisions and snapshots themselves remain append-only. The checker and local API use this pointer rather than assuming the newest distinct snapshot is current.

When updating an older newspaper, rename the old paraphrase field `abstractZh` to `editorialSummaryZh` in current authoring JSON and add `data/abstracts.json`. Retrieve and translate available Abstracts; mark remaining access gaps explicitly. Adapt its existing build/templates in place to use the new fields and shared renderer, preserving local branding, empty-state handling, issue revisions and image-path checks. Never promote old paraphrases to translations, overwrite immutable issues or delete the database to migrate. Rebuilding appends review revisions containing the new records; existing snapshots remain intact. Display/metadata-only corrections do not create a new issue unless the edition's editorial content changes.

## Organization, profile, technology

Organization: `id, short, name, symbol, category, evidenceIds[], trendTitle, observed, hypothesis, caveat, confidence`.

Profile: `intro, focus[], strengths[], relevanceLevel, relevanceReason, trackingAdvice, representativeIds[], verifiedAt`. Representatives must be catalog works actually attributed to this organization. Relevance is to profile.readerFocus, not an institution ranking. One-paper groups cannot establish long-run strengths.

Technology: `id,name,kind,status,intro,problem,steps[],example,caveat,connections:[{workId,relation,note}],sources:[{label,url}],verifiedAt`. Distinguish source-confirmed adoption, related paradigm and speculative application. Do not make causal chains from coincident release dates.

## Journal

Statement: `id,topicId,createdOn,title,confidence,evidenceIds[],observation,interpretation,counterEvidence,reversal,change,externalSources:[{label,url,note}]`. Append versions sharing topicId; preserve all old entries. Existing editions' notes remain historical observations, not retrospective forecasts.

Forecast: `id,createdOn,deadline,probability` (0–1 exclusive), `claim,evidenceIds[],successRule,exclusions,failureRule`. Register before the outcome, freeze the conditions.

Evaluation: `id,forecastId,evaluatedOn,status,rationale,evidenceIds[],sourceCoverage`. status is pending/hit/miss/unresolved/retracted. A resolved hit/miss also requires `errorType,lesson,nextCheck`; supported errorType labels are in review-and-memory.md. Human/agent adjudication must verify the full prediction criteria; database temporal checks alone do not prove a substantive hit.

Research advice: `direction,opportunity,bottleneck,test`. This can describe individual researchers, small teams or enterprise trade-offs; it is not restricted to academic labs. Workflow: `title,text` entries describing the maintained memory loop.

## Build/serve

`python build.py` validates references and dates, appends SQLite history and emits index.html, technologies.html, statistics.html and trends.html (organization flow is in index.html). `python check_report.py` verifies generated artifacts and storage integrity. Core code uses only the standard library. Source authoring and builds require filesystem execution; do not claim they ran in a chat-only host.

`python serve.py` serves reading pages and read-only `/api/research` and `/api/history` on `127.0.0.1:8766`. No model backend, external publishing or scheduler is installed. The HTML contains offline data too. Preserve the complete newspaper directory for future accumulation; an isolated HTML copy is for reading, not continued memory.
