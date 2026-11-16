#!/usr/bin/env python3
"""UNFORTUNATELY — the 6 article charts (navy theme)
Reads ../unfortunately_dataset.csv, writes PNG + SVG into ../charts/.
Run:  python3 charts_article.py
"""
from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_data import load_article, OUT

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams


INK    = "#121212"   # text
BLUE   = "#052962"   # main
ACCENT = "#0084c6"   # secondary
RED    = "#c70000"   # highlight
GREY   = "#dcdcdc"
MUTE   = "#767676"

rcParams.update({
    "font.family": "DejaVu Sans", "text.color": INK,
    "axes.edgecolor": INK, "axes.labelcolor": INK,
    "xtick.color": MUTE, "ytick.color": INK,
    "axes.titlesize": 15, "axes.titleweight": "bold",
    "figure.facecolor": "white", "axes.facecolor": "white",
    "svg.fonttype": "none",
})

df = load_article()
HUM = df["Human reply (YES) or automatic reply (NO)"] == "YES"
H = df[HUM]
SENT = len(df)

def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    print("saved", name)

def footer(fig, extra=""):
    fig.text(0.01, 0.005,
             f"Source: author's correspondence log, {SENT:,} institutions, Jan–Dec 2025. {extra}",
             fontsize=7.5, color=MUTE, ha="left")

def titled(ax, t, sub):
    """Title + subtitle with a fixed points-based gap (height-independent)."""
    ax.annotate(t, xy=(0, 1), xycoords="axes fraction", xytext=(0, 26),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=15, fontweight="bold", color=INK, annotation_clip=False)
    ax.annotate(sub, xy=(0, 1), xycoords="axes fraction", xytext=(0, 10),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=10.5, color=MUTE, annotation_clip=False)

def ftitled(fig, t, sub):
    """Figure-level title + subtitle (for axis-off charts), fixed points gap."""
    H = fig.get_size_inches()[1] * 72.0  # figure height in points
    fig.text(0.01, 1 - 16/H, t, ha="left", va="top", fontsize=15,
             fontweight="bold", color=INK)
    fig.text(0.01, 1 - 38/H, sub, ha="left", va="top", fontsize=10.5, color=MUTE)

# ---------------------------------------------------------------- fig 1
deliv = (df["Delivered"] == "YES").sum()
ans   = (df["Is there an answer"] == "YES").sum()
hum   = HUM.sum()
pf    = (df["PF_positive_feedback"] == "YES").sum()
coop  = (df["COOP_agreement"] == "YES").sum()

stages = [("Emails sent", SENT), ("Delivered", deliv), ("Any reply at all", ans),
          ("A human wrote back", hum), ("Showed interest in the work", pf),
          ("Led to a collaboration", coop)]
fig, ax = plt.subplots(figsize=(9, 4.6))
ys = range(len(stages))[::-1]
for y, (lab, v) in zip(ys, stages):
    color = BLUE if v > 1000 else (ACCENT if v > 60 else RED)
    ax.barh(y, max(v, SENT*0.0035), height=0.62, color=color)
    share = f"{100*v/SENT:.1f}%" if 0 < v < SENT else ("100%" if v == SENT else "")
    txt = f"{v:,}" + (f"   ({share} of sent)" if share and v != SENT else "")
    if v == 0: txt = "0"
    ax.text(max(v, SENT*0.0035) + 40, y, txt, va="center", fontsize=11,
            fontweight="bold", color=INK)
    ax.text(-60, y, lab, va="center", ha="right", fontsize=11.5)
ax.set_xlim(0, 5150); ax.set_yticks([]); ax.set_xticks([])
for s in ax.spines.values(): s.set_visible(False)
titled(ax, "4,269 letters in, 0 collaborations out",
       "One artist's identical proposal to art institutions in 91 countries — what came back")
footer(fig, "Interest = reply with positive feedback on the work.")
fig.subplots_adjust(left=0.27)
save(fig, "fig1_funnel")

# ---------------------------------------------------------------- fig 2
hrs = H["Response_hours"].dropna().sort_values()
import numpy as np
cum = np.arange(1, len(hrs) + 1) / len(hrs) * 100
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(hrs / 24, cum, color=BLUE, lw=2.4)
ax.set_xscale("log")
ax.set_xlim(0.01, 130); ax.set_ylim(0, 102)
marks = [(5/24, "5 h"), (1, "24 h"), (7, "7 days"), (30, "30 days")]
for x, lab in marks:
    yv = (hrs <= x * 24).mean() * 100
    ax.plot([x], [yv], "o", color=RED, ms=6, zorder=5)
    ax.annotate(f"{lab}: {yv:.0f}%", (x, yv), textcoords="offset points",
                xytext=(8, -14), fontsize=10.5, fontweight="bold", color=RED)
ax.axhline(100, color=GREY, lw=.8, ls=":")
ax.set_xticks([1/24, 1, 7, 30, 120]); ax.set_xticklabels(["1 h", "1 day", "1 week", "1 month", "4 months"])
ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels(["0", "25", "50", "75", "100%"])
ax.grid(axis="y", color=GREY, lw=.7)
for s in ["top", "right", "left"]: ax.spines[s].set_visible(False)
titled(ax, "When the art world says no, it says it within a day",
       f"Cumulative share of the {len(hrs)} human replies, by time elapsed since the outgoing email (log scale)")
footer(fig)
save(fig, "fig2_speed")

# ---------------------------------------------------------------- fig 3
g  = H["GTWC: Greeting"].notna().mean() * 100
t  = H["GTWC: Post-greeting thank-you phrase (short)"].notna().mean() * 100
w_ = H["GTWC: Pre-closing well-wishing phrase"].notna().mean() * 100
c  = H["GTWC: Closing phrase"].notna().mean() * 100
pers = H["GTWC: Greeting personalization"].notna().mean() * 100
medw = H["reply_words"].median()
unf  = (H["Is the word ‘unfortunately’ used?"] == "YES").mean() * 100

rows = [
    ("“Dear Pavlo,”",                       f"greeting — {g:.0f}% of replies; {pers:.0f}% use the name", g),
    ("“Thank you for your email.”",         f"opening thank-you — {t:.0f}%", t),
    (f"“Unfortunately …”  [body, median {medw:.0f} words]", f"the word itself appears in {unf:.0f}% of replies", unf),
    ("“We wish you all the best.”", f"well-wishing line — {w_:.0f}%", w_),
    ("“Kind regards,”",                     f"sign-off — {c:.0f}%", c),
]
fig, ax = plt.subplots(figsize=(9.6, 5))
ax.set_xlim(0, 100); ax.set_ylim(-0.7, len(rows) - 0.1)
for i, (quote, note, share) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.barh(y - 0.22, 100, height=0.13, color="#f0f0f0", zorder=1)
    ax.barh(y - 0.22, share, height=0.13, color=(RED if "Unfortunately" in quote else ACCENT), zorder=2)
    ax.text(0, y + 0.16, quote, fontsize=12.5, style="italic", color=INK,
            fontweight="bold" if "Unfortunately" in quote else "normal")
    ax.text(100, y - 0.22, f" {note}", fontsize=9.5, color=MUTE, va="center", ha="left")
ax.axis("off")
ftitled(fig, "The composite rejection: one letter assembled from 272 real ones",
        "Most frequent phrase in each structural slot of the human replies, with the share of replies that fill that slot")
footer(fig, "Slot phrases and fill rates from manual letter-by-letter coding.")
fig.subplots_adjust(right=0.70, top=0.84)
save(fig, "fig3_anatomy")

# ---------------------------------------------------------------- fig 4
A = df[df["Was there an automatic reply?"] == "YES"]
PR = A[A["Automatic reply - Promise to reply"] == "YES"]
n_auto, n_pr = len(A), len(PR)
tc = PR["Automatic reply - Promise to reply - Timeliness category"].value_counts()
on_time = tc.get("Replied on time / early", 0)
late    = tc.get("Replied late", 0)
nodl_ok = tc.get("Human reply received / no fixed deadline", 0)
silent  = tc.get("No human reply after fixed deadline", 0) + tc.get("No human reply / no fixed deadline", 0)
od = PR["days_overdue"].dropna()
mx = PR["Automatic reply - Promise to reply - Reply period max days (approx.)"].dropna()

fig, ax = plt.subplots(figsize=(9.6, 4.6))
# top bar: 134 auto-replies
ax.barh(1, n_pr, height=0.5, color=BLUE)
ax.barh(1, n_auto - n_pr, left=n_pr, height=0.5, color="#b9c6d8")
ax.text(n_pr/2, 1, f"promised a human reply — {n_pr}", ha="center", va="center",
        color="white", fontsize=11, fontweight="bold")
ax.text(n_pr + (n_auto - n_pr)/2, 1, f"no promise — {n_auto - n_pr}", ha="center",
        va="center", color=INK, fontsize=11)
# bottom bar: outcomes of the 80
segs = [(silent, "#9e9e9e", f"never replied — {silent}", "white"),
        (late, ACCENT, f"{late}", "white"),
        (nodl_ok, "#64b2d1", f"{nodl_ok}", "white"),
        (on_time, RED, f"{on_time}", "white")]
x0 = 0
for v, col, lab, tcol in segs:
    ax.barh(0, v, left=x0, height=0.5, color=col)
    ax.text(x0 + v/2, 0, lab, ha="center", va="center", color=tcol,
            fontsize=10.5, fontweight="bold")
    x0 += v
ax.annotate(f"replied late — {late}", (silent + late/2, -0.34),
            ha="center", fontsize=9.5, color=ACCENT, fontweight="bold")
ax.annotate(f"replied, no deadline given — {nodl_ok}", (silent + late + nodl_ok/2, -0.57),
            ha="center", fontsize=9.5, color="#64b2d1", fontweight="bold")
ax.annotate(f"replied on time — {on_time}", (silent + late + nodl_ok + on_time/2, -0.80),
            ha="center", fontsize=9.5, color=RED, fontweight="bold")
ax.annotate("", xy=(n_pr*0.5, 0.42), xytext=(n_pr*0.5, 0.72),
            arrowprops=dict(arrowstyle="->", color=MUTE))
ax.set_yticks([0, 1])
ax.set_yticklabels([f"what the {n_pr}\npromises produced", f"{n_auto} auto-replies"], fontsize=11)
ax.set_xticks([]); ax.set_xlim(0, n_auto + 2); ax.set_ylim(-1.05, 1.6)
for sp in ax.spines.values(): sp.set_visible(False)
ftitled(fig, "“We will get back to you”: a promise kept one time in five",
        f"Median promised window: {mx.median():.0f} days.  Median delay of the {len(od)} promised replies still missing: {od.median():.0f} days (as of 16 Nov 2026).")
footer(fig, "Promise tracking coded manually from each auto-reply text.")
fig.subplots_adjust(top=0.82, left=0.17)
save(fig, "fig4_promises")

# ---------------------------------------------------------------- fig 5
cc = df.groupby("Country").agg(sent=("ID", "count"),
        human=("Human reply (YES) or automatic reply (NO)", lambda s: (s == "YES").sum()))
cc["rate"] = 100 * cc["human"] / cc["sent"]
top = cc.sort_values("sent", ascending=False).head(12).sort_values("rate")
fig, ax = plt.subplots(figsize=(9, 5.4))
ys = range(len(top))
for y, (name, r) in zip(ys, top.iterrows()):
    hl = name == "Australia"
    ax.plot([0, r["rate"]], [y, y], color=GREY, lw=2, zorder=1)
    ax.plot([r["rate"]], [y], "o", ms=11, color=RED if hl else BLUE, zorder=3)
    ax.text(r["rate"] + 0.45, y, f"{r['rate']:.1f}%", va="center", fontsize=10.5,
            fontweight="bold", color=RED if hl else INK)
    ax.text(-0.4, y, f"{name}  ·  {int(r['sent']):,} sent", ha="right", va="center", fontsize=10.5)
ax.set_xlim(0, 26); ax.set_yticks([])
ax.set_xticks([0, 5, 10, 15, 20, 25]); ax.set_xticklabels(["0", "5", "10", "15", "20", "25%"])
ax.grid(axis="x", color="#efefef")
for s in ax.spines.values(): s.set_visible(False)
titled(ax, "Where a letter gets an answer: human-reply rate, 12 biggest destinations",
       "Share of institutions where a person (not a machine) wrote back")
footer(fig)
fig.subplots_adjust(left=0.30)
save(fig, "fig5_geography")

# ---------------------------------------------------------------- fig 6
cd = H[H["CLOSED DOORS reason flagged: YES/NO"] == "YES"]["CLOSED DOORS SUBCATEGORY"].value_counts()
labels = {
    "No new artists / full roster / schedule full": "Roster or schedule is full —\nnot taking new artists",
    "No unsolicited submissions / proposals": "We do not accept\nunsolicited submissions",
    "Institutional policy / collection limits / programme fit": "Outside our collection,\npolicy or programme",
    "Curatorial / invitation-based selection": "Selection is by\ninvitation / curators only",
    "Only through galleries / dealers / fairs": "Approach us only through\ngalleries, dealers or fairs",
    "Other closed-door reason / no current cooperation": "Other closed-door reason",
}
fig, ax = plt.subplots(figsize=(9, 4.8))
vals = cd.sort_values()
ys = range(len(vals))
ax.barh(ys, vals.values, height=0.6, color=[RED if v == cd.max() else BLUE for v in vals.values])
for y, (k, v) in zip(ys, vals.items()):
    ax.text(v + 0.6, y, f"{v}  ({100*v/cd.sum():.0f}%)", va="center", fontsize=10.5, fontweight="bold")
    ax.text(-1, y, labels.get(k, k), ha="right", va="center", fontsize=10.5)
ax.set_xlim(0, 58); ax.axis("off")
ftitled(fig, "Why the door is closed: the reasons institutions actually give",
        f"The {cd.sum()} human replies (47% of all 272) that named an explicit closed-door reason")
footer(fig, "Reason categories coded manually from reply texts.")
fig.subplots_adjust(left=0.30, top=0.84)
save(fig, "fig6_doors")

print("ALL CHARTS DONE ->", OUT)
