"""Shared CSS theme and page configuration for the dashboard."""
from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Apply shared page config and CSS styling.

    Call this at the top of every page before any other st.* calls.
    """
    st.set_page_config(
        page_title="Rishil's Tools",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="auto",
    )
    _inject_css()


def _inject_css() -> None:
    """Inject custom CSS to tighten layout and style tool cards."""
    st.markdown(
        """
        <style>
        /* Tighten default Streamlit padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 1rem;
        }

        /* Tool card styling */
        .tool-card {
            background: var(--secondary-background-color, #1a1a20);
            border: 1px solid rgba(124, 58, 237, 0.25);
            border-radius: 12px;
            padding: 1.5rem;
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            cursor: pointer;
        }
        .tool-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.2);
        }
        .tool-card .icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .tool-card .name {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-color, #e8e8ea);
            margin-bottom: 0.3rem;
        }
        .tool-card .desc {
            font-size: 0.85rem;
            color: rgba(232, 232, 234, 0.65);
            line-height: 1.4;
        }
        .tool-card .last-run {
            font-size: 0.75rem;
            color: rgba(232, 232, 234, 0.4);
            margin-top: auto;
        }

        /* Disabled / coming-soon cards */
        .tool-card.disabled {
            opacity: 0.4;
            cursor: not-allowed;
            pointer-events: none;
        }
        .tool-card.disabled:hover {
            transform: none;
            box-shadow: none;
        }

        /* Footer styling */
        .dashboard-footer {
            text-align: center;
            color: rgba(232, 232, 234, 0.35);
            font-size: 0.8rem;
            padding-top: 3rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
