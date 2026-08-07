"""Render the measured results as charts (`M9-07b`).

Guidelines §9.3 names the visualisation types it wants — "Bar charts for comparisons, Line
charts for trends, Scatter plots for correlations, Heatmaps for parameter sensitivity, Box
plots for distributions" — and `M9-07b` adds the acceptance condition: "clear axes, legend,
caption".

    uv run python scripts/run_experiments.py     # measure
    uv run python scripts/render_charts.py       # draw

Every chart reads `results/*.json`, which `run_experiments.py` produced by refereeing real
matches. This script computes nothing and invents nothing; if a number is wrong here it is
wrong in the measurement, which is the separation that makes the pictures trustworthy.

SVG, so the output is resolution-independent by construction rather than by a DPI setting,
and so the charts can be asserted in tests rather than merely eyeballed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p2p_cop_agent.analysis import (  # noqa: E402
    Series,
    Summary,
    bar_chart,
    box_plot,
    heatmap,
    line_chart,
)

RESULTS = ROOT / "results"
ASSETS = ROOT / "assets"


def load(name: str) -> dict:
    return json.loads((RESULTS / f"{name}.json").read_text("utf-8"))


def _summary(block: dict) -> Summary:
    return Summary(runs=block["runs"], mean=block["mean"], stdev=block["stdev"],
                   minimum=block["min"], q1=block["q1"], median=block["median"],
                   q3=block["q3"], maximum=block["max"])


def strategy_charts() -> dict[str, str]:
    data = load("strategy_arms")
    arms = ("blind", "belief", "oracle")
    runs = data["runs_per_arm"]
    paired = data["paired_belief_vs_blind"]
    return {
        "chart-strategy-comparison.svg": bar_chart(
            title="Cop strategy arms: capture rate and mean score",
            caption=f"{runs} paired seeds per arm; each seed gives every arm the identical "
                    f"Thief trajectory. Belief closes "
                    f"{data['belief_share_of_available_gap'] * 100:.1f}% of the blind-to-oracle gap.",
            x_label="strategy arm", y_label="value",
            categories=list(arms),
            series=[
                Series("capture rate", [data[a]["capture_rate"] for a in arms]),
                Series("mean cop score / 20", [data[a]["cop_score"]["mean"] / 20 for a in arms]),
            ]),
        "chart-strategy-distribution.svg": box_plot(
            title="Cop score distribution by strategy arm",
            caption=f"Five-number summary over {runs} seeds. Belief wins {paired['wins']} of "
                    f"{paired['pairs']} pairs and loses {paired['losses']}.",
            x_label="strategy arm", y_label="cop score (max 20)",
            labels=list(arms),
            summaries=[_summary(data[a]["cop_score"]) for a in arms]),
        "chart-turns-distribution.svg": box_plot(
            title="Turns to resolution by strategy arm",
            caption=f"Lower is a faster capture. {runs} seeds per arm; the blind arm's "
                    f"upper whisker is the survival horizon, not a capture.",
            x_label="strategy arm", y_label="turns",
            labels=list(arms),
            summaries=[_summary(data[a]["turns"]) for a in arms]),
    }


def sweep_chart(name: str, title: str, note: str) -> tuple[str, str]:
    data = load(name)
    values = [point["value"] for point in data["points"]]
    caption = (f"{data['runs_per_point']} runs per point · Appendix F status "
               f"{data['appendix_f_status']}, minimum {data['minimum']} · {note}")
    return f"chart-{name.replace('_', '-')}.svg", line_chart(
        title=title, caption=caption,
        x_label=data["parameter"], y_label="value",
        x_values=values,
        series=[
            Series("capture rate", [p["capture_rate"] for p in data["points"]]),
            Series("mean turns / 35", [p["turns"]["mean"] / 35 for p in data["points"]]),
        ])


def sensitivity_heatmap() -> tuple[str, str]:
    """§9.3's named use for a heatmap: parameter sensitivity, two axes at once."""
    sweeps = [("sweep_grid_size", "grid size"),
              ("sweep_barrier_quota", "barrier quota"),
              ("sweep_survival_threshold", "survival threshold")]
    rows, labels = [], []
    for name, label in sweeps:
        data = load(name)
        base = data["points"][0]["capture_rate"]
        rows.append([round(point["capture_rate"] - base, 4) for point in data["points"]])
        labels.append(f"{label} (min {data['minimum']})")
    width = max(len(row) for row in rows)
    rows = [row + [row[-1]] * (width - len(row)) for row in rows]
    return "chart-parameter-sensitivity.svg", heatmap(
        title="Parameter sensitivity: change in capture rate from each minimum",
        caption="Each row sweeps one Appendix F Minimum upward, holding the rest at the "
                "fixture. Cells repeat where a sweep had fewer points than the widest.",
        x_label="sweep step (1 = the Appendix F minimum)",
        y_label="parameter",
        x_values=[f"step {i + 1}" for i in range(width)],
        y_values=labels, rows=rows, value_format="{:+.3f}")


def scent_chart() -> tuple[str, str]:
    data = load("scent_decay")
    return "chart-scent-decay.svg", line_chart(
        title="Scent decay from a single deposit",
        caption=f"Source {data['source_intensity']}, decay {data['decay_rate']} per turn — "
                f"both Appendix F **{data['appendix_f_status']}**, so this explains the "
                f"model rather than proposing a change to it.",
        x_label="turns since deposit", y_label="intensity",
        x_values=data["turns"],
        series=[Series("intensity", data["intensity"])])


def cost_chart() -> tuple[str, str]:
    data = load("decision_cost")
    return "chart-decision-cost.svg", bar_chart(
        title="Per-turn decision cost against the negotiated timeout",
        caption=f"{data['samples']} samples. Worst case {data['max']} ms is "
                f"{data['worst_case_share_of_timeout'] * 100:.4f}% of the "
                f"{data['response_timeout_ms']:.0f} ms response timeout.",
        x_label="statistic", y_label="milliseconds",
        categories=["mean", "median", "p95", "max"],
        series=[Series("decision time (ms)",
                       [data["mean"], data["median"], data["p95"], data["max"]])])


def main() -> int:
    ASSETS.mkdir(exist_ok=True)
    charts = dict(strategy_charts())
    charts.update([
        sweep_chart("sweep_grid_size", "Capture rate against board size",
                    "flat: see results/board_reach.json"),
        sweep_chart("sweep_barrier_quota", "Capture rate against barrier quota",
                    "flat: this arm places no barriers, see results/decision_mix.json"),
        sweep_chart("sweep_survival_threshold", "Capture rate against survival threshold",
                    "the one Minimum that moves the outcome"),
        sensitivity_heatmap(), scent_chart(), cost_chart(),
    ])
    for name, svg in charts.items():
        (ASSETS / name).write_text(svg, "utf-8")
        print(f"assets/{name}  ({len(svg):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
