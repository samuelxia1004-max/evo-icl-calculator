"""Read the local clinical registry. Never export identifiers or free-text notes.

The column map is based on the independently audited September 2026 registry
map. Workbooks stay outside the repository. Rows exist in memory only.
"""
from pathlib import Path
import hashlib
import math
import re

import numpy as np
import pandas as pd
from openpyxl import load_workbook


def number(value):
    if isinstance(value, bool):
        return np.nan
    try:
        result = float(str(value).strip())
        return result if math.isfinite(result) else np.nan
    except (TypeError, ValueError):
        return np.nan


def numeric_endpoint(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def orientation(value):
    text = str(value or "").strip()
    if "垂直" in text:
        return 90.0, "explicit"
    if "水平" in text:
        return 0.0, "explicit"
    if "基准" in text or "斜轴" in text:
        return np.nan, "unresolved"
    text = text.split("切口")[-1]
    match = re.search(r"对准\s*(\d+(?:\.\d+)?)\s*°?", text)
    if match:
        return float(match.group(1)) % 180, "alignment"
    match = re.search(r"(\d{1,2})\s*(?:[-—－]|到)\s*(\d{1,2})\s*点", text)
    if match and (int(match[1]) - int(match[2])) % 12 == 6:
        return float((90 - 30 * int(match[1])) % 180), "clock"
    return np.nan, "unresolved"


def read_registry(path):
    path = Path(path)
    workbook = load_workbook(path, read_only=True, data_only=True)
    patients = []
    records = []
    conservative_name_groups = {}
    issues = {"invalid_stsh": 0, "invalid_stsv": 0, "invalid_lt": 0}
    for sheet in workbook:
        if sheet.title not in ("2022", "2023", "2024", "2025"):
            continue
        header = 3 if sheet.title == "2023" else 2
        shift = 0 if sheet.title in ("2022", "2023") else -2
        for row_index, row in enumerate(sheet.iter_rows(min_row=header + 2, values_only=True), header + 2):
            if not row[1]:
                continue
            # Names identify registry rows for inclusion only, and are never retained.
            if not any(numeric_endpoint(row[64 + shift + eye]) or numeric_endpoint(row[84 + shift + eye]) for eye in (0, 1)):
                continue
            group = len(patients)
            name_key = str(row[1]).strip()
            conservative_group = conservative_name_groups.setdefault(name_key, len(conservative_name_groups))
            patients.append({"group": group, "year": int(sheet.title)})
            for eye in (0, 1):
                if not numeric_endpoint(row[64 + shift + eye]) and not numeric_endpoint(row[84 + shift + eye]):
                    continue
                cols = {
                    "acd": 27 + eye, "lt": 49 + shift + eye,
                    "wtw": 37 + shift + eye, "acv": 29 + eye,
                    "aca": 31 + eye, "al": 45 + shift + eye,
                    "size": 51 + shift + eye,
                    "cyl": 12 + 3 * eye, "sphere": 11 + 3 * eye,
                    "early": 65 + shift + eye, "month1": 85 + shift + eye,
                    "month3": 97 + shift + eye, "month6": 109 + shift + eye,
                    "year1": 121 + shift + eye,
                }
                record = {key: number(row[col - 1]) for key, col in cols.items()}
                # Only native numeric outcome cells are treated as observations.
                for endpoint in ("early", "month1", "month3", "month6", "year1"):
                    if not numeric_endpoint(row[cols[endpoint] - 1]):
                        record[endpoint] = np.nan
                parts = re.split(r"[/／]", str(row[38 + shift + eye]))
                record["stsh"] = number(parts[0]) if parts else np.nan
                record["stsv"] = number(parts[1]) if len(parts) == 2 else np.nan
                for field, low, high in (("stsh", 9, 15), ("stsv", 10.5, 14), ("lt", 2.5, 5.5)):
                    if np.isfinite(record[field]) and not low <= record[field] <= high:
                        issues["invalid_" + field] += 1
                        record[field] = np.nan
                angle, method = orientation(row[72 + shift + eye])
                lens = str(row[52 + shift + 5 * eye] or "").lower()
                record.update(group=group, year=int(sheet.title), eye="OD" if eye == 0 else "OS",
                              conservative_group=conservative_group,
                              age=number(row[2]), sex=1 if row[3] == "男" else 0,
                              toric=1 if "toric" in lens else 0, angle=angle,
                              angle_method=method)
                radians = math.radians(angle) if np.isfinite(angle) else np.nan
                record["sin2"] = math.sin(radians) ** 2 if np.isfinite(radians) else np.nan
                record["sts_eff"] = 1 / math.sqrt(math.cos(radians) ** 2 / record["stsh"] ** 2 +
                                                   math.sin(radians) ** 2 / record["stsv"] ** 2)
                records.append(record)
    workbook.close()
    frame = pd.DataFrame(records)
    metadata = {
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "patient_records": len(patients), "eyes": len(frame),
        "conservative_same_name_groups": len(conservative_name_groups),
        "issues": issues,
        "orientation_methods": frame.angle_method.value_counts().to_dict(),
        "unknown_orientation": int(frame.angle.isna().sum()),
        "native_numeric_endpoint_rule": True,
        "year_eye_counts": {str(key): int(value) for key, value in frame.year.value_counts().sort_index().items()},
    }
    return frame, metadata
