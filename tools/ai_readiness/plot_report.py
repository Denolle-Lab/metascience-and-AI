#!/usr/bin/env python3
"""Plot verified ai_readiness report output, without network or model calls.

Usage: python plot_report.py report.json --outprefix figures/readiness [--label TEXT]
       [--conditionals]

Points are not joined: absent years and unknown labels never become zeroes or
interpolated trends. Matplotlib is needed only when rendering, not for extraction.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import textwrap


METRICS = (
    ("multimodal_actual_use", "Multimodal use", "Known eligible reviewed papers"),
    ("ai_actual_use", "AI use", "Known eligible reviewed papers"),
    ("deep_learning_actual_use", "Deep-learning use", "Known eligible reviewed papers"),
    ("foundation_model_actual_use", "Foundation-model use", "Known eligible reviewed papers"),
    ("foundation_model_pretraining", "Foundation-model pretraining", "Known eligible reviewed papers"),
)
CONDITIONALS = (
    ("foundation_model_given_ai", "Foundation models among AI users", "Known eligible reviewed AI users"),
    ("foundation_model_given_deep_learning", "Foundation models among DL users", "Known eligible reviewed DL users"),
)


def number(value, label, *, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number.")
    if value < 0 or (integer and int(value) != value):
        raise ValueError(f"{label} must be a nonnegative {'integer' if integer else 'number'}.")
    return int(value) if integer else float(value)


def ratio(positive, denominator, proportion, label):
    if positive > denominator:
        raise ValueError(f"{label}: positive count exceeds its denominator.")
    if denominator == 0:
        if proportion is not None:
            raise ValueError(f"{label}: zero denominator must have a null proportion.")
        return None
    value = number(proportion, label + ' proportion')
    if value > 1 or not math.isclose(value, positive / denominator, rel_tol=1e-8, abs_tol=1e-10):
        raise ValueError(f"{label}: proportion does not match the supplied counts.")
    return value


def extract_plot_data(report, *, include_conditionals=False):
    """Return validated observed points; never manufacture missing observations.

    Population points require the core's saved-sample binding and availability
    flag. The report producer remains responsible for validating the study design.
    """
    if not isinstance(report, dict) or report.get("screen_labels_used_as_actual_use") is not False:
        raise ValueError("Expected a core report explicitly separating screening from actual use.")
    annuals = report.get("years")
    if not isinstance(annuals, list) or not annuals:
        raise ValueError("No annual reviewed results are available to plot.")
    seen = set()
    for annual in annuals:
        if not isinstance(annual, dict) or not isinstance(annual.get("metrics"), dict):
            raise ValueError("Every annual result needs a metrics object.")
        year = annual.get("year")
        if isinstance(year, bool) or not isinstance(year, int) or year in seen:
            raise ValueError("Report years must be unique integers.")
        seen.add(year)
    panels = []
    for name, title, denominator_label in METRICS + (CONDITIONALS if include_conditionals else ()):
        points = []
        for annual in sorted(annuals, key=lambda item: item["year"]):
            result = annual.get("metrics", {}).get(name)
            if result is None:
                continue
            if not isinstance(result, dict):
                raise ValueError(f"{annual['year']} {name}: expected a metric object.")
            context = f"{annual['year']} {name}"
            n = number(result.get("reviewed_eligible_known_denominator"), context + ' denominator', integer=True)
            k = number(result.get("reviewed_positive_count"), context + ' positives', integer=True)
            p = ratio(k, n, result.get("reviewed_subset_proportion"), context)
            unknown_value = result.get("unknown_or_inaccessible_labels")
            unknown = None if unknown_value is None else number(unknown_value, context + ' unknown labels', integer=True)
            if annual.get("reviewed_rows") is not None and n > number(annual["reviewed_rows"], context + ' reviewed rows', integer=True):
                raise ValueError(f"{context}: denominator exceeds the number of reviewed papers.")
            if p is not None:
                points.append({"year": annual["year"], "kind": "reviewed_subset", "proportion": p,
                               "positive": k, "denominator": n, "unknown": unknown, "ci": None})
            population = result.get("population_estimate") or {}
            if not isinstance(population, dict):
                raise ValueError(f"{context}: expected a population-estimate object.")
            if population.get("available") is not True:
                continue
            if report.get("sample_binding_verified") is not True:
                raise ValueError(f"{context}: population estimate lacks verified saved-sample binding.")
            if p is None:
                raise ValueError(f"{context}: population estimate has no known reviewed observations.")
            N = number(population.get("eligible_population_total_estimate"), context + ' estimated denominator')
            K = number(population.get("positive_population_total_estimate"), context + ' estimated positives')
            P = ratio(K, N, population.get("proportion"), context + ' population')
            if P is None:
                raise ValueError(f"{context}: an available population estimate needs a positive denominator.")
            ci = population.get("ci95_normal_approximation")
            if ci is not None:
                if not isinstance(ci, list) or len(ci) != 2:
                    raise ValueError(f"{context}: a reported CI must contain two bounds.")
                low, high = (number(bound, context + ' CI bound') for bound in ci)
                if not 0 <= low <= P <= high <= 1:
                    raise ValueError(f"{context}: reported CI does not enclose the estimate within [0, 1].")
                ci = [low, high]
            points.append({"year": annual["year"], "kind": "population", "proportion": P,
                           "positive": K, "denominator": N, "unknown": None, "ci": ci})
        if points:
            panels.append({"metric": name, "title": title, "denominator_label": denominator_label, "points": points})
    if not panels:
        raise ValueError("No known eligible full-text reviewed data or valid population estimates; no figure was created.")
    return panels


def render(report, panels, outprefix, label=None):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        from matplotlib.ticker import PercentFormatter
    except ImportError as error:
        raise RuntimeError("Plotting requires matplotlib; data extraction works without it. Install it in your chosen environment before rendering.") from error
    columns = 2 if len(panels) > 1 else 1
    rows = math.ceil(len(panels) / columns)
    fig, axes = plt.subplots(rows, columns, figsize=(12 if columns == 2 else 7, 3.55 * rows + 1.45), squeeze=False)
    subset_color, population_color = "#17659c", "#b34e00"
    any_population = any(p["kind"] == "population" for panel in panels for p in panel["points"])
    any_ci = any(p["ci"] is not None for panel in panels for p in panel["points"])
    years = sorted(annual["year"] for annual in report["years"])
    for ax, panel in zip(axes.flat, panels):
        for point in panel["points"]:
            population = point["kind"] == "population"
            x = point["year"] + (0.11 if population else -0.11 if any_population else 0)
            y = point["proportion"]
            color = population_color if population else subset_color
            ax.plot(x, y, marker="D" if population else "o", color=color,
                    markerfacecolor="white" if population else color, markersize=6, linestyle="None", zorder=3)
            if point["ci"] is not None:
                low, high = point["ci"]
                ax.errorbar(x, y, yerr=[[y - low], [high - y]], fmt="none", ecolor=color, capsize=3, linewidth=1.1, zorder=2)
            if not population:
                ax.annotate(f"{point['positive']}/{point['denominator']}", (x, y),
                            xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8, color=color)
        ax.set_title(panel["title"], loc="left", fontsize=12, fontweight="bold")
        ax.set_xlabel("Publication year")
        ax.set_ylabel("Proportion")
        ax.set_xticks(years, [str(year) for year in years], rotation=45 if len(years) > 7 else 0)
        ax.set_xlim(years[0] - 0.55, years[-1] + 0.55)
        ax.set_ylim(-0.06, 1.15)
        ax.set_yticks([0, .25, .5, .75, 1])
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        ax.grid(axis="y", alpha=.22)
        ax.spines[["top", "right"]].set_visible(False)
        ax.text(0, -0.29 if len(years) > 7 else -0.25, panel["denominator_label"],
                transform=ax.transAxes, fontsize=8, color="#444444")
    for ax in list(axes.flat)[len(panels):]:
        ax.set_visible(False)
    legend = [Line2D([], [], marker="o", color=subset_color, linestyle="None", label="Reviewed subset (labels show positives / known denominator)")]
    if any_population:
        legend.append(Line2D([], [], marker="D", markerfacecolor="white", color=population_color,
                             linestyle="None", label="Design-weighted estimate within the frozen source frame"))
    title = label or "Verified literature-use evidence"
    fig.suptitle(title, fontsize=16, fontweight="bold", y=.985)
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(.5, .96), frameon=False, fontsize=9, ncol=1)
    note = ("Subset proportions describe reviewed papers with known labels, not the research community. "
            "Unknown labels and unreviewed/inaccessible papers are excluded, never coded as zero. "
            "AI, DL and FM labels overlap. Points are not connected; missing years are not interpolated. ")
    note += "Whiskers use only the report's supplied 95% confidence intervals. " if any_ci else "No confidence intervals were supplied for the plotted points. "
    note += "Scope: " + str(report.get("scope") or "Reviewed accessible subset only.")
    wrapped = textwrap.fill(note, 153 if columns == 2 else 90)
    needed_footer_inches = len(wrapped.splitlines()) * .14 + .55
    height = fig.get_size_inches()[1]
    if needed_footer_inches > height * .3:
        fig.set_size_inches(fig.get_size_inches()[0], height + needed_footer_inches)
        height = fig.get_size_inches()[1]
    bottom = max(.15, .025 + needed_footer_inches / height)
    fig.text(.06, .025, wrapped, fontsize=8, color="#444444", va="bottom")
    fig.subplots_adjust(top=.86, bottom=bottom, left=.075, right=.97, hspace=.6, wspace=.28)
    prefix = Path(outprefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    paths = [Path(str(prefix) + suffix) for suffix in (".svg", ".png")]
    try:
        fig.savefig(paths[0], bbox_inches="tight")
        fig.savefig(paths[1], dpi=200, bbox_inches="tight")
    finally:
        plt.close(fig)
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON report emitted by ai_readiness.core report")
    parser.add_argument("--outprefix", required=True, help="Output path prefix; writes .svg and .png")
    parser.add_argument("--label", help="Figure title; scope and limitations remain visible")
    parser.add_argument("--conditionals", action="store_true", help="Also plot FM use among verified AI and DL users")
    args = parser.parse_args(argv)
    try:
        report = json.loads(Path(args.input).read_text(encoding="utf-8"))
        panels = extract_plot_data(report, include_conditionals=args.conditionals)
        outputs = render(report, panels, args.outprefix, args.label)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Cannot plot report: {error}\n")
    print("\n".join(str(path) for path in outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
