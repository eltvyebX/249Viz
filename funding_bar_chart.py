"""
Horizontal Bar Chart Race (MP4) — Sudan Humanitarian Funding by Donor (2010–2025)
Renders the same cumulative-funding race as the Plotly HTML version.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as mticker

# ---------------------------------------------------------------
# 1. Load & prepare data 
# ---------------------------------------------------------------
df = pd.read_csv("fts_sudan_funding_clean.csv")
df = df[df["donor"] != "Qatar Charity"]

df = df.sort_values(["donor", "year"])
df["cumulative_usd"] = df.groupby("donor")["funding_usd"].cumsum()

years = sorted(df["year"].unique())
donors = sorted(df["donor"].unique())

pivot = (
    df.pivot(index="year", columns="donor", values="cumulative_usd")
    .reindex(years)
    .ffill()
    .fillna(0)
)

colors = {
    donor: c
    for donor, c in zip(
        donors,
        ["#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2", "#B279A2"],
    )
}

x_max = pivot.values.max() * 1.2

# Smooth interpolation: N in-between steps per year transition for a fluid race
STEPS_PER_YEAR = 12
HOLD_LAST_FRAMES = 20  # pause on the final year at the end

frames = []  # list of (display_year_label, {donor: value})
for i, year in enumerate(years):
    if i == 0:
        frames.append((str(year), pivot.loc[year].to_dict()))
        continue
    prev_vals = pivot.loc[years[i - 1]]
    cur_vals = pivot.loc[year]
    for step in range(1, STEPS_PER_YEAR + 1):
        t = step / STEPS_PER_YEAR
        interp = prev_vals + (cur_vals - prev_vals) * t
        label = str(year) if step == STEPS_PER_YEAR else str(years[i - 1])
        frames.append((label, interp.to_dict()))

# Hold on the final frame
frames += [frames[-1]] * HOLD_LAST_FRAMES

# ---------------------------------------------------------------
# 2. Set up the figure
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
fig.patch.set_facecolor("white")


def draw_frame(i):
    ax.clear()
    label, values = frames[i]
    row = pd.Series(values).sort_values(ascending=True)

    bar_colors = [colors[d] for d in row.index]
    bars = ax.barh(row.index, row.values, color=bar_colors, height=0.6)

    for bar, val in zip(bars, row.values):
        ax.text(
            val + x_max * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"${val:,.0f}",
            va="center",
            ha="left",
            fontsize=10,
            color="#333333",
        )

    ax.set_xlim(0, x_max)
    ax.set_title(
        f"Total Cumulative Funding by Donor — Sudan ({label})",
        fontsize=14,
        fontweight="bold",
        loc="left",
        pad=15,
    )
    ax.set_xlabel("Cumulative Funding (USD)", fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:,.0f}M"))
    ax.tick_params(axis="y", labelsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    fig.tight_layout()
    return bars


ani = animation.FuncAnimation(fig, draw_frame, frames=len(frames), interval=1000 / 24)

writer = animation.FFMpegWriter(fps=24, bitrate=3000)
ani.save("sudan_funding_bar_race.mp4", writer=writer)
print("Saved sudan_funding_bar_race.mp4")
