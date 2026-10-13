"""Reproducible ICL research reanalysis; aggregate outputs only.

Usage: python analysis/reanalyse.py --workbook /local/registry.xlsx
Run from the repository root. No network access, no edits to the workbook.
"""
import argparse
from collections import Counter
import importlib.metadata
import json
import math
from pathlib import Path
import time
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge, ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, GridSearchCV, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from threadpoolctl import threadpool_limits

from read_registry import read_registry

SEED = 20261013
REPEATS = 3
CORE = ["acd", "size", "toric", "lt", "sts_eff", "sin2"]
ANATOMY = ["acd", "size", "toric", "lt", "stsh"]
AXIS = ["acd", "size", "toric", "lt", "sts_eff"]
EXTENDED = CORE + ["wtw", "acv", "aca", "al", "age", "sex"]
LEGACY = {"intercept": -959.8149, "acd": 198.8547, "size": 189.3997,
          "toric": 45.9887, "sts_eff": -114.9899, "lt": -99.3845, "sin2": -58.9862}


def jdefault(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)


def save(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2, default=jdefault, allow_nan=False) + "\n")


def basic(values):
    array = np.asarray(values, float)
    array = array[np.isfinite(array)]
    return {"n": len(array), "mean": float(array.mean()), "sd": float(array.std(ddof=1)),
            "median": float(np.median(array)), "q25": float(np.quantile(array, .25)),
            "q75": float(np.quantile(array, .75))} if len(array) else {"n": 0}


def metrics(y, prediction):
    y, prediction = np.asarray(y), np.asarray(prediction)
    error = prediction - y
    slope, intercept = np.polyfit(prediction, y, 1) if np.std(prediction) > 1e-8 else (np.nan, np.nan)
    return {"n": len(y), "mae": float(abs(error).mean()),
            "rmse": float(np.sqrt((error ** 2).mean())), "r2": float(r2_score(y, prediction)),
            "bias": float(error.mean()), "within200": float((abs(error) <= 200).mean()),
            "within250": float((abs(error) <= 250).mean()),
            "calibration_slope": float(slope) if np.isfinite(slope) else None,
            "calibration_intercept": float(intercept) if np.isfinite(intercept) else None}


def group_weights(groups, repeats=3000):
    codes, unique = pd.factorize(np.asarray(groups))
    rng = np.random.default_rng(SEED)
    counts = rng.multinomial(len(unique), np.ones(len(unique)) / len(unique), size=repeats)
    return codes, counts


def clustered_ci(values, groups):
    values = np.asarray(values, float)
    codes, weights = group_weights(groups)
    sums = np.bincount(codes, weights=values)
    sizes = np.bincount(codes)
    estimates = (weights @ sums) / (weights @ sizes)
    return [float(x) for x in np.quantile(estimates, [.025, .975])]


def cluster_difference(y, indicator, groups):
    codes, weights = group_weights(groups)
    y, indicator = np.asarray(y), np.asarray(indicator)
    arrays = []
    for group in (False, True):
        mask = indicator == group
        sums = np.bincount(codes[mask], weights=y[mask], minlength=weights.shape[1])
        counts = np.bincount(codes[mask], minlength=weights.shape[1])
        with np.errstate(divide="ignore", invalid="ignore"):
            arrays.append((weights @ sums) / (weights @ counts))
    differences = arrays[1] - arrays[0]
    differences = differences[np.isfinite(differences)]
    return {"difference": float(y[indicator].mean() - y[~indicator].mean()),
            "ci95": np.quantile(differences, [.025, .975]).tolist(), "bootstrap": 3000}


def pipeline(model):
    return Pipeline([("impute", SimpleImputer(strategy="median")),
                     ("scale", StandardScaler()), ("model", model)])


def candidates():
    output = {
        "mean": (CORE, pipeline(DummyRegressor()), {}),
        "ols_anatomy": (ANATOMY, pipeline(LinearRegression()), {}),
        "ols_axis": (AXIS, pipeline(LinearRegression()), {}),
        "ridge_orientation": (CORE, pipeline(Ridge()), {"model__alpha": [.1, 1, 10, 100]}),
        "ridge_extended": (EXTENDED, pipeline(Ridge()), {"model__alpha": [1, 10, 100]}),
        "elastic_net": (EXTENDED, pipeline(ElasticNet(max_iter=5000)),
                        {"model__alpha": [.5, 2, 10], "model__l1_ratio": [.2, .8]}),
        "random_forest": (EXTENDED, pipeline(RandomForestRegressor(n_estimators=120, random_state=SEED, n_jobs=1)),
                          {"model__max_depth": [4, 8], "model__min_samples_leaf": [5, 12]}),
        "hist_gradient": (EXTENDED, pipeline(HistGradientBoostingRegressor(max_iter=100, learning_rate=.04,
                              early_stopping=False, random_state=SEED)),
                          {"model__max_leaf_nodes": [5, 9], "model__l2_regularization": [10, 100]}),
        "gradient_boost": (EXTENDED, pipeline(GradientBoostingRegressor(n_estimators=100, learning_rate=.035,
                              loss="huber", random_state=SEED)),
                           {"model__max_depth": [2, 3], "model__min_samples_leaf": [8, 16]}),
        "svr": (EXTENDED, pipeline(SVR()), {"model__C": [30, 100], "model__epsilon": [20, 50]}),
    }
    try:
        from xgboost import XGBRegressor
        output["xgboost"] = (EXTENDED, pipeline(XGBRegressor(n_estimators=120, learning_rate=.035,
                 subsample=.85, colsample_bytree=.9, random_state=SEED, n_jobs=1)),
                 {"model__max_depth": [2, 3], "model__reg_lambda": [10, 100]})
    except Exception as exc:
        print("XGBoost unavailable:", type(exc).__name__, flush=True)
    return output


def splits(groups, n_splits=5, seed=SEED):
    return list(GroupKFold(n_splits=n_splits, shuffle=True, random_state=seed).split(np.zeros(len(groups)), groups=groups))


def fit_tuned(frame, endpoint, specification, seed):
    features, estimator, grid = specification
    cv = splits(frame.group.to_numpy(), n_splits=4, seed=seed)
    if not grid:
        fitted = clone(estimator).fit(frame[features], frame[endpoint])
        return fitted, {}, cv
    search = GridSearchCV(clone(estimator), grid, cv=cv, scoring="neg_mean_absolute_error", n_jobs=1)
    search.fit(frame[features], frame[endpoint])
    return search.best_estimator_, search.best_params_, cv


def grouped_validation(frame, endpoint, specifications, repeats=REPEATS, intervals=False):
    predictions = {key: np.zeros((repeats, len(frame))) for key in specifications}
    intervals_out = {key: np.zeros((repeats, len(frame), 4)) for key in specifications}
    selected = {key: [] for key in specifications}
    frame = frame.reset_index(drop=True)
    for repeat in range(repeats):
        for fold, (train_index, test_index) in enumerate(splits(frame.group, seed=SEED + repeat)):
            train, test = frame.iloc[train_index], frame.iloc[test_index]
            assert set(train.group).isdisjoint(test.group)
            for key, spec in specifications.items():
                started = time.time()
                fitted, params, inner = fit_tuned(train, endpoint, spec, SEED + repeat * 10 + fold)
                selected[key].append(params)
                yhat = fitted.predict(test[spec[0]])
                predictions[key][repeat, test_index] = yhat
                if intervals and key in ("ridge_orientation", "ridge_extended", "ols_axis", "ols_anatomy"):
                    inner_prediction = cross_val_predict(clone(fitted), train[spec[0]], train[endpoint], cv=inner, n_jobs=1)
                    residual = train[endpoint].to_numpy() - inner_prediction
                    quantiles = np.quantile(residual, [.1, .9, .025, .975])
                    intervals_out[key][repeat, test_index] = yhat[:, None] + quantiles
                print(f"{endpoint} repeat {repeat + 1}/{repeats} fold {fold + 1}/5 {key} {time.time()-started:.1f}s", flush=True)
    report = {}
    target = frame[endpoint].to_numpy()
    for key, prediction in predictions.items():
        repeated_metrics = [metrics(target, p) for p in prediction]
        # Average losses, never the predictions, for the repeated-CV primary metrics.
        summary = {k: (float(np.mean([m[k] for m in repeated_metrics])) if repeated_metrics[0][k] is not None else None)
                   for k in repeated_metrics[0]}
        summary["n"] = len(target)
        summary["patients"] = int(frame.group.nunique())
        absolute_error = np.mean(abs(prediction - target), axis=0)
        summary["mae_ci95"] = clustered_ci(absolute_error, frame.group)
        summary["repeat_metrics"] = repeated_metrics
        summary["selected_parameters"] = dict(Counter(json.dumps(p, sort_keys=True) for p in selected[key]))
        summary["validation"] = "3 x 5 outer patient-grouped folds; 4 inner grouped folds" if repeats == 3 else "5 patient-grouped folds"
        bands = intervals_out[key]
        if intervals and np.any(bands):
            summary["coverage80"] = float(np.mean((target >= bands[:, :, 0]) & (target <= bands[:, :, 1])))
            summary["coverage95"] = float(np.mean((target >= bands[:, :, 2]) & (target <= bands[:, :, 3])))
            summary["interval_width80"] = float(np.mean(bands[:, :, 1] - bands[:, :, 0]))
        report[key] = summary
    return report, predictions


def linear_export(fitted, features):
    imputer, scaler, model = (fitted.named_steps[k] for k in ("impute", "scale", "model"))
    coefficients = np.asarray(model.coef_) / scaler.scale_
    intercept = float(model.intercept_ - np.dot(coefficients, scaler.mean_))
    return {"type": "linear", "features": features, "intercept": intercept,
            "coefficients": dict(zip(features, coefficients.tolist())),
            "imputation": dict(zip(features, imputer.statistics_.tolist()))}


def aggregate_bins(y, predictions):
    edges = np.linspace(0, 1000, 13)
    means = []
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (predictions >= low) & (predictions < high)
        if mask.sum() >= 5:
            means.append({"predicted": float(predictions[mask].mean()), "observed": float(y[mask].mean()),
                          "n": int(mask.sum()), "sd": float(y[mask].std(ddof=1))})
    return means


def inferential_audit(frame):
    result = {}
    early = frame[frame.early.notna()].copy()
    orientation = early.dropna(subset=["angle"])
    result["early_orientation"] = cluster_difference(orientation.early.to_numpy(),
               ((orientation.angle > 45) & (orientation.angle < 135)).to_numpy(), orientation.group)
    result["early_orientation"]["counts"] = {"horizontal": int(((orientation.angle <= 45) | (orientation.angle >= 135)).sum()),
                                               "vertical": int(((orientation.angle > 45) & (orientation.angle < 135)).sum())}
    sulcus = frame.dropna(subset=["stsh", "stsv"])
    difference = sulcus.stsv - sulcus.stsh
    result["sulcus_anisotropy"] = {"n": len(sulcus), "difference": float(difference.mean()),
                                  "ci95": clustered_ci(difference, sulcus.group)}
    matched = early.dropna(subset=["angle", "stsh", "stsv", "size"]).copy()
    predictions = {
        "KS_horizontal_STS_proxy": 660.9 * (matched["size"] - matched.stsh) + 86.6,
        "KS_binary_STS_proxy": 660.9 * (matched["size"] - np.where((matched.angle > 45) & (matched.angle < 135), matched.stsv, matched.stsh)) + 86.6,
        "KS_ellipse_STS_proxy": 660.9 * (matched["size"] - matched.sts_eff) + 86.6,
        "Zhu2026_horizontal": -2286.216 - 164.416 * matched.stsh + 375.487 * matched["size"],
    }
    result["formula_comparison_common_cohort"] = {name: metrics(matched.early, pred) for name, pred in predictions.items()}
    improvement = abs(predictions["KS_horizontal_STS_proxy"] - matched.early) - abs(predictions["KS_ellipse_STS_proxy"] - matched.early)
    result["KS_axis_improvement"] = {"n": len(matched), "mae_reduction": float(improvement.mean()),
                                    "ci95": clustered_ci(improvement, matched.group),
                                    "note": "ATA was not measured. These are modified STS-proxy implementations, not original KS validation."}
    for endpoint in ("early", "month1"):
        sample = frame.dropna(subset=[endpoint, "acd", "size", "cyl", "sin2"]).copy()
        import statsmodels.api as sm
        centered = sample["size"] - 12.6
        design = pd.DataFrame({"acd": sample.acd, "size_centered": centered,
                               "cyl": sample.cyl, "sin2": sample.sin2,
                               "size_x_sin2": centered * sample.sin2})
        fit = sm.OLS(sample[endpoint], sm.add_constant(design)).fit(cov_type="cluster", cov_kwds={"groups": sample.group})
        index = list(fit.params.index).index("size_x_sin2")
        result[endpoint + "_interaction_complete_cylinder"] = {
            "n": len(sample), "patients": int(sample.group.nunique()),
            "beta": float(fit.params.iloc[index]), "ci95": fit.conf_int().iloc[index].tolist(),
            "p": float(fit.pvalues.iloc[index]), "note": "Exploratory, complete observed refractive cylinder; no zero substitution."}
    return result


def followup(frame):
    summary = {}
    for endpoint in ("month1", "month3", "month6", "year1"):
        paired = frame.dropna(subset=["early", endpoint])
        summary[endpoint] = {"n": len(paired), "patients": int(paired.group.nunique()),
              "early": basic(paired.early), "followup": basic(paired[endpoint]),
              "change": basic(paired[endpoint] - paired.early),
              "change_ci95": clustered_ci(paired[endpoint] - paired.early, paired.group)}
    # Compare follow-up models on exactly the same eyes, with patient separation.
    common = frame.dropna(subset=CORE + ["early", "month1", "month6"]).copy()
    specs = {"preoperative_only": (CORE, pipeline(Ridge()), {"model__alpha": [1, 10, 100]}),
             "plus_observed_early": (CORE + ["early"], pipeline(Ridge()), {"model__alpha": [1, 10, 100]}),
             "plus_observed_month1": (CORE + ["month1"], pipeline(Ridge()), {"model__alpha": [1, 10, 100]})}
    report, preds = grouped_validation(common, "month6", specs, repeats=1)
    summary["six_month_comparison"] = report
    summary["six_month_selection"] = "Postoperative models are a separate research question; grouped CV on the common paired cohort, not external validation."
    fitted, params, _ = fit_tuned(common, "month6", specs["plus_observed_month1"], SEED)
    exported = linear_export(fitted, specs["plus_observed_month1"][0])
    exported.update(endpoint="month6", selected_parameters=params, validation=report["plus_observed_month1"],
                    residual_quantiles=np.quantile(common.month6.to_numpy() - preds["plus_observed_month1"][0], [.1, .9, .025, .975]).tolist(),
                    status="exploratory_refit_on_all_paired_eyes_no_temporal_test")
    return summary, exported


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--outdir", default="research")
    args = parser.parse_args()
    output = Path(args.outdir)
    frame, source = read_registry(args.workbook)
    specs = candidates()
    cohort = {"source": source, "endpoints": {endpoint: basic(frame[endpoint]) for endpoint in ("early", "month1", "month3", "month6", "year1")},
              "missingness": {key: int(frame[key].isna().sum()) for key in EXTENDED + ["cyl"]},
              "complete_core_month1": int(frame.dropna(subset=CORE + ["month1"]).shape[0])}
    eligible = frame.dropna(subset=CORE + ["month1"]).copy()
    dev = eligible[eligible.year < 2025].reset_index(drop=True)
    temporal = eligible[eligible.year == 2025].reset_index(drop=True)
    assert set(dev.group).isdisjoint(temporal.group)
    cohort["development"] = {"eyes": len(dev), "patients": int(dev.group.nunique()), "years": [2022, 2023, 2024]}
    cohort["temporal_test"] = {"eyes": len(temporal), "patients": int(temporal.group.nunique()), "year": 2025}
    save(output / "cohort.json", cohort)
    print("Cohort", json.dumps(cohort["development"]), "; temporal", json.dumps(cohort["temporal_test"]), flush=True)
    report, preds = grouped_validation(dev, "month1", specs, intervals=True)
    linear_names = [name for name in report if name.startswith("ols_") or name.startswith("ridge_") or name == "elastic_net"]
    linear_best = min(linear_names, key=lambda k: report[k]["mae"])
    nonlinear_names = [name for name in report if name not in linear_names and name != "mean"]
    nonlinear_best = min(nonlinear_names, key=lambda k: report[k]["mae"])
    improvement = np.mean(abs(preds[linear_best] - dev.month1.to_numpy()) - abs(preds[nonlinear_best] - dev.month1.to_numpy()), axis=0)
    improvement_ci = clustered_ci(improvement, dev.group)
    choose_nonlinear = improvement.mean() >= 5 and improvement_ci[0] > 0
    chosen = nonlinear_best if choose_nonlinear else linear_best
    selection = {"linear_best": linear_best, "nonlinear_best": nonlinear_best, "nonlinear_mae_improvement": float(improvement.mean()),
                 "paired_ci95": improvement_ci, "chosen": chosen, "rule": "Nonlinear improvement >=5 μm with positive paired patient bootstrap CI; otherwise best transparent linear."}
    paired_improvements = {}
    for reference in ("ols_anatomy", "ols_axis", "mean"):
        differences = np.mean(abs(preds[reference] - dev.month1.to_numpy()) - abs(preds[linear_best] - dev.month1.to_numpy()), axis=0)
        paired_improvements[reference] = {"mae_reduction": float(differences.mean()), "ci95": clustered_ci(differences, dev.group)}
    selection["paired_linear_improvements"] = paired_improvements
    print("SELECTION", json.dumps(selection), flush=True)
    # The exported browser model must be a transparent linear model in this release.
    if choose_nonlinear:
        selection["browser_default"] = linear_best
        selection["browser_note"] = "Nonlinear research candidate retained; transparent linear model is the deployable research demonstrator."
    else:
        selection["browser_default"] = chosen
    deploy = selection["browser_default"]
    features = specs[deploy][0]
    fitted, params, inner = fit_tuned(dev, "month1", specs[deploy], SEED)
    exported = linear_export(fitted, features)
    exported.update(id="icl-20261013-" + deploy, version="3.0.0", built="2026-10-13", endpoint="month1",
                    training=cohort["development"], selected_parameters=params,
                    research_validation=report[deploy], temporal_test=None)
    temporal_report = {}
    # Evaluation is performed only after all model selection has been completed.
    for name in ("mean", "ols_anatomy", "ols_axis", deploy, nonlinear_best):
        if name in temporal_report:
            continue
        model, _, _ = fit_tuned(dev, "month1", specs[name], SEED)
        predictions = model.predict(temporal[specs[name][0]])
        metric = metrics(temporal.month1, predictions)
        metric["mae_ci95"] = clustered_ci(abs(predictions - temporal.month1.to_numpy()), temporal.group)
        temporal_report[name] = metric
    full_inner_pred = cross_val_predict(clone(fitted), dev[features], dev.month1, cv=inner, n_jobs=1)
    residual = dev.month1.to_numpy() - full_inner_pred
    quantiles = np.quantile(residual, [.1, .9, .025, .975])
    exported["residual_quantiles"] = quantiles.tolist()
    exported["residual_sd"] = float(residual.std(ddof=1))
    # A histogram, never patient residual rows, powers the browser empirical CDF.
    edges = np.arange(-800, 821, 20)
    counts, edges = np.histogram(residual, bins=edges)
    exported["residual_histogram"] = {"edges": edges.tolist(), "counts": counts.tolist(), "tail_low": int((residual < edges[0]).sum()), "tail_high": int((residual >= edges[-1]).sum())}
    for key in ("acd", "lt", "stsh", "stsv", "wtw", "size", "angle"):
        values = dev[key].dropna().to_numpy()
        exported.setdefault("reference", {})[key] = {"quantiles": np.quantile(values, np.linspace(0, 1, 21)).tolist(), "mean": float(values.mean()), "sd": float(values.std(ddof=1))}
    vector = dev[CORE].to_numpy()
    exported["distance"] = {"features": CORE, "mean": vector.mean(axis=0).tolist(), "inverse_covariance": np.linalg.pinv(np.cov(vector, rowvar=False)).tolist(),
                             "note": "Exploratory distance indicator; no validated A–D clinical reliability grades."}
    target_temporal = fitted.predict(temporal[features])
    temporal_default = temporal_report[deploy]
    temporal_default["coverage80"] = float(((temporal.month1 >= target_temporal + quantiles[0]) & (temporal.month1 <= target_temporal + quantiles[1])).mean())
    temporal_default["coverage95"] = float(((temporal.month1 >= target_temporal + quantiles[2]) & (temporal.month1 <= target_temporal + quantiles[3])).mean())
    exported["temporal_test"] = temporal_default
    exported["validation_status"] = "Patient-grouped internal validation + small same-centre temporal test; no independent external validation."
    # Bootstrap coefficient uncertainty based only on development patients.
    rng = np.random.default_rng(SEED)
    groups = dev.group.unique()
    bootstrap_coefficients = []
    for _ in range(300):
        drawn = rng.choice(groups, len(groups), replace=True)
        index = np.concatenate([np.flatnonzero(dev.group.to_numpy() == group) for group in drawn])
        model = clone(fitted).fit(dev.iloc[index][features], dev.iloc[index].month1)
        result = linear_export(model, features)
        bootstrap_coefficients.append([result["intercept"]] + [result["coefficients"][f] for f in features])
    exported["bootstrap_coefficients"] = bootstrap_coefficients
    # WTW->STS mapping fitted on development eyes only, for explicitly flagged research fallback.
    fallback = {}
    for key in ("stsh", "stsv"):
        sample = dev.dropna(subset=[key, "wtw"])
        slope, intercept = np.polyfit(sample.wtw, sample[key], 1)
        fallback[key] = {"intercept": float(intercept), "slope": float(slope), "n": len(sample),
                         "mae_apparent": float(abs(sample[key] - (intercept + slope * sample.wtw)).mean())}
    exported["wtw_fallback"] = fallback
    y = dev.month1.to_numpy()
    # Complete-case cylinder analysis isolates the old missingness ambiguity.
    sensitivity = {}
    imputed = frame[(frame.month1.notna()) & (frame.angle.notna()) & (frame.year < 2025)].copy()
    sensitive_specs = {"orientation_fold_imputed": specs["ridge_orientation"]}
    sensitive_report, _ = grouped_validation(imputed, "month1", sensitive_specs, repeats=1)
    sensitivity["fold_imputed_cohort"] = sensitive_report
    first_eye = dev.groupby("group", sort=False).head(1)
    one_report, _ = grouped_validation(first_eye, "month1", {deploy: specs[deploy]}, repeats=1)
    sensitivity["one_eye_per_patient"] = one_report
    conservative = dev.copy()
    conservative["group"] = conservative.conservative_group
    conservative_report, _ = grouped_validation(conservative, "month1", {deploy: specs[deploy]}, repeats=1)
    sensitivity["conservative_same_name_grouping"] = conservative_report
    sensitivity["identity_note"] = "Primary groups are worksheet patient records. Same-name records are conservatively linked only in this sensitivity; actual identity requires clinical identifiers."
    direct_axis = dev[dev.angle_method.isin(["explicit", "clock"])]
    direct_report, _ = grouped_validation(direct_axis, "month1", {deploy: specs[deploy]}, repeats=1)
    sensitivity["explicit_or_clock_axis_only"] = direct_report
    sensitivity["axis_interpretation_note"] = "Alignment angles may be a toric optical axis rather than physical lens long-axis. The clinical team must verify correspondence; the sensitivity excludes those notes."
    cylinder = frame.dropna(subset=["early", "acd", "size", "cyl", "sin2"])
    cyl_specs = {"early_four_variable_observed_cylinder": (["acd", "size", "cyl", "sin2"], pipeline(LinearRegression()), {})}
    cyl_report, _ = grouped_validation(cylinder[cylinder.year < 2025], "early", cyl_specs, repeats=1)
    sensitivity["early_formula_observed_cylinder"] = cyl_report
    # Legacy values are locked historical comparators, not independent external validation.
    legacy_prediction = np.full(len(dev), LEGACY["intercept"])
    for key in CORE:
        legacy_prediction += LEGACY[key] * dev[key].to_numpy()
    sensitivity["legacy_locked_apparent"] = metrics(y, legacy_prediction)
    sensitivity["legacy_note"] = "Coefficient provenance includes these development data, so this is historical/apparent scoring, never an independent model performance comparison."
    inference = inferential_audit(frame)
    longitudinal, follow_model = followup(frame)
    environment = {key: importlib.metadata.version(key) for key in ("numpy", "pandas", "scipy", "scikit-learn", "statsmodels", "openpyxl", "matplotlib")}
    results = {"date": "2026-10-13", "seed": SEED, "cohort": cohort, "models": report, "selection": selection,
               "temporal": temporal_report, "sensitivity": sensitivity, "inference": inference, "longitudinal": longitudinal,
               "environment": environment, "ci_note": "Patient bootstrap intervals conditional on fixed out-of-fold predictions; do not cover the entire model-selection procedure."}
    calibration = aggregate_bins(y, preds[deploy][0])
    results["calibration_bins"] = calibration
    results["residual_histogram"] = exported["residual_histogram"]
    save(output / "results.json", results)
    save("assets/model.json", exported)
    save("assets/followup-model.json", follow_model)
    save("assets/research.json", results)
    pd.DataFrame({key: {m: value for m, value in report[key].items() if m in ("mae", "rmse", "r2", "bias", "within200", "within250", "n", "patients", "coverage80", "coverage95")} for key in report}).T.to_csv(output / "model-comparison.csv", index_label="model")
    print("DONE", deploy, "CV MAE", report[deploy]["mae"], "temporal MAE", temporal_default["mae"], flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        main()
