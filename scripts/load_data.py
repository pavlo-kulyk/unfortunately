"""Loads the public dataset and exposes it under the column names the chart code uses."""
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "unfortunately_dataset.csv"
OUT = HERE.parent / "charts"
OUT.mkdir(exist_ok=True)

# public name -> name used inside the report-chart code
LEGACY = {"institution":"NAME","sent_at":"time of my letter","sent":"Has the email been sent","delivered":"Delivered","any_reply":"Is there an answer",
 "auto_reply":"Was there an automatic reply?","auto_reply_at":"Automatic reply time","auto_reply_days":"Automatic PERIOD","human_reply":"Human reply (YES) or automatic reply (NO)",
 "personalised":"Personalisation in human reply","human_reply_at":"Response time","human_reply_days":"PERIOD","promise_made":"Is there a promise to reply in automatic reply?",
 "promise_max_days":"How many days did they promise to reply?","promise_kept":"Is there a promised reply?","out_of_office":"ooo_flag","cooperation_agreed":"Is there agreement on cooperation?",
 "positive_feedback":"Positive feedback on my technique","word_unfortunately":"Is the word ‘unfortunately’ used?","word_unsolicited":"Is the word ‘unsolicited’ used?","word_curator":"Is the word ‘curator’ used?",
 "refusal_reason_raw":"Reasons","refusal_reason":"Reason category","advice_given":"Was the advice","keep_on_file":"Promise to keep the proposal on file",
 "greeting":"Greeting","greeting_formula":"Greeting formula","greeting_honorific":"Greeting honorific","greeting_name_used":"Greeting personalization","greeting_punctuation":"Punctuation after Greeting phrase",
 "thank_you_phrase":"Post-greeting thank-you phrase (short)","well_wishing_phrase":"Pre-closing well-wishing phrase","closing_phrase":"Closing phrase",
 "human_reply_hours":"Response_hours","auto_reply_hours":"AutoReply_hours","country":"Country","city":"City","region":"Region","source":"Source","url":"URL",
 "reference_flagship":"flagship","reference_flagship_match":"flagship_match"}

def load_public():
    """The dataset exactly as published (public column names)."""
    return pd.read_csv(DATA, low_memory=False)

def load():
    """The dataset under the legacy column names used by charts_report.py."""
    r = load_public().rename(columns=LEGACY)
    r["ooo_flag"] = r["ooo_flag"].eq("YES")
    return r

def load_article():
    """The dataset under the raw-sheet column names used by charts_article.py."""
    p = load_public()
    P = "Automatic reply - Promise to reply"
    d = pd.DataFrame({"ID": p["id"], "NAME": p["institution"], "Country": p["country"], "Region": p["region"],
        "Delivered": p["delivered"], "Is there an answer": p["any_reply"], "Was there an automatic reply?": p["auto_reply"],
        "Human reply (YES) or automatic reply (NO)": p["human_reply"], "Response_hours": p["human_reply_hours"],
        "PF_positive_feedback": p["positive_feedback"], "COOP_agreement": p["cooperation_agreed"],
        "Is the word ‘unfortunately’ used?": p["word_unfortunately"],
        "GTWC: Greeting": p["greeting"], "GTWC: Greeting personalization": p["greeting_name_used"],
        "GTWC: Post-greeting thank-you phrase (short)": p["thank_you_phrase"],
        "GTWC: Pre-closing well-wishing phrase": p["well_wishing_phrase"], "GTWC: Closing phrase": p["closing_phrase"],
        "CLOSED DOORS reason flagged: YES/NO": p["refusal_reason"].notna().map({True: "YES", False: "NO"}).where(p["human_reply"].eq("YES")),
        "CLOSED DOORS SUBCATEGORY": p["refusal_reason"],
        P: p["promise_made"], P + " - Reply period max days (approx.)": p["promise_max_days"],
        P + " - Timeliness category": p["promise_timeliness"],
        "days_overdue": p["promise_days_overdue_asof_2026-11-16"], "reply_words": p["reply_words"]})
    return d
