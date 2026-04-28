"""Landing page for Rishil's Tools dashboard."""
from __future__ import annotations

import platform

import streamlit as st

from shared.styling import apply_theme

apply_theme()

st.markdown("# 🛠️ Rishil's Tools")
st.markdown("*Personal ops dashboard*")
st.markdown("---")

# Tool definitions
TOOLS = [
    {
        "icon": "📧",
        "name": "Email Summarizer",
        "desc": "Pulls Gmail, filters automation, gives you a chronological digest.",
        "page": "pages/1_📧_Email_Summarizer.py",
        "enabled": True,
    },
    {
        "icon": "💬",
        "name": "WhatsApp → DomPortal",
        "desc": "Forward WhatsApp messages into the DomPortal system.",
        "page": None,
        "enabled": False,
    },
    {
        "icon": "💰",
        "name": "Payroll",
        "desc": "Generate and review monthly payroll runs.",
        "page": None,
        "enabled": False,
    },
]

# Render tool cards in a 3-column grid
cols = st.columns(3)

for i, tool in enumerate(TOOLS):
    with cols[i % 3]:
        if tool["enabled"]:
            disabled_class = ""
            badge = ""
        else:
            disabled_class = " disabled"
            badge = '<span style="font-size:0.7rem;color:rgba(232,232,234,0.5);">Coming soon</span>'

        card_html = f"""
        <div class="tool-card{disabled_class}">
            <div>
                <div class="icon">{tool["icon"]}</div>
                <div class="name">{tool["name"]}</div>
                <div class="desc">{tool["desc"]}</div>
            </div>
            <div class="last-run">{badge}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        if tool["enabled"]:
            st.page_link(tool["page"], label=f"Open {tool['name']} →")

# Footer
hostname = platform.node() or "localhost"
st.markdown(
    f'<div class="dashboard-footer">Running locally • {hostname}</div>',
    unsafe_allow_html=True,
)
