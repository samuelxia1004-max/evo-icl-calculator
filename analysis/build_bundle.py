"""Bundle public aggregate artifacts for a network-free static demo."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = {"model": json.loads((root / "assets/model.json").read_text()),
        "research": json.loads((root / "assets/research.json").read_text()),
        "followup": json.loads((root / "assets/followup-model.json").read_text())}
(root / "assets/bundle.js").write_text("/* Aggregate research artifacts; no individual patient rows. */\nwindow.VaultData=" +
    json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("</", "<\\/") + ";\n")
print("Built", root / "assets/bundle.js")
