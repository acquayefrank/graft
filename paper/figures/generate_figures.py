#!/usr/bin/env python3
"""Generates publication-quality figures for the Graft Paper Track manuscript."""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9.5,
    'ytick.labelsize': 9.5,
    'legend.fontsize': 9.5,
    'figure.titlesize': 13,
    'figure.dpi': 300,
})

FIG_DIR = Path(__file__).resolve().parent
FIG_DIR.mkdir(parents=True, exist_ok=True)


def generate_figure1_complexity_phase_transition():
    """Figure 1: Resolution Rate and Mean Latency across Patch Complexity Buckets."""
    buckets = ['Tiny\n(1–5L)', 'Small\n(6–15L)', 'Medium\n(16–50L)', 'Large\n(51–150L)', 'Huge\n(>150L)']
    tasks = [12, 8, 5, 3, 2]
    resolved = [10, 6, 0, 0, 0]
    resolution_rates = [100.0 * r / t for r, t in zip(resolved, tasks)]
    latencies = [172.4, 204.8, 311.2, 360.0, 360.0]

    x = np.arange(len(buckets))
    width = 0.5

    fig, ax1 = plt.subplots(figsize=(6.8, 3.8))

    # Bar chart for resolution rate
    colors = ['#1a73e8', '#1a73e8', '#ea4335', '#ea4335', '#ea4335']
    bars = ax1.bar(x, resolution_rates, width, color=colors, alpha=0.88, edgecolor='black', linewidth=0.8, zorder=3)
    ax1.set_ylabel('Resolution Rate (%)', color='#202124', fontweight='bold')
    ax1.set_ylim(0, 105)
    ax1.set_xticks(x)
    ax1.set_xticklabels(buckets, fontweight='medium')
    ax1.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

    # Bar value labels
    for bar, rate, res, tot in zip(bars, resolution_rates, resolved, tasks):
        height = bar.get_height()
        label = f"{rate:.1f}%\n({res}/{tot})" if rate > 0 else f"0.0%\n(0/{tot})"
        ax1.annotate(label,
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontsize=8.5, fontweight='bold',
                     color='#202124')

    # Secondary axis for latency
    ax2 = ax1.twinx()
    line = ax2.plot(x, latencies, color='#f29900', marker='o', linewidth=2.4, markersize=7, label='Mean Task Latency', zorder=4)
    ax2.set_ylabel('Mean Latency (seconds)', color='#b06000', fontweight='bold')
    ax2.set_ylim(100, 400)
    ax2.axhline(360, color='#d93025', linestyle=':', linewidth=1.2, label='Task Timeout (360s / 6m)', zorder=2)
    ax2.tick_params(axis='y', labelcolor='#b06000')

    # Annotate the 15-line phase transition
    ax1.axvline(1.5, color='#5f6368', linestyle='--', linewidth=1.5, alpha=0.8, zorder=2)
    ax1.text(1.42, 92, '80.0% Production Baseline\n(Tiny + Small Combined)', ha='right', va='top',
             fontsize=8.5, fontweight='bold', color='#137333',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#e6f4ea', edgecolor='#137333', alpha=0.9))
    ax1.text(1.58, 92, 'The 15-Line\nComplexity Wall (0%)', ha='left', va='top',
             fontsize=8.5, fontweight='bold', color='#c5221f',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#fce8e6', edgecolor='#c5221f', alpha=0.9))

    # Combined legend
    lines, labels = ax2.get_legend_handles_labels()
    ax2.legend(lines, labels, loc='lower left', framealpha=0.95, facecolor='white', edgecolor='#dadce0')

    plt.title('SWE-bench Dev30: Resolution Rate & Latency across Diff Complexity', pad=14, fontweight='bold')
    plt.tight_layout()

    out_png = FIG_DIR / 'fig1_complexity_phase_transition.png'
    out_pdf = FIG_DIR / 'fig1_complexity_phase_transition.pdf'
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"[OK] Generated {out_png.name} and {out_pdf.name}")


def generate_figure2_failure_taxonomy():
    """Figure 2: Empirical Failure Mode Taxonomy Breakdown across Failed Tasks."""
    labels = [
        'Scale Horizon Timeout\n(Diff > 15 lines across 3+ files)',
        'Tool Parameter Mangling\n(Docstring JSON syntax errors)',
        'Harness Deadlock & Blindness\n(Post-submit chatter / Repro loops)'
    ]
    sizes = [42.9, 28.6, 28.6]
    counts = ['6 / 14 tasks', '4 / 14 tasks', '4 / 14 tasks']
    colors = ['#ea4335', '#fbbc04', '#4285f4']
    explode = (0.04, 0.02, 0.02)

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=140, colors=colors,
        textprops=dict(color='#202124', fontsize=9, fontweight='medium'),
        wedgeprops=dict(edgecolor='white', linewidth=1.5)
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)

    plt.title('Empirical Failure Mode Taxonomy on SWE-bench Dev30 (14 Failed Tasks)', pad=12, fontweight='bold')
    plt.tight_layout()

    out_png = FIG_DIR / 'fig2_failure_taxonomy.png'
    out_pdf = FIG_DIR / 'fig2_failure_taxonomy.pdf'
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"[OK] Generated {out_png.name} and {out_pdf.name}")


def generate_figure3_architecture():
    """Figure 3: System Architecture Flowchart of Host, Container A, and Container B."""
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.axis('off')

    # Draw 3 main containers/boxes
    # Box 1: Host Orchestrator
    box1 = patches.FancyBboxPatch((0.02, 0.15), 0.28, 0.72, boxstyle="round,pad=0.03",
                                  fc="#e8f0fe", ec="#1a73e8", lw=1.8)
    ax.add_patch(box1)
    ax.text(0.16, 0.81, "Host Orchestrator\n(Dual Intel Xeon + 4x L4)", ha="center", va="center",
            fontsize=9.5, fontweight="bold", color="#174ea6")
    ax.text(0.16, 0.50, "vLLM v1 Inference Server\n(Gemma 4 31B W4A16, TP=4)\n\nadk-submission Core\n\nswegemma Agent Runner\n(4.5m Pacing Gate)",
            ha="center", va="center", fontsize=8.2, color="#202124")

    # Arrow 1 -> 2
    ax.annotate("", xy=(0.35, 0.51), xytext=(0.30, 0.51),
                arrowprops=dict(arrowstyle="->", lw=2, color="#1a73e8"))
    ax.text(0.325, 0.56, "API", ha="center", va="center", fontsize=8, fontweight="bold", color="#1a73e8")

    # Box 2: Container A (Agent Execution)
    box2 = patches.FancyBboxPatch((0.35, 0.15), 0.30, 0.72, boxstyle="round,pad=0.03",
                                  fc="#fef7e0", ec="#f29900", lw=1.8)
    ax.add_patch(box2)
    ax.text(0.50, 0.81, "Container A: Agent Sandbox\n(Docker, Offline & Air-Gapped)", ha="center", va="center",
            fontsize=9.5, fontweight="bold", color="#b06000")
    ax.text(0.50, 0.50, "Workspace: /workspace\n(Git Repo Snapshot)\n\n9 Declarative Tools:\nAST, Graph, Filesystem\n\nIsolated Scratchpad:\nbuild/repro.py",
            ha="center", va="center", fontsize=8.2, color="#202124")

    # Arrow 2 -> 3
    ax.annotate("", xy=(0.70, 0.51), xytext=(0.65, 0.51),
                arrowprops=dict(arrowstyle="->", lw=2, color="#34a853"))
    ax.text(0.675, 0.56, "git diff", ha="center", va="center", fontsize=8, fontweight="bold", color="#137333")

    # Box 3: Container B (Verification)
    box3 = patches.FancyBboxPatch((0.70, 0.15), 0.28, 0.72, boxstyle="round,pad=0.03",
                                  fc="#e6f4ea", ec="#1e8e3e", lw=1.8)
    ax.add_patch(box3)
    ax.text(0.84, 0.81, "Container B: Verification\n(Phase 2 Clean Sandbox)", ha="center", va="center",
            fontsize=9.5, fontweight="bold", color="#137333")
    ax.text(0.84, 0.50, "Fresh Repo Baseline\n(base_commit checkout)\n\n4-Pass Resilient Patch Engine\n(Protected test-file stripping)\n\nHidden Pytest Suite\n(Graded Evaluation)",
            ha="center", va="center", fontsize=8.2, color="#202124")

    plt.title('Graft Dual-Container Hermetic Evaluation Architecture', pad=12, fontweight='bold', fontsize=12)
    plt.tight_layout()

    out_png = FIG_DIR / 'fig3_architecture.png'
    out_pdf = FIG_DIR / 'fig3_architecture.pdf'
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()
    print(f"[OK] Generated {out_png.name} and {out_pdf.name}")


if __name__ == '__main__':
    generate_figure1_complexity_phase_transition()
    generate_figure2_failure_taxonomy()
    generate_figure3_architecture()
