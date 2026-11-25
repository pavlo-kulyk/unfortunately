#!/usr/bin/env python3
"""UNFORTUNATELY — the 33 report charts (pink theme)
Reads ../unfortunately_dataset.csv, writes PNG + SVG into ../charts/.
Run:  python3 charts_report.py
"""
from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_data import load, OUT

import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, Polygon

r = load()
for c in ["time of my letter", "Response time", "Automatic reply time"]:
    r[c] = pd.to_datetime(r[c], errors="coerce")

HUM = r["Human reply (YES) or automatic reply (NO)"] == "YES"
H = r[HUM].copy()
AUTO = r[r["Was there an automatic reply?"] == "YES"].copy()
N = len(r)
hum = len(H)

# ---- palette ----------------------------------------------------------------
PINK   = "#d81b60"; PINK_MID = "#ee6e9f"; PINK_SOFT = "#f7b6cc"; PINK_PALE = "#fbdfe9"
T1="#F8C7D8"; T2="#F0A0BE"; T3="#E45E8E"; T4="#D81B60"
INK="#1a1a1a"; MUTE="#777"; LINE="#e8e4e2"; GREY="#d9d4d2"

rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "text.color": INK, "axes.edgecolor": "#cfcac8",
    "axes.labelcolor": INK, "xtick.color": MUTE, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "svg.fonttype": "none",
})

def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=170, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  saved", name)

def title(ax, t, sub=None):
    # points-based offsets (height-independent) -> consistent title/subtitle gap
    ax.annotate(t, xy=(0, 1), xycoords="axes fraction",
                xytext=(0, 26 if sub else 9), textcoords="offset points",
                ha="left", va="bottom", fontsize=15, fontweight="bold",
                color=INK, annotation_clip=False)
    if sub:
        ax.annotate(sub, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 10), textcoords="offset points",
                    ha="left", va="bottom", fontsize=10.5, color=MUTE,
                    annotation_clip=False)

def yes(df, col):
    return (df[col].astype(str).str.strip().str.upper() == "YES")

def hbars(name, labels, values, ttl, sub=None, fmt="{:.0f}", unit="",
          color=PINK, note=None, figsize=None, valuesuffix=None, highlight=None):
    """Generic ranked horizontal bar chart (top value on top)."""
    n = len(labels)
    fig, ax = plt.subplots(figsize=figsize or (9, max(2.4, 0.52*n + 1.3)))
    y = np.arange(n)[::-1]
    cols = [color]*n
    if highlight is not None:
        cols = [PINK if i in highlight else PINK_SOFT for i in range(n)]
    ax.barh(y, values, height=0.66, color=cols)
    vmax = max(values) if len(values) else 1
    for yi, v, lab in zip(y, values, labels):
        suf = valuesuffix[list(labels).index(lab)] if valuesuffix else ""
        ax.text(v + vmax*0.012, yi, (fmt.format(v)+unit+suf), va="center",
                fontsize=10.5, fontweight="bold", color=INK)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=11)
    ax.set_xticks([]); ax.set_xlim(0, vmax*1.16)
    for s in ["bottom","left"]: ax.spines[s].set_visible(False)
    title(ax, ttl, sub)
    if note:
        fig.text(0.01, -0.02, note, fontsize=8.5, color=MUTE, ha="left")
    fig.tight_layout()
    save(fig, name)

def funnel(name, stages, ttl, sub):
    n = len(stages)
    fig, ax = plt.subplots(figsize=(9.6, 0.66*n + 2.0))
    vmax = stages[0][1]
    cols = [T1, T2, T3, T4, PINK, "#7a1240"][:n]
    ys = np.arange(n)[::-1]
    for i,(y,(lab,v)) in enumerate(zip(ys, stages)):
        w = max(v, vmax*0.006)
        ax.barh(y, w, height=0.62, color=cols[i], zorder=3)
        share = f"{100*v/vmax:.1f}%" if 0 < v < vmax else ("100%" if v==vmax else "")
        lbl = f"{v:,}" + (f"   ·   {share}" if share and v!=vmax else "")
        if v == 0: lbl = "0"
        ax.text(w + vmax*0.012, y, lbl, va="center", ha="left", fontsize=11,
                fontweight="bold", color=INK, zorder=4)
        ax.text(-vmax*0.015, y, lab, va="center", ha="right", fontsize=11.5, color=INK)
    ax.set_xlim(0, vmax*1.02); ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)
    title(ax, ttl, sub)
    fig.subplots_adjust(left=0.28, top=0.82)
    save(fig, name)


print("Rendering charts ->", OUT)

# ============================================================ 01 funnel
from funnel import render_funnel as render_01_funnel
render_01_funnel()

# ============================================================ 02 region
reg = r.groupby("Region").agg(sent=("id","count"),
        human=("Human reply (YES) or automatic reply (NO)", lambda s:(s=="YES").sum()),
        pf=("Positive feedback on my technique", lambda s:(s=="YES").sum()))
reg["human%"]=100*reg["human"]/reg["sent"]; reg["pf%"]=100*reg["pf"]/reg["sent"]
reg=reg.sort_values("sent", ascending=False)
fig, ax = plt.subplots(figsize=(9.6,4.8))
x=np.arange(len(reg)); w=0.38
ax.bar(x-w/2, reg["human%"], w, color=PINK, label="Human reply rate")
ax.bar(x+w/2, reg["pf%"], w, color=PINK_SOFT, label="Positive-feedback rate")
for xi,hv,pv in zip(x, reg["human%"], reg["pf%"]):
    ax.text(xi-w/2, hv+0.25, f"{hv:.1f}%", ha="center", fontsize=9.5, fontweight="bold")
    ax.text(xi+w/2, pv+0.25, f"{pv:.1f}%", ha="center", fontsize=9.5, color="#a3235c")
ax.set_xticks(x); ax.set_xticklabels([f"{i}\n(n={int(s):,})" for i,s in zip(reg.index, reg["sent"])], fontsize=10)
ax.set_ylabel("% of letters sent to region"); ax.set_ylim(0, reg["human%"].max()*1.18)
ax.legend(frameon=False, fontsize=10, loc="upper right")
title(ax, "Response rate is regional, not global",
      "Human-reply and positive-feedback rate by region")
fig.tight_layout(); save(fig, "02_region")

# ============================================================ 03 countries (top 15)
cc = r.groupby("Country").agg(sent=("id","count"),
        human=("Human reply (YES) or automatic reply (NO)", lambda s:(s=="YES").sum()),
        pf=("Positive feedback on my technique", lambda s:(s=="YES").sum()))
cc["human%"]=100*cc["human"]/cc["sent"]
top=cc.sort_values("sent", ascending=False).head(15).sort_values("human%")
overall=100*HUM.sum()/N
fig, ax = plt.subplots(figsize=(9.6, 7.0))
y=np.arange(len(top))
ax.barh(y, top["human%"], height=0.66,
        color=[PINK if v>=overall else PINK_SOFT for v in top["human%"]])
for yi,(nm,row) in zip(y, top.iterrows()):
    ax.text(row["human%"]+0.25, yi, f"{row['human%']:.1f}%",
            va="center", fontsize=10, fontweight="bold", color=INK)
ax.set_yticks(y)
ax.set_yticklabels([f"{nm}  (n={int(row['sent']):,})" for nm,row in top.iterrows()], fontsize=10.5)
ax.axvline(overall, color=INK, ls="--", lw=1.2)
ax.text(overall+0.15, -0.55, f"corpus-wide {overall:.1f}%", color=INK, fontsize=9.5, va="top")
ax.set_xticks([]); ax.set_xlim(0, top["human%"].max()*1.18)
for s in ["bottom","left"]: ax.spines[s].set_visible(False)
title(ax, "Volume does not buy attention",
      "Human-reply rate, top 15 destinations by outreach volume — dark = above corpus average")
fig.tight_layout(); save(fig, "03_countries")

# ============================================================ 09 institution type
ct = r.groupby("institution_type").agg(sent=("id","count"),
        human=("Human reply (YES) or automatic reply (NO)", lambda s:(s=="YES").sum()),
        pf=("Positive feedback on my technique", lambda s:(s=="YES").sum()))
ct["human%"]=100*ct["human"]/ct["sent"]; ct["pf%"]=100*ct["pf"]/ct["sent"]
ct=ct[ct["sent"]>=35].sort_values("sent", ascending=False)
fig, ax = plt.subplots(figsize=(9.6, 6.2))
y=np.arange(len(ct))[::-1]
ax.barh(y, ct["human%"], height=0.66, color=PINK, label="Human reply rate")
ax.barh(y, ct["pf%"], height=0.30, color="#7a1240", label="Positive feedback")
for yi,(nm,row) in zip(y, ct.iterrows()):
    ax.text(row["human%"]+0.12, yi, f"{row['human%']:.1f}%   (n={int(row['sent']):,})",
            va="center", fontsize=10, fontweight="bold")
ax.set_yticks(y); ax.set_yticklabels(ct.index, fontsize=11)
ax.set_xticks([]); ax.set_xlim(0, ct["human%"].max()*1.30)
for s in ["bottom","left"]: ax.spines[s].set_visible(False)
ax.legend(frameon=False, fontsize=10, loc="lower right")
title(ax, "By institution type",
      "Both rates are shares of all letters sent; category assigned by hand. Bars ≥ 35 letters.")
fig.tight_layout(); save(fig, "09_types")

# ============================================================ 10 source
src = r.copy(); src["Source"]=src["Source"].fillna("(none)")
sg = src.groupby("Source").agg(sent=("id","count"),
        human=("Human reply (YES) or automatic reply (NO)", lambda s:(s=="YES").sum()),
        pf=("Positive feedback on my technique", lambda s:(s=="YES").sum()))
sg["human%"]=100*sg["human"]/sg["sent"]; sg["pf%"]=100*sg["pf"]/sg["sent"]
sg=sg[sg["sent"]>=40].sort_values("human%", ascending=False)
fig, ax = plt.subplots(figsize=(9.6, 5.4))
y=np.arange(len(sg))[::-1]
ax.barh(y, sg["human%"], height=0.62, color=PINK, label="Human reply rate")
ax.barh(y, sg["pf%"], height=0.28, color="#7a1240", label="Positive feedback")
for yi,(nm,row) in zip(y, sg.iterrows()):
    ax.text(row["human%"]+0.1, yi, f"{row['human%']:.1f}%  ·  pf {row['pf%']:.1f}%  (n={int(row['sent']):,})",
            va="center", fontsize=9.5, fontweight="bold")
ax.set_yticks(y); ax.set_yticklabels(sg.index, fontsize=10.5)
ax.set_xticks([]); ax.set_xlim(0, sg["human%"].max()*1.42)
for s in ["bottom","left"]: ax.spines[s].set_visible(False)
ax.legend(frameon=False, fontsize=10, loc="lower right")
title(ax, "Where the contact came from matters",
      "Reply rate by the directory or list a contact came from (sources ≥ 40 letters)")
fig.tight_layout(); save(fig, "10_source")

# ============================================================ 11 volume vs rate
r["mon"]=r["time of my letter"].dt.to_period("M")
mv=r.groupby("mon").size()
mh=r[HUM].groupby(r[HUM]["time of my letter"].dt.to_period("M")).size()
rate=(100*mh/mv).reindex(mv.index)
mv=mv[mv>0]
labels=[str(p) for p in mv.index]
fig, ax = plt.subplots(figsize=(9.8,5.0))
x=np.arange(len(mv))
ax.bar(x, mv.values, color=PINK_SOFT, width=0.7, label="Letters sent")
_ax1_top = mv.max()*1.16; _ax2_top = np.nanmax(rate.values)*1.4
for xi,v in zip(x, mv.values):
    ax.annotate(f"{v:,}", (xi, v), textcoords="offset points", xytext=(0,3),
                ha="center", fontsize=8.5, color=MUTE)
ax.set_ylabel("Letters sent", color=MUTE); ax.set_ylim(0, _ax1_top)
ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
ax2=ax.twinx(); ax2.spines["top"].set_visible(False)
ax2.plot(x, rate.reindex(mv.index).values, "-o", color=PINK, lw=2.4, label="Human-reply rate")
_rvals = rate.reindex(mv.index).values
for xi,v,bar in zip(x, _rvals, mv.values):
    if np.isnan(v): continue
    # if the bar is tall its "620"-style label sits where the % label would go,
    # so drop the % label below the marker instead of above it (also for the
    # steep dip at 2025-03, where an above-label would sit on the line)
    below = (bar/_ax1_top) >= (v/_ax2_top) - 0.02 or labels[xi].endswith("-03")
    ax2.annotate(f"{v:.1f}%", (xi, v), textcoords="offset points",
                 xytext=(0, -12 if below else 9), va="top" if below else "bottom",
                 ha="center", fontsize=9, fontweight="bold", color=PINK)
ax2.set_ylabel("Human-reply rate", color=PINK); ax2.set_ylim(0, _ax2_top)
# Annotation for the Google account block
_sep = next((i for i,l in enumerate(labels) if l.endswith("-09")), None)
if _sep is not None:
    ax.annotate("Google blocked\nthe account\n23 Sep 2025",
                xy=(_sep+0.4, mv.values[_sep]),
                xytext=(_sep+1.2, mv.max()*0.95),
                fontsize=9.5, color=MUTE,
                arrowprops=dict(arrowstyle="->", color="#aaa", lw=0.9))
title(ax, "Scaling up did not raise the reply rate", "Monthly outgoing volume (bars) vs human-reply rate (line)")
fig.tight_layout(); save(fig, "11_volume_vs_rate")

# ============================================================ 04 reasons
rc = H["Reason category"].value_counts()
lab=[re.sub(r"\s*/\s*", " / ", s) for s in rc.index]
lab=[ (s if len(s)<=42 else s[:40]+"…") for s in lab]
cd=int(rc.sum())
hbars("04_reasons", lab, rc.values,
      "Stated reasons for the closed door",
      f"The {cd} human replies that named an explicit refusal reason",
      fmt="{:.0f}",
      valuesuffix=[f"  ({100*v/cd:.0f}%)" for v in rc.values],
      figsize=(9.8,4.6))

# ============================================================ 05 language + behaviour
def wf(word):
    # the private reply texts are not published; each marker is a pre-computed YES/NO column
    col = {"we wish":"word_we_wish","success":"word_success","good luck":"word_good_luck","team":"word_team",
           "curator":"Is the word ‘curator’ used?","curatorial":"word_curatorial","director":"word_director","committee":"word_committee"}[word]
    return (H[col]=="YES").sum()
markers=[("“unfortunately”", (H["Is the word ‘unfortunately’ used?"]=="YES").sum()),
         ("“we wish …”", wf("we wish")),
         ("“success”", wf("success")),
         ("“unsolicited”", (H["Is the word ‘unsolicited’ used?"]=="YES").sum()),
         ("“good luck”", wf("good luck")),
         ("Personalised (used my name)", (H["Personalisation in human reply"]=="YES").sum()),
         ("Offered advice / a redirect", (H["Was the advice"]=="YES").sum()),
         ("Kept proposal on file", (H["Promise to keep the proposal on file"]=="YES").sum())]
lab=[m[0] for m in markers]; val=[m[1] for m in markers]
hbars("05_language", lab, val,
      "The language and behaviour of a reply",
      f"Markers across the {hum} human replies",
      valuesuffix=[f"  ({100*v/hum:.0f}%)" for v in val],
      figsize=(9.6,4.8))

# ============================================================ 13 vocab expanded
vocab=[("“unfortunately”", (H["Is the word ‘unfortunately’ used?"]=="YES").sum()),
       ("“we wish”", wf("we wish")),
       ("“success”", wf("success")),
       ("“team”", wf("team")),
       ("“good luck”", wf("good luck")),
       ("“curator”", wf("curator")),
       ("“unsolicited”", (H["Is the word ‘unsolicited’ used?"]=="YES").sum()),
       ("“programme” / “program”", (H["word_programme"]=="YES").sum()),
       ("“curatorial”", wf("curatorial")),
       ("“director”", wf("director")),
       ("“committee”", wf("committee"))]
vocab=sorted(vocab, key=lambda t:-t[1])
lab=[m[0] for m in vocab]; val=[m[1] for m in vocab]
hbars("13_vocab_expanded", lab, val,
      "The broader vocabulary of the gate",
      f"Word markers across the {hum} human replies — the refusal speaks in the passive plural",
      valuesuffix=[f"  ({100*v/hum:.1f}%)" for v in val],
      figsize=(9.6,5.6))

# ============================================================ 06 response time
hrs=H["Response_hours"].dropna()
fig, ax = plt.subplots(figsize=(9.8,5.0))
bins=np.logspace(np.log10(max(0.4,hrs.min())), np.log10(hrs.max()), 26)
ax.hist(hrs, bins=bins, color=PINK_SOFT, edgecolor="white")
ax.set_xscale("log")
med=hrs.median(); q1=hrs.quantile(.25)
ax.axvline(med, color=PINK, lw=2); ax.text(med*1.05, ax.get_ylim()[1]*0.92, f"median {med:.0f} h", color=PINK, fontweight="bold", fontsize=10)
ax.axvline(q1, color=INK, lw=1.2, ls="--"); ax.text(q1*0.55, ax.get_ylim()[1]*0.78, f"q1 {q1:.1f} h", color=INK, fontsize=9)
ticks=[1,6,24,24*7,24*30,24*120]; tl=["1 h","6 h","1 day","1 week","1 month","4 months"]
ax.set_xticks(ticks); ax.set_xticklabels(tl, fontsize=9.5)
ax.set_xlabel("Time from my email to the human reply (log scale)")
ax.set_ylabel("Number of replies")
within=lambda h:(hrs<=h).sum()
title(ax,"When a reply comes, it comes fast",
      f"{within(5)} within 5 h · {within(24)} within a day · {within(24*7)} within a week · of {len(hrs)}")
fig.tight_layout(); save(fig,"06_response_time")

# ============================================================ 08 day of week
order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
out_d=r["time of my letter"].dt.day_name().value_counts().reindex(order).fillna(0)
rep_d=H["Response time"].dt.day_name().value_counts().reindex(order).fillna(0)
fig, ax = plt.subplots(figsize=(9.8,5.0))
x=np.arange(7)
ax.bar(x-0.2, out_d.values, 0.4, color=PINK_SOFT, label="Letters sent")
ax.set_ylabel("Letters sent", color=MUTE); ax.set_ylim(0, out_d.max()*1.16)
for xi,v in zip(x, out_d.values): ax.text(xi-0.2, v+8, f"{int(v)}", ha="center", fontsize=8, color=MUTE)
ax2=ax.twinx(); ax2.spines["top"].set_visible(False)
ax2.bar(x+0.2, rep_d.values, 0.4, color=PINK, label="Human replies")
ax2.set_ylabel("Human replies", color=PINK); ax2.set_ylim(0, rep_d.max()*1.25)
for xi,v in zip(x, rep_d.values): ax2.text(xi+0.2, v+0.6, f"{int(v)}", ha="center", fontsize=8.5, color=PINK, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels([d[:3] for d in order])
h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, frameon=False, fontsize=10, loc="upper right")
title(ax, "Wednesday is the day they write back", "When letters went out (left axis) vs when human replies arrived (right axis)")
fig.tight_layout(); save(fig,"08_dow")

# ============================================================ 12 ooo
ooo=r[r["ooo_flag"]==True]
om=ooo["Automatic reply time"].dt.month.value_counts().sort_index()
months={1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
om=om.reindex(range(1,13)).fillna(0)
fig, ax = plt.subplots(figsize=(9.6,4.6))
x=np.arange(12)
cols=[PINK if m==8 else PINK_SOFT for m in range(1,13)]
ax.bar(x, om.values, color=cols, width=0.72)
for xi,v in zip(x, om.values):
    if v>0: ax.text(xi, v+0.3, f"{int(v)}", ha="center", fontsize=9.5, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels([months[m] for m in range(1,13)])
ax.set_ylabel("Out-of-office auto-replies")
tot=int(ooo.shape[0]); aug=int(om.get(8,0))
title(ax,"Vacation season is visible in the inbox",
      f"{tot} of {int(AUTO.shape[0])} auto-replies were out-of-office — {100*aug/tot:.0f}% arrived in August")
fig.tight_layout(); save(fig,"12_ooo")

# ============================================================ 07 timeline
sent_m=r.groupby(r["time of my letter"].dt.to_period("M")).size()
pf_m=r[r["Positive feedback on my technique"]=="YES"].groupby(r[r["Positive feedback on my technique"]=="YES"]["Response time"].dt.to_period("M")).size()
hum_m=r[HUM].groupby(r[HUM]["Response time"].dt.to_period("M")).size()
idx=sorted(set(sent_m.index)|set(pf_m.index)|set(hum_m.index))
labels=[str(p) for p in idx]
sv=[sent_m.get(p,0) for p in idx]; pv=[pf_m.get(p,0) for p in idx]; hvv=[hum_m.get(p,0) for p in idx]
fig, ax=plt.subplots(figsize=(9.8,5.0))
x=np.arange(len(idx))
ax.bar(x, sv, color=PINK_PALE, width=0.7, label="Letters sent")
ax.set_ylabel("Letters sent", color=MUTE); ax.set_ylim(0, max(sv)*1.16)
ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
ax2=ax.twinx(); ax2.spines["top"].set_visible(False)
ax2.plot(x, hvv, "-o", color=PINK_MID, lw=2, ms=4, label="Human replies (by arrival)")
ax2.plot(x, pv, "-o", color=PINK, lw=2.4, ms=5, label="Positive replies (by arrival)")
mi=int(np.argmax(pv))
ax2.annotate(f"Sept: {pv[mi]} positive", (x[mi], pv[mi]), textcoords="offset points",
             xytext=(6,10), fontsize=9.5, color=PINK, fontweight="bold")
ax2.set_ylabel("Replies", color=PINK); ax2.set_ylim(0, max(max(hvv),max(pv))*1.4)
h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, frameon=False, fontsize=9.5, loc="upper left")
title(ax, "Timeline of a one-person experiment", "Monthly outreach volume and the replies it produced")
fig.tight_layout(); save(fig,"07_timeline")

# ============================================================ 14 promises
prom=(r["Is there a promise to reply in automatic reply?"]=="YES").sum()
kept=(r["Is there a promised reply?"]=="YES").sum()
funnel("14_promises",
       [("Automatic replies", int(AUTO.shape[0])),
        ("…promised a human reply", int(prom)),
        ("…a human actually replied", int(kept))],
       "“We will get back to you”: kept one time in five",
       f"{prom} of {int(AUTO.shape[0])} auto-replies promised a follow-up — {kept} delivered ({100*kept/prom:.0f}%)")

# ============================================================ 16 bounce
src2=r.copy(); src2["Source"]=src2["Source"].fillna("(none)")
bg=src2.groupby("Source").agg(sent=("id","count"),
        bounced=("Delivered", lambda s:(s=="NO").sum()))
bg["b%"]=100*bg["bounced"]/bg["sent"]
bg=bg[bg["sent"]>=40].sort_values("b%", ascending=False)
overall=100*(r["Delivered"]=="NO").sum()/N
fig, ax=plt.subplots(figsize=(9.6,5.0))
y=np.arange(len(bg))[::-1]
ax.barh(y, bg["b%"], height=0.62, color=[PINK if v>=overall else PINK_SOFT for v in bg["b%"]])
for yi,(nm,row) in zip(y, bg.iterrows()):
    ax.text(row["b%"]+0.08, yi, f"{row['b%']:.1f}%  (n={int(row['sent']):,})", va="center", fontsize=9.5, fontweight="bold")
ax.axvline(overall, color=INK, ls="--", lw=1.2)
ax.text(overall, len(bg)-0.3, f" overall {overall:.1f}%", color=INK, fontsize=9.5, va="top")
ax.set_yticks(y); ax.set_yticklabels(bg.index, fontsize=10.5)
ax.set_xticks([]); ax.set_xlim(0, bg["b%"].max()*1.30)
for s in ["bottom","left"]: ax.spines[s].set_visible(False)
title(ax,"Bounce rate: a cleanliness check",
      "Undeliverable share by contact source — curated lists are far cleaner than scraped directories")
fig.tight_layout(); save(fig,"16_bounce")

# ============================================================ 17 flagship coverage
FLAGSHIPS = {
 'United Kingdom':['Tate','National Gallery','National Portrait Gallery','Royal Academy','Serpentine','Hayward Gallery','Whitechapel Gallery','ICA','White Cube','Gagosian','Hauser','Lisson','Sadie Coles','Thomas Dane','Stephen Friedman','Victoria Miro'],
 'United States':['MoMA','Museum of Modern Art','Met','Metropolitan Museum','Guggenheim','Whitney','SFMOMA','LACMA','Art Institute of Chicago','Walker','Dia','New Museum','MOCA','Gagosian','Pace','David Zwirner','Hauser','Marian Goodman','Matthew Marks','Lehmann Maupin','Salon 94'],
 'Germany':['Neue Nationalgalerie','Alte Nationalgalerie','Hamburger Bahnhof','Museum Ludwig','Kunstsammlung NRW','Haus der Kunst','Pinakothek','Berlinische Galerie','Schirn','Städel','Städel Museum','Deichtorhallen','Museum Folkwang','Documenta','Sprüth Magers','Esther Schipper','Galerie Max Hetzler','Galerie Eigen','Buchholz'],
 'France':['Louvre','Centre Pompidou',"Musée d'Orsay",'Jeu de Paume','Palais de Tokyo','Fondation Cartier','Fondation Louis Vuitton','Galerie Perrotin','Perrotin','Kamel Mennour','Thaddaeus Ropac','Chantal Crousel','Lafayette Anticipations'],
 'Italy':['Uffizi','Venice Biennale','Biennale di Venezia','Palazzo Grassi','Fondazione Prada','Pinault','Museo del Novecento','MAXXI','Castello di Rivoli','GAM','Massimo de Carlo','Continua'],
 'Spain':['Prado','Reina Sofía','Reina Sofia','Thyssen','Guggenheim Bilbao','MACBA','CaixaForum','Museo Sorolla','IVAM','Mario Sequeira','Juana de Aizpuru'],
 'Switzerland':['Kunsthaus Zürich','Kunsthaus Zurich','Fondation Beyeler','Kunstmuseum Basel','Kunstmuseum Bern','MAMCO','Art Basel','Hauser','Galerie Eva Presenhuber'],
 'Netherlands':['Rijksmuseum','Stedelijk','Van Gogh Museum','Mauritshuis','Kunsthal','Kröller-Müller','Kroller-Muller','Bonnefanten','Boijmans','Annet Gelink','Grimm'],
 'Japan':['Mori Art Museum','National Art Center','National Museum of Modern Art','Tokyo Metropolitan','Museum of Contemporary Art Tokyo','Taka Ishii','Scai The Bathhouse','Ota Fine Arts'],
 'China':['UCCA','Long Museum','Power Station of Art','M Plus','M+','Rockbund','ShanghART','Long March Space'],
 'Australia':['NGA','National Gallery of Australia','Art Gallery of New South Wales','NGV','National Gallery of Victoria','MCA','Museum of Contemporary Art','Art Gallery of Western Australia','GOMA','Roslyn Oxley9','Anna Schwartz'],
 'Austria':['Belvedere','Albertina','MUMOK','Kunsthistorisches','Leopold','mumok','Secession','Galerie Thaddaeus Ropac'],
 'Belgium':['Bozar','S.M.A.K.','SMAK','WIELS','Musée Magritte','M HKA','M-HKA','BAM','Xavier Hufkens','Axel Vervoordt'],
 'Canada':['National Gallery of Canada','Art Gallery of Ontario','AGO','Musée des Beaux-Arts','Montreal Museum of Fine Arts','MOCA Toronto','Polygon'],
 'Brazil':['MASP','MAM','Pinacoteca','Inhotim',"Fortes D'Aloia",'Mendes Wood','Luisa Strina'],
}
def hay(s): return re.sub(r"\s+"," ",str(s).lower()).strip()
covrows=[]
for country, fl in FLAGSHIPS.items():
    names=[hay(n) for n in r[r["Country"]==country]["NAME"].dropna()]
    found=sum(1 for f in fl if any(re.search(r"(?<![a-z])"+re.escape(f.lower())+r"(?![a-z])", nm) for nm in names))
    covrows.append((country, 100*found/len(fl), found, len(fl)))
covrows.sort(key=lambda t:-t[1])
lab=[f"{c}" for c,_,_,_ in covrows]
val=[v for _,v,_,_ in covrows]
suf=[f"  ({fo}/{to})" for _,_,fo,to in covrows]
overall_cov=100*sum(fo for *_,fo,_ in [(c,v,fo,to) for c,v,fo,to in covrows])/sum(to for *_,to in [(c,v,fo,to) for c,v,fo,to in covrows])
hbars("17_top5", lab, val,
      "Did the list actually reach the flagships?",
      f"Share of each country's reference flagship institutions present in the dataset — overall ≈ {overall_cov:.0f}%",
      fmt="{:.0f}", unit="%", valuesuffix=suf, figsize=(9.6,6.4),
      highlight=[i for i,v in enumerate(val) if v>=80])

# ============================================================ 18 lengths
auto_len=r["auto_reply_chars"].dropna()
hsig=H["reply_chars_with_signature"].dropna()
hstr=H["reply_chars"].dropna()
groups=[("Auto-replies\n(machine)", auto_len),
        ("Human reply\n(with signature)", hsig),
        ("Human reply\n(signature stripped)", hstr)]
stats=["median","mean","90th pct"]
fig, ax=plt.subplots(figsize=(9.6,5.0))
x=np.arange(len(groups)); w=0.26
cols=[PINK_SOFT, PINK_MID, PINK]
for j,st in enumerate(stats):
    vals=[ (s.median() if st=="median" else s.mean() if st=="mean" else s.quantile(.9)) for _,s in groups]
    ax.bar(x+(j-1)*w, vals, w, color=cols[j], label=st)
    for xi,v in zip(x, vals): ax.text(xi+(j-1)*w, v+40, f"{v:,.0f}", ha="center", fontsize=8.5, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels([g[0] for g in groups])
ax.set_ylabel("Characters"); ax.legend(frameon=False, fontsize=10)
title(ax,"How long the letters are",
      "Character counts — software is wordier than the curator; half the human letter is signature")
fig.tight_layout(); save(fig,"18_lengths")

# ============================================================ 20 lengths by country
lc=H.groupby("Country")["reply_chars"].agg(["count","median","mean"])
lc=lc[lc["count"]>=5].sort_values("median")
fig, ax=plt.subplots(figsize=(9.6,5.4))
y=np.arange(len(lc))[::-1]
ax.barh(y, lc["median"], height=0.6, color=PINK, label="median")
ax.plot(lc["mean"].values, y, "o", color=INK, ms=6, label="mean")
# The label goes after whichever mark is further right. It used to sit just
# past the end of the bar, but the mean of a skewed distribution is almost
# always to the right of its median, so the dot landed on top of the text in
# every country where replies are long-tailed — which is most of them.
gap = max(lc["median"].max(), lc["mean"].max()) * 0.02
for yi,(nm,row) in zip(y, lc.iterrows()):
    ax.text(max(row["median"], row["mean"]) + gap, yi,
            f"{int(row['median'])}  (n={int(row['count'])})",
            va="center", fontsize=9.5, fontweight="bold")
ax.set_yticks(y); ax.set_yticklabels(lc.index, fontsize=10.5)
ax.set_xlabel("Characters (signature stripped)")
ax.legend(frameon=False, fontsize=10, loc="upper right")
ax.set_xlim(0, max(lc["median"].max(), lc["mean"].max())*1.28)
title(ax,"Length of the human reply by country",
      "Median (bar) and mean (dot) reply length, signature removed. Countries with ≥ 5 human replies.")
fig.tight_layout(); save(fig,"20_lengths_by_country")

# ============================================================ 21 structure funnel
slots=[("Greeting", H["has_greeting"].sum()),
       ("Post-greeting thank-you", H["has_thanks"].sum()),
       ("Body (the “no”)", len(H)),
       ("Pre-closing well-wishing", H["has_wish"].sum()),
       ("Closing / sign-off", H["has_closing"].sum())]
lab=[s[0] for s in slots]; val=[100*s[1]/len(H) for s in slots]
fig, ax=plt.subplots(figsize=(9.6,4.4))
y=np.arange(len(slots))[::-1]
cols=[PINK if v>=85 else (PINK_MID if v>=60 else PINK_SOFT) for v in val]
ax.barh(y, val, height=0.62, color=cols)
for yi,v,s in zip(y,val,slots):
    ax.text(v+0.6, yi, f"{v:.0f}%  ({int(s[1])})", va="center", fontsize=10, fontweight="bold")
ax.set_yticks(y); ax.set_yticklabels(lab, fontsize=11)
ax.set_xticks([]); ax.set_xlim(0,112)
for s in ["bottom","left"]: ax.spines[s].set_visible(False)
title(ax,"Five slots, mostly filled",
      "Share of the 272 human replies that include each slot — well-wishing is the one they skip")
fig.tight_layout(); save(fig,"21_structure_funnel")

# ============================================================ 22 pattern combos
pat=H["gtwc_pattern"].value_counts()
lab=list(pat.index); val=list(pat.values)
hbars("22_pattern_combos", lab, val,
      "Which slots travel together",
      "All G/T/W/C patterns across the 272 replies — two dominate: full, and full-minus-wishing",
      valuesuffix=[f"  ({100*v/len(H):.0f}%)" for v in val], color=PINK, figsize=(9.4,5.0))

# ============================================================ 23 greeting formula
gf=H["Greeting formula"].str.strip().value_counts()
gf=gf[gf>=1]
hbars("23_greeting_breakdown", list(gf.index), list(gf.values),
      "How they begin",
      "Greeting formula across the 272 replies (outgoing letters all opened “Dear”, which inflates it)",
      valuesuffix=[f"  ({100*v/len(H):.0f}%)" if 100*v/len(H)>=1 else "" for v in gf.values],
      figsize=(9.4,4.8))

# ============================================================ 24 personalization
def name_bucket(s):
    if pd.isna(s) or str(s).strip()=="" : return "No name"
    s=str(s).strip()
    if s in ("Pavlo","Pavlo Kulyk","Kulyk"): return s
    return "Mangled"
pb=H["Greeting personalization"].map(name_bucket).value_counts()
orderp=["Pavlo","Pavlo Kulyk","Kulyk","No name","Mangled"]
pb=pb.reindex([o for o in orderp if o in pb.index])
hbars("24_personalization", list(pb.index), list(pb.values),
      "The name the gallery actually used",
      "First name only in two-thirds of replies",
      valuesuffix=[f"  ({100*v/len(H):.0f}%)" for v in pb.values],
      figsize=(9.2,3.9))

# ============================================================ 25 punctuation
pu=H["Punctuation after Greeting phrase"].fillna("—").replace({",":"comma  ,", "!":"exclamation  !"})
pc=pu.value_counts()
pc.index=[ ("none (line break)" if i=="—" else i) for i in pc.index]
hbars("25_punctuation", list(pc.index), list(pc.values),
      "What follows the greeting word",
      "The comma is law",
      valuesuffix=[f"  ({100*v/len(H):.0f}%)" for v in pc.values],
      figsize=(9.0,3.2))

# ============================================================ 26 top thanks
tk=H["Post-greeting thank-you phrase (short)"].dropna().value_counts().head(8)
hbars("26_top_thanks", list(tk.index), list(tk.values),
      "What they thank you for",
      "Top opening thank-you phrases — the thanks is for the email, not the work",
      valuesuffix=[f"  ({100*v/238:.0f}%)" for v in tk.values],
      figsize=(9.6,4.6))

# ============================================================ 28 wish phrases
wp=H["Pre-closing well-wishing phrase"].dropna().str.lower()
themes=[("“best”","best"),("“future”/“journey”","future|journey"),
        ("“your work”/“projects”","your work|your project|practice"),
        ("“luck”","luck"),("“success”","success")]
lab=[t[0] for t in themes]; val=[wp.str.contains(t[1], regex=True).sum() for t in themes]
hbars("28_wish_phrases", lab, val,
      "What they wish you, when they wish",
      f"Recurring themes inside the {len(wp)} well-wishing lines",
      valuesuffix=[f"  ({100*v/len(wp):.0f}%)" for v in val],
      figsize=(9.4,3.9))

# ============================================================ 27 top closings
cl=H["Closing phrase"].dropna().str.strip().str.lower().value_counts().head(10)
lab=[s.title() for s in cl.index]
hbars("27_top_closings", lab, list(cl.values),
      "How they sign off",
      "Top declared closing phrases — the ‘regards’ family is over half of all sign-offs",
      valuesuffix=[f"  ({100*v/244:.0f}%)" for v in cl.values],
      figsize=(9.4,5.0))

# ============================================================ 30 honorific by country
hc=H.copy(); hc["hon"]=hc["Greeting honorific"].notna()
cnt=hc.groupby("Country").agg(n=("id","count"), hon=("hon","sum"))
cnt=cnt[cnt["n"]>=10]; cnt["p"]=100*cnt["hon"]/cnt["n"]
cnt=cnt.sort_values("p", ascending=False)
hbars("30_honorific_by_country", list(cnt.index), list(cnt["p"].values),
      "The geography of formality",
      "Share of replies opening with an honorific (Mr / Sir / Herr). Countries with ≥ 10 human replies.",
      fmt="{:.0f}", unit="%", valuesuffix=[f"  (n={int(x)})" for x in cnt["n"]],
      figsize=(9.2,4.0))

# ============================================================ 31 formality by country
fc=H.copy()
cn=fc.groupby("Country").size(); keep=cn[cn>=10].index
fc=fc[fc["Country"].isin(keep)]
ct2=pd.crosstab(fc["Country"], fc["greeting_bucket"], normalize="index")*100
for c in ["Dear","Hi / Hey","Hello","Other"]:
    if c not in ct2: ct2[c]=0
ct2=ct2[["Dear","Hi / Hey","Hello","Other"]].sort_values("Dear")
fig, ax=plt.subplots(figsize=(9.6,4.6))
y=np.arange(len(ct2))
left=np.zeros(len(ct2))
segcols={"Dear":PINK,"Hi / Hey":PINK_MID,"Hello":PINK_SOFT,"Other":GREY}
for c in ["Dear","Hi / Hey","Hello","Other"]:
    ax.barh(y, ct2[c], left=left, color=segcols[c], label=c, height=0.66)
    for yi,v,l in zip(y, ct2[c], left):
        if v>=8: ax.text(l+v/2, yi, f"{v:.0f}", ha="center", va="center", fontsize=9, color="white" if c in ("Dear","Hi / Hey") else INK)
    left+=ct2[c].values
ax.set_yticks(y); ax.set_yticklabels(ct2.index, fontsize=11)
ax.set_xlim(0,100); ax.set_xlabel("% of the country's human replies", labelpad=10)
# The legend sat at -0.22 and the axis label sits just below the ticks, so
# the two occupied the same strip. The label is given room of its own with
# labelpad and the legend is moved below it; save() writes with a tight
# bounding box, so the figure grows to fit rather than clipping.
ax.legend(frameon=False, ncol=4, fontsize=9.5, loc="lower center",
          bbox_to_anchor=(0.5, -0.34))
title(ax,"Willingness to mirror the “Dear” opener",
      "Greeting formula by country (every outgoing letter opened “Dear”)")
fig.tight_layout(); save(fig,"31_formality_by_country")

# ============================================================ 29 body by completeness
fig, ax=plt.subplots(figsize=(9.6,5.0))
data=[H[H["n_structural_slots"]==k]["reply_words"].dropna().values for k in range(5)]
bp=ax.boxplot(data, positions=range(5), widths=0.6, patch_artist=True, showfliers=False)
for patch in bp["boxes"]: patch.set_facecolor(PINK_SOFT); patch.set_edgecolor(PINK)
for med in bp["medians"]: med.set_color(PINK); med.set_linewidth(2)
means=[np.mean(d) if len(d) else 0 for d in data]
ax.plot(range(5), means, "o-", color=INK, lw=1.5, ms=6, label="mean")
for k,m in enumerate(means): ax.text(k, m+3, f"{m:.0f}", ha="center", fontsize=9, fontweight="bold")
ax.set_xticks(range(5)); ax.set_xticklabels([f"{k} slots\n(n={len(data[k])})" for k in range(5)])
ax.set_ylabel("Reply length (words)"); ax.legend(frameon=False, fontsize=10)
title(ax,"Polish predicts length",
      "Reply length in words by number of courtesy slots present — nobody writes a long, bare letter")
fig.tight_layout(); save(fig,"29_body_by_completeness")

# ============================================================ 32 composite email
def modal(series):
    s=series.dropna()
    return s.value_counts().index[0] if len(s) else ""
greet=f"Dear {modal(H['Greeting personalization'])},"
thank=modal(H["Post-greeting thank-you phrase (short)"])+"."
wish=modal(H["Pre-closing well-wishing phrase"])
wish=wish[0].upper()+wish[1:] if wish else "We wish you all the best"
close=modal(H["Closing phrase"])+","
fig, ax=plt.subplots(figsize=(8.6,6.4)); ax.axis("off")
card=FancyBboxPatch((0.06,0.06),0.88,0.86, boxstyle="round,pad=0.02,rounding_size=0.03",
                    linewidth=1.2, edgecolor=LINE, facecolor="white", mutation_aspect=1)
ax.add_patch(card)
lines=[(greet, INK, 15, "bold"),
       (thank, INK, 13, "normal"),
       ("Unfortunately, we are not able to take this forward", "#555", 13, "italic"),
       ("at the moment.", "#555", 13, "italic"),
       (wish+".", INK, 13, "normal"),
       (close, PINK, 14, "bold"),
       ("The Team", MUTE, 12, "normal")]
yy=0.82
for txt,col,fs,style in lines:
    ax.text(0.12, yy, txt, fontsize=fs, color=col, style=("italic" if style=="italic" else "normal"),
            fontweight=("bold" if style=="bold" else "normal"), transform=ax.transAxes)
    yy-=0.11
ax.text(0.12,0.955,"THE COMPOSITE REJECTION", fontsize=10.5, color=PINK, fontweight="bold",
        transform=ax.transAxes)
ax.text(0.12,0.0,"Each line is the single most frequent phrase in its slot across the 272 human replies.",
        fontsize=9, color=MUTE, transform=ax.transAxes)
save(fig,"32_composite_email")

# ============================================================ 33 mangled names
mang=H[H["Greeting personalization"].map(name_bucket)=="Mangled"]["Greeting personalization"].value_counts()
n=len(mang)
# Layout in points: each card is as wide as its name (so "Thierry Pavlo Kulyk" no longer
# spills into the next card), cards flow left to right and wrap only past 700 pt.
_MN_GAP, _MN_CARD_H, _MN_ROW_GAP, _MN_TOP = 10, 60, 12, 52
_mf=plt.figure(figsize=(4,1), dpi=100); _mr=_mf.canvas.get_renderer(); _mn_cards=[]
for nm,c in mang.items():
    _tw=_mf.text(0,0,f"“{nm}”", fontsize=12.5, fontweight="bold").get_window_extent(_mr).width*72/_mf.dpi
    _mn_cards.append((f"“{nm}”", f"×{c}", max(104, _tw+36)))
plt.close(_mf)
_mn_rows=[[]]; _mx=0
for cd in _mn_cards:
    if _mn_rows[-1] and _mx+_MN_GAP+cd[2] > 700: _mn_rows.append([]); _mx=0
    _mx += (_MN_GAP if _mn_rows[-1] else 0) + cd[2]; _mn_rows[-1].append(cd)
_mw=max(560, max(sum(cd[2] for cd in rw)+_MN_GAP*(len(rw)-1) for rw in _mn_rows))
_mh=_MN_TOP+len(_mn_rows)*_MN_CARD_H+(len(_mn_rows)-1)*_MN_ROW_GAP+4
fig=plt.figure(figsize=(_mw/72,_mh/72)); ax=fig.add_axes([0,0,1,1])
ax.set_xlim(0,_mw); ax.set_ylim(0,_mh); ax.axis("off")
ax.text(0,_mh-4,"The salutation slips", fontsize=15, fontweight="bold", va="top")
ax.text(0,_mh-30,f"{int(mang.sum())} of 272 personalised replies addressed someone who isn’t quite me",
        fontsize=10.5, color=MUTE, va="top")
_my=_mh-_MN_TOP-_MN_CARD_H
for rw in _mn_rows:
    _mx=0
    for label,cnt,w in rw:
        ax.add_patch(FancyBboxPatch((_mx+1,_my+1), w-2, _MN_CARD_H-2, boxstyle="round,pad=0,rounding_size=6",
                     linewidth=1.1, edgecolor=PINK_SOFT, facecolor=PINK_PALE, clip_on=False))
        ax.text(_mx+w/2, _my+36, label, ha="center", va="center", fontsize=12.5, fontweight="bold", color="#7a1240")
        ax.text(_mx+w/2, _my+15, cnt, ha="center", va="center", fontsize=10, color=MUTE)
        _mx+=w+_MN_GAP
    _my-=_MN_CARD_H+_MN_ROW_GAP
save(fig,"33_mangled_names")

# ============================================ 34 who the encyclopedia writes down
# Three states, because "no article" and "never matched to an entity" are not the
# same claim: the pipeline may only report a zero it actually measured. Colour is
# one pink ramp for the two measured states plus a neutral for the unmeasured one.
IX = r[r["index_type"].notna()].copy()
_we = IX["wikipedia_editions"]
IX["_state"] = np.where(_we.fillna(-1) > 0, "has",
                 np.where(_we.fillna(-1) == 0, "zero", "unknown"))
TYPE_EN = {"MUSEUM":"Museums", "EDUCATION":"Academies & schools",
           "AUCTION_HOUSE":"Auction houses", "FAIR_BIENNIAL":"Fairs & biennials",
           "ART_CENTER":"Art centres", "FOUNDATION_NONPROFIT":"Foundations",
           "ASSOCIATION":"Associations", "COMMERCIAL_GALLERY":"Commercial galleries"}
_ct = (pd.crosstab(IX["index_type"], IX["_state"])
         .reindex(columns=["has","zero","unknown"], fill_value=0))
_n  = _ct.sum(1)
_pc = _ct.div(_n, axis=0) * 100
_pc = _pc.loc[_pc["has"].sort_values(ascending=False).index]

fig, ax = plt.subplots(figsize=(9.6, 0.56*len(_pc) + 2.0))
y = np.arange(len(_pc))[::-1]
_segs = [("has", PINK, "has a Wikipedia article"),
         ("zero", PINK_PALE, "checked, no article"),
         ("unknown", GREY, "no entity to check against")]
_left = np.zeros(len(_pc))
for key, col, lab in _segs:
    v = _pc[key].values
    ax.barh(y, v, left=_left, height=0.66, color=col, label=lab)
    _left = _left + v
for yi, (t, row) in zip(y, _pc.iterrows()):
    if row["has"] >= 7:
        ax.text(row["has"]/2, yi, f"{row['has']:.0f}%", ha="center", va="center",
                fontsize=10.5, fontweight="bold", color="white")
    else:
        ax.text(row["has"] + 1.2, yi, f"{row['has']:.0f}%", ha="left", va="center",
                fontsize=10.5, fontweight="bold", color=INK)
ax.set_yticks(y)
ax.set_yticklabels([f"{TYPE_EN.get(t,t)}  ({int(_n[t]):,})" for t in _pc.index], fontsize=11)
ax.set_xlim(0, 100); ax.set_xticks([])
for s in ["bottom","left"]: ax.spines[s].set_visible(False)
title(ax, "Who the encyclopedia writes down",
      f"Wikipedia coverage by institution type (n = {len(IX):,} of {N:,}); institution count in brackets")
ax.legend(frameon=False, fontsize=9.5, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.20))
fig.text(0.01, -0.055, "Grey is not an absence of fame — it is an absence of measurement: no Wikidata entity "
                       "could be confirmed for that institution, so no article count was ever taken.",
         fontsize=8.5, color=MUTE, ha="left")
save(fig, "34_wiki_gap")

# ============================================ 35 top of field
# Two panels, one shared y-scale, one measure. Never a second axis.
r["_hum"] = HUM
GALM = r["index_type"].eq("COMMERCIAL_GALLERY")
OTHM = r["index_type"].notna() & ~GALM
WE   = r["wikipedia_editions"].fillna(0)
FR   = r["art_fairs"].fillna(0)

def _bins(mask, series, edges):
    out = []
    for lo, hi, lab in edges:
        s = r[mask & series.between(lo, hi)]
        out.append((lab, len(s), int(s["_hum"].sum()),
                    s["_hum"].mean()*100 if len(s) else 0.0))
    return out

_left  = _bins(GALM, FR, [(0,0,"none"),(1,1,"1"),(2,3,"2–3"),(4,6,"4–6"),(7,99,"7+")])
_right = _bins(OTHM, WE, [(0,0,"none"),(1,2,"1–2"),(3,9,"3–9"),(10,29,"10–29"),(30,9999,"30+")])

fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.5), sharey=True)
_ymax = max(v[3] for v in _left + _right) * 1.30
for ax, dat, head, sub in [
        (axes[0], _left,  "Commercial galleries",  "by art fairs exhibited at, of 20"),
        (axes[1], _right, "Everyone else",         "by Wikipedia language editions")]:
    x = np.arange(len(dat))
    cols = [PINK_SOFT]*(len(dat)-1) + [PINK]
    ax.bar(x, [d[3] for d in dat], width=0.62, color=cols)
    for xi, d in zip(x, dat):
        ax.text(xi, d[3] + _ymax*0.030, f"{d[3]:.1f}%", ha="center",
                fontsize=11, fontweight="bold", color=INK)
        ax.text(xi, -_ymax*0.115, f"n={d[1]:,}", ha="center", fontsize=8.5, color=MUTE)
    ax.set_xticks(x); ax.set_xticklabels([d[0] for d in dat], fontsize=10.5)
    ax.set_ylim(0, _ymax); ax.set_yticks([])
    ax.tick_params(axis="x", length=0, pad=6)
    for s in ["left","bottom"]: ax.spines[s].set_visible(False)
    ax.annotate(head, xy=(0,1), xycoords="axes fraction", xytext=(0,18),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=12.5, fontweight="bold", color=INK, annotation_clip=False)
    ax.annotate(sub, xy=(0,1), xycoords="axes fraction", xytext=(0,7),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=10, color=MUTE, annotation_clip=False)
fig.subplots_adjust(top=0.70, bottom=0.10, left=0.03, right=0.985, wspace=0.10)
fig.text(0.012, 0.975, "Nothing happens until the very top", ha="left", va="top",
         fontsize=15, fontweight="bold", color=INK)
fig.text(0.012, 0.905, "Human reply rate. Two populations, two unrelated instruments, "
                       "the same flat-then-jump shape.", fontsize=10.5, color=MUTE,
         ha="left", va="top")
save(fig, "35_top_of_field")

print("\nDONE.")
