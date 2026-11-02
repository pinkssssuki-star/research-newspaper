# Comparative review and research memory

## Fair review

Translate the paper's original Abstract in full, with a versioned source and the original text available for comparison. Keep author claims, original-Abstract translation, brief card description and editorial explanation distinct. Check official release pages for companion papers; explicitly mark missing or inaccessible Abstracts. Never pass a paraphrase off as the paper's Abstract. See the data contract for fields and legacy migration.

Separate established observation, author-reported result and editorial inference. State the practical problem and the users/tasks for which the contribution helps. Do not assign a universal usefulness score.

For each meaningful comparator record its exact version, task/split, metric and direction, input/tool privileges, training/adaptation budget, evaluation budget, sample count and source table/section when disclosed. Report “not disclosed/not verified” instead of completing missing information from intuition. Product announcements may have no controlled baselines; empty baseline lists are valid.

Record which conditions explain differences: data scale/quality/diversity, domain adaptation, pretrained foundation, architecture/objective, task decomposition/tooling, oracle information, simulation/reality gap, selected tasks, latency/compute, resets and evaluation metric. Extra data or computation is not automatically an unfair trick. Do not seek faults for their own sake.

Explain why the strongest relevant comparator trails, ties or wins, including negative results and trade-offs. Matched ablations support local causality; a cross-paper leaderboard usually cannot separate architecture, data and budget. Never fabricate percentage attribution. Distinguish improvements in success, safety, cost and deployability. A safety method can be useful while slower or less successful; a dataset can help without a new architecture.

Reading depth must reflect actual access: full-paper review, official material/selected tables, or abstract/method-only. None means independent reproduction. Quote sparingly, respect source licences and cite original sources near claims.

Put this review in the daily work-detail dialog along with the Abstract translation and source text. Reuse that card/detail component in statistics, including figures, sources and organization/technology entry points. Statistics filters and charts are additional navigation, not the sole place where readers can assess an individual work. Report practical usefulness and the dominant plausible reason for baseline differences without inventing a trick count, numerical attribution or unfairness unsupported by controls.

## Trends versus forecasts

For a trend statement save topicId, immutable version ID, date, observations, interpretation, confidence, supporting work IDs, counterevidence/alternative explanations, reversal condition and change from the prior version. External organizational signals may be cited with URLs but should not inflate paper counts. Hiring is not a deployed model. Curated sample proportions are not field-wide market shares.

A forecast is registered **before** outcomes: ID, createdOn, deadline, subjective probability, claim, eligible evidence, success rule, exclusions and failure/unresolved rule. Define distinct team/source clusters and what counts as a genuinely new result. Historical editorial notes are not retroactive predictions. Prefer a few useful falsifiable forecasts over many obvious or vague claims.

Every daily invocation checks pending and overdue predictions. Append an evaluation with ID, forecastId, evaluatedOn, status, rationale, evidenceIds and sourceCoverage. Status is pending/hit/miss/unresolved/retracted. A miss cannot precede the deadline; a hit must cite post-registration events actually meeting all rules. Search absence alone is not failure without adequate coverage. If eligibility cannot be verified, use unresolved. Source date precision matters at deadline boundaries.

For hit/miss also record errorType, lesson and nextCheck. Supported errorType values: 未发现明显误判, 遗漏信息, 样本偏差, 重复证据, 能力产品混用, 归因混杂, 过度外推, 其他. Never conceal withdrawn or unresolved forecasts. Rate only adjudicated hit/miss events; report the denominator and unresolved coverage. Brier is mean `(probability - outcome)^2`, lower is better. A small selected sample does not establish calibrated forecasting skill.

Revise the research advice after identifying why earlier reasoning failed: missed sources, duplicate evidence, inappropriate causal attribution, benchmark selection, over-extrapolation or changed resource assumptions. Save that lesson and explicitly consult it on the next run. Small teams' opportunities should depend on available data, compute, equipment, engineering and time; do not declare entire research directions impossible merely because large companies participate.
