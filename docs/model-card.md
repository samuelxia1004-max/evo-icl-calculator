# Model card · EVO ICL Vault Lab 3.0

Status: research demonstrator. Analysis 2026-10-13; interface release 2026-10-14.

Purpose: scientific discussion of cohort-level modelling and synthetic anatomical scenarios. Not for patient care or live clinical use. It does not diagnose, determine suitability, select lens size/orientation or recommend treatment.

Endpoint: one-month measured postoperative vault, μm. Population: a single-centre retrospective 2022–2025 registry. Primary training: 341 complete-core-parameter eyes / 173 patient records from 2022–2024. Separate temporal test: 29 eyes / 15 records from 2025. Group identity is based on worksheet records and requires clinician verification for ambiguous duplicate identities.

Model: standardized Ridge, α=10; ACD, ICL size, Toric, LT, axis-matched STS and sin²θ jointly fitted. Device-specific column mapping and full-precision coefficients are in the analysis code and `assets/model.json`. Unknown or invalid inputs cause calculation to stop. WTW fallback is exploratory and labelled; its intervals have not been separately validated.

Internal evaluation: repeated nested patient-grouped outer 3×5 folds / inner 4 folds. MAE 110.3 μm (patient-bootstrap CI 99.3–121.6), R² 0.303. Temporal: MAE 149.7 μm (108.7–187.6), calibration slope 1.70. No independent-centre external validation or prospective human-factors/impact study.

Uncertainty: empirical inner-OOF residual intervals evaluated in outer folds; no distribution-free conformal guarantee. Temporal 80%/95% coverage 65.5%/96.6%. Default 95%; no temporal-test recalibration. Bootstrap coefficient bands estimate parameter variation, not individual error. Range probabilities derive from a residual histogram and lack independent event-probability calibration.

Interpretation: changes of size/angle represent conditional associations in nonrandom observational data. Recorded toric alignment may not represent physical lens long-axis, pending surgical-record confirmation. Oblique-angle scenarios are geometric interpolation. Cohort-tail markers are descriptive, not validated clinical reliability grades.

Separate six-month model: exploratory paired cohort (281 eyes / 142 records), requires an observed month-one measurement. Internal grouped CV MAE 60.5 μm, R² 0.746. Refitted on all paired eyes; no temporal/external test. Never used as a preoperative prediction.

Missing domains: CLR/STSL, independent centres, validated functional rehabilitation outcomes. Patient-specific application and clinical deployment require a separately authorized, qualified process; software tests are not evidence of clinical fitness.

Privacy/release: no raw Excel, identifiers, clinical narratives or per-eye source rows in the new public web release. Public outputs include code, source hash, models, aggregates, histograms, figure files and synthetic demonstrations. Parameter sharing is explicit and requires confirmation that the inputs are synthetic. OCR/PDF runs locally but downloads engines/language packs from a CDN. In-memory session only; no localStorage/sessionStorage.

Human review: institution, authorship, ethics/data authority and clinical interpretation not supplied to this task. Poster is a draft, not a submitted/accepted publication. Numerical/software verification does not resolve these items.

Changes: replaces v2.0.2 locked coefficients plus an in-sample residual adjustment; recalculates residuals for the jointly fitted model; defaults to 95%; removes embedded individual rows; adds aggregate validation evidence and a separate longitudinal experiment. For rollback, restore the previous Git revision rather than mixing old coefficients with new intervals.
