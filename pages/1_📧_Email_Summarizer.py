"""Email Summarizer page — action-oriented inbox triage."""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

# Add parent dir so shared/ is importable
_DASHBOARD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, _DASHBOARD_DIR)

from shared.styling import apply_theme
from shared.tool_runner import (
    load_email_config,
    load_recent_runs,
    run_email_summary,
    save_email_config,
)

logger = logging.getLogger(__name__)

apply_theme()

# ── Inject triage card CSS ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    .triage-card {
        background: var(--secondary-background-color, #1a1a20);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #555;
    }
    .triage-card.urgency-high { border-left-color: #ef4444; }
    .triage-card.urgency-medium { border-left-color: #eab308; }
    .triage-card.urgency-low { border-left-color: #eab308; }
    .triage-card.urgency-fyi { border-left-color: #6b7280; }

    .triage-card .card-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 0.3rem;
    }
    .triage-card .sender {
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-color, #e8e8ea);
    }
    .triage-card .time {
        font-size: 0.8rem;
        color: rgba(232, 232, 234, 0.5);
    }
    .triage-card .subject {
        font-size: 0.85rem;
        color: rgba(232, 232, 234, 0.75);
        margin-bottom: 0.5rem;
    }
    .triage-card .want {
        font-size: 0.9rem;
        color: var(--text-color, #e8e8ea);
        margin-bottom: 0.3rem;
    }
    .triage-card .deadline {
        font-size: 0.8rem;
        color: #eab308;
        margin-bottom: 0.3rem;
    }
    .triage-card .draft-label {
        font-size: 0.75rem;
        color: rgba(232, 232, 234, 0.45);
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }
    .triage-card .draft {
        font-size: 0.85rem;
        color: rgba(232, 232, 234, 0.85);
        background: rgba(124, 58, 237, 0.08);
        border-left: 2px solid rgba(124, 58, 237, 0.3);
        padding: 0.5rem 0.8rem;
        border-radius: 4px;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Header ──────────────────────────────────────────────────────────────
st.markdown("# 📧 Inbox Triage")
st.markdown("*What needs a reply in the last 24 hours.*")
st.markdown("---")

# ── Sidebar: Config Editor ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Allowlist / Blocklist")
    st.caption("Edit the lists below and click Save. One entry per line.")

    raw_config = load_email_config()

    allowlist_domains = st.text_area(
        "Allowlist domains",
        value="\n".join(raw_config.get("allowlist_domains", [])),
        height=80,
        key="allow_domains",
    )
    allowlist_addresses = st.text_area(
        "Allowlist addresses",
        value="\n".join(raw_config.get("allowlist_addresses", [])),
        height=80,
        key="allow_addrs",
    )
    blocklist_domains = st.text_area(
        "Blocklist domains",
        value="\n".join(raw_config.get("blocklist_domains", [])),
        height=80,
        key="block_domains",
    )
    blocklist_addresses = st.text_area(
        "Blocklist addresses",
        value="\n".join(raw_config.get("blocklist_addresses", [])),
        height=80,
        key="block_addrs",
    )

    if st.button("Save changes", key="save_config"):
        try:
            updated = {
                **raw_config,
                "allowlist_domains": [d.strip() for d in allowlist_domains.strip().split("\n") if d.strip()],
                "allowlist_addresses": [a.strip() for a in allowlist_addresses.strip().split("\n") if a.strip()],
                "blocklist_domains": [d.strip() for d in blocklist_domains.strip().split("\n") if d.strip()],
                "blocklist_addresses": [a.strip() for a in blocklist_addresses.strip().split("\n") if a.strip()],
            }
            json.loads(json.dumps(updated))
            save_email_config(updated)
            st.success("Config saved.")
        except (ValueError, TypeError) as e:
            st.error(f"Invalid config: {e}")

    st.markdown("---")
    st.markdown("### Recent Runs")
    recent = load_recent_runs(5)
    if recent:
        for run in recent:
            ts = run.get("timestamp", "")[:16].replace("T", " ")
            wd = run.get("window_desc", "")
            kept = run.get("kept", 0)
            nr = run.get("needs_reply", "?")
            st.caption(f"**{ts}** — {wd} ({kept} kept, {nr} reply)")
    else:
        st.caption("No runs yet.")

# ── Controls Form ───────────────────────────────────────────────────────
with st.form("email_form"):
    col1, col2 = st.columns(2)
    with col1:
        show_omitted = st.toggle("Show omitted senders", value=True, key="show_omitted")
    with col2:
        use_cache = st.toggle("Use cache", value=True, key="use_cache")

    submitted = st.form_submit_button("Run triage", type="primary", use_container_width=True)

# ── Render a triage card ───────────────────────────────────────────────


def _render_card(email_data: dict, urgency_class: str, show_draft: bool = True) -> None:
    """Render a single triage card for an email.

    Args:
        email_data: Parsed email dict with 'triage' key.
        urgency_class: CSS class for border colour (urgency-high, urgency-medium, etc.).
        show_draft: Whether to show the draft reply section.
    """
    t = email_data.get("triage", {})
    time_str = email_data["date"].strftime("%H:%M")
    msg_id = email_data.get("message_id", "")
    gmail_url = f"https://mail.google.com/mail/u/0/#inbox/{msg_id}"
    what_they_want = t.get("what_they_want", "N/A")
    deadline = t.get("deadline")
    draft = t.get("draft_reply")

    # Build card HTML
    deadline_html = f'<div class="deadline">🕐 Deadline: {deadline}</div>' if deadline else ""
    draft_html = ""
    if show_draft and draft:
        escaped_draft = draft.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        draft_html = f"""
        <div class="draft-label">✏️ Draft reply:</div>
        <div class="draft">{escaped_draft}</div>
        """

    card_html = f"""
    <div class="triage-card {urgency_class}">
        <div class="card-header">
            <span class="sender">{email_data['from_name']}</span>
            <span class="time">{time_str}</span>
        </div>
        <div class="subject">Subject: {email_data['subject']}</div>
        <div class="want"><strong>What they want:</strong> {what_they_want}</div>
        {deadline_html}
        {draft_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Action buttons inline
    btn_cols = st.columns([1, 1, 4])
    with btn_cols[0]:
        if show_draft and draft:
            if st.button("Copy draft", key=f"copy_{msg_id}"):
                safe = draft.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
                components.html(
                    f"""<script>
                    navigator.clipboard.writeText(`{safe}`);
                    </script>""",
                    height=0,
                )
                st.toast("Draft copied!")
    with btn_cols[1]:
        st.link_button("Open in Gmail", gmail_url)


# ── Run Pipeline ────────────────────────────────────────────────────────
if submitted:
    status = st.status("Starting inbox triage...", expanded=True)
    progress_bar = st.progress(0)

    def progress_callback(stage: str, current: int, total: int) -> None:
        """Update the Streamlit status and progress bar."""
        if stage == "auth":
            status.update(label="Authenticating with Gmail...")
        elif stage == "fetch":
            if total > 0:
                status.update(label=f"Fetched {total} emails")
            else:
                status.update(label="Fetching emails...")
        elif stage == "filter":
            status.update(label=f"Filtered: {current} kept out of {total}")
        elif stage == "summarize":
            if total > 0:
                progress_bar.progress(current / total)
                status.update(label=f"Triaging {current} of {total}...")
        elif stage == "done":
            progress_bar.progress(1.0)
            status.update(label="Done!", state="complete")

    try:
        result = run_email_summary(
            window="24h",
            start=None,
            end=None,
            use_cache=use_cache,
            show_omitted=show_omitted,
            progress_callback=progress_callback,
        )

        ts = result["triage_stats"]
        needs_reply = ts["reply_high"] + ts["reply_medlow"]

        # ── Quick stats ─────────────────────────────────────
        st.markdown(
            f"📥 **Inbox triage — last 24 hours** &nbsp; | &nbsp; "
            f"{len(result['kept'])} from people &bull; "
            f"{needs_reply} need a reply &bull; "
            f"{ts['fyi']} FYI &bull; "
            f"{len(result['omitted'])} omitted"
        )

        # ── Metrics Row ─────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total fetched", result["total_fetched"])
        m2.metric("Need reply", needs_reply)
        m3.metric("FYI", ts["fyi"])
        m4.metric("Cached hits", result["stats"]["cached"])

        groups = result["groups"]

        # ── High urgency section ────────────────────────────
        if groups["high"]:
            st.markdown("### 🔴 Needs reply — high urgency")
            for e in groups["high"]:
                _render_card(e, "urgency-high", show_draft=True)

        # ── Medium/low urgency section ──────────────────────
        if groups["medlow"]:
            st.markdown("### 🟡 Needs reply — medium / low urgency")
            for e in groups["medlow"]:
                urgency = e.get("triage", {}).get("urgency", "low")
                _render_card(e, f"urgency-{urgency}", show_draft=True)

        # ── FYI section ─────────────────────────────────────
        if groups["fyi"]:
            st.markdown("### ⚪ FYI only")
            for e in groups["fyi"]:
                _render_card(e, "urgency-fyi", show_draft=False)

        # ── Omitted Senders ─────────────────────────────────
        if result["omitted"]:
            with st.expander(f"Omitted senders ({len(result['omitted'])})", expanded=False):
                st.markdown(result["omitted_markdown"])

        # ── Download / Copy ─────────────────────────────────
        st.markdown("---")
        btn1, btn2 = st.columns(2)
        with btn1:
            st.download_button(
                "Download as Markdown",
                data=result["markdown"],
                file_name=f"inbox_triage_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with btn2:
            if st.button("Copy to clipboard", use_container_width=True, key="copy_all"):
                safe_md = result["markdown"].replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
                components.html(
                    f"""<script>
                    navigator.clipboard.writeText(`{safe_md}`);
                    </script>""",
                    height=0,
                )
                st.toast("Copied to clipboard!")

    except FileNotFoundError as e:
        st.error(
            "**Gmail credentials not found.** Place `credentials.json` in the email_summarizer directory.\n\n"
            f"See the README for setup instructions.\n\n`{e}`"
        )
    except EnvironmentError as e:
        st.error(f"**Missing API key.** {e}")
    except Exception as e:
        logger.exception("Email triage failed")
        st.error(f"**Error:** {e}")
