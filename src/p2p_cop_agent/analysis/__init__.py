"""Parameter research and result visualisation (`M9-06`, `M9-07`).

Guidelines §9.1 asks for "systematic experiments with controlled changes to parameters",
§9.2 for a results analysis, §9.3 for bar, line, scatter, heatmap and box-plot
visualisations. The book is blunter about the standard: the research must be "based on
numbers and not on guesses" (p.142/266).

* `statistics` — summaries that never appear without their run count, plus the paired
  comparison the seeded protocol makes available.
* `charts` — line and bar charts as SVG.
* `heatmap` — the two-parameter sensitivity grid §9.3 names specifically.
* `boxplot` — the distribution view, drawn from the same five-number summary.

SVG rather than a plotting library: vector output is resolution-independent by
construction, adds no dependency to pin, and — the deciding reason — a chart emitted as
text can be **asserted**, so the tests check that a bar's height encodes its value.
"""

from p2p_cop_agent.analysis.boxplot import box_plot
from p2p_cop_agent.analysis.charts import Series, bar_chart, heat_cell_colour, line_chart
from p2p_cop_agent.analysis.heatmap import heatmap
from p2p_cop_agent.analysis.statistics import (
    PairedResult,
    Summary,
    paired_compare,
    quantile,
    summarise,
)

__all__ = [
    "PairedResult",
    "Series",
    "Summary",
    "bar_chart",
    "box_plot",
    "heat_cell_colour",
    "heatmap",
    "line_chart",
    "paired_compare",
    "quantile",
    "summarise",
]
