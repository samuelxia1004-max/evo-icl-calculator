# Reanalysis protocol · 2026-10-13

Written before fitting the new models. This is a dated analysis plan, not a preregistration.

## Questions

1. Does an independently reconstructed, orientation-aware model of one-month vault improve patient-grouped out-of-sample error over a small anatomy-only model?
2. Do nonlinear models improve enough to justify their complexity in a small single-centre series?
3. Does matching the sulcus diameter to the recorded implantation meridian reduce the error of a modified published formula?
4. How much does an observed early/one-month measurement improve later-vault prediction?

## Data and cohort

- Read the original 2022–2025 registry locally, without modifying it.
- Preserve one worksheet row as one patient record; both eyes share a group. Repeated names are not used to merge records.
- Report endpoint-specific denominators: one-month modelling does not require an early measurement. The legacy early-vault cohort is reported separately.
- Use device-specific fields: Pentacam ACD/WTW/ACV/ACA; Jingxin900 LT/AL; UBM horizontal and vertical STS. Refractive cylinder and ordered toric-cylinder specifications are distinct.
- Known errors are flagged and set missing: STS-H outside 9–15 mm, STS-V outside 10.5–14 mm, LT outside 2.5–5.5 mm. No inferred decimal correction or column swapping.
- Implantation direction follows the audited parser: explicit horizontal/vertical first, absolute alignment angle or opposing clock-hours next; incision clock-hours and relative/unspecified axes do not establish implantation direction.

## Endpoints and predictors

Primary endpoint: measured one-month vault, μm. Primary analysis requires recorded orientation and complete ACD, size, Toric, LT, STS-H/V. A larger fold-imputed cohort is a sensitivity analysis.

Candidate predictor sets:

- Anatomy-only: ACD, size, Toric, LT, horizontal STS.
- Axis-matched: ACD, size, Toric, LT, effective STS.
- Orientation-aware: axis-matched set plus sin²θ. The term is jointly fitted; no residual correction is fitted on evaluation eyes.
- Extended: orientation-aware set plus WTW, ACV, ACA, AL, age and sex. These candidates use fold-only imputation.

Secondary endpoints: early vault and six-month vault. An observed early/one-month vault may be used only in explicitly postoperative follow-up models. Such models never appear as preoperative predictions.

## Validation and selection

- Keep 2025 patient records untouched as a temporal test. They are from the same centre and are not external validation.
- On 2022–2024 development records use repeated five-fold patient-grouped outer validation, with four-fold grouped inner tuning. Seed 20261013; three repetitions.
- Median imputation, scaling, tuning and interval calibration remain inside the training folds.
- Compare training-mean baseline, OLS, Ridge, constrained random forest, histogram gradient boosting and XGBoost when available. Use a bounded grid and mean absolute error for inner selection.
- Report MAE, RMSE, R², bias, ±200 μm and ±250 μm proportions, calibration slope, and patient-cluster bootstrap uncertainty. Model-difference intervals use paired patient resampling.
- Prefer a transparent linear model unless a nonlinear model improves development MAE by at least 5 μm and the paired patient bootstrap interval supports improvement. Report all prespecified candidates.
- The selected model fitted on 2022–2024 is the website model. Do not refit it using the temporal test and continue quoting the same temporal-test performance.
- Construct empirical intervals from inner grouped out-of-fold residuals and evaluate their coverage in the outer folds. Label them CV-derived prediction intervals, not distribution-free conformal guarantees.
- Probability displays are residual-model estimates, not independently calibrated event probabilities. Classification of rare extremes remains exploratory.

## Inference and sensitivity

- Patient-cluster inference for sulcus anisotropy, modified-formula errors and orientation-by-size interaction; observational associations do not prove a causal effect of changing size/direction.
- Recheck matched-angle versus binary H/V mapping, complete-case versus fold-imputed cohorts, missing cylinder versus historical zero coding, one-eye-per-patient and balanced patient weighting.
- Compare paired longitudinal follow-up only; do not turn changing available-case means into individual trajectories. Report follow-up missingness and baseline differences.

## Public outputs

Publish source code, coefficients/model objects, aggregate performance, aggregate bins, synthetic examples, source/cleaning provenance, model card and figures. Do not publish the workbook, free-text clinical notes, identifiers or reconstructed per-eye rows. Existing website data rows are replaced by aggregate summaries.

## Release and poster

Research demonstrator for scientific discussion. No clinical validation, no automated lens selection. Publication author/affiliation/ethics metadata and the exact Jiangsu meeting's submission requirements remain author-supplied. Produce a reviewable poster draft and a submission plan; do not submit to a society automatically.
