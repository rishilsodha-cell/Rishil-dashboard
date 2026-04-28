"""Helper module for running tools and managing run history."""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# Add email_summarizer's parent to sys.path so we can import it as a package
_TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from email_summarizer.config import Config, load_config  # noqa: E402
from email_summarizer.filter import filter_emails  # noqa: E402
from email_summarizer.gmail_client import authenticate, fetch_emails  # noqa: E402
from email_summarizer.main import format_output, parse_window, _triage_stats, _group_emails  # noqa: E402
from email_summarizer.summarizer import summarize_emails  # noqa: E402

HISTORY_DIR = Path.home() / ".dashboard"
HISTORY_FILE = HISTORY_DIR / "run_history.json"

EMAIL_SUMMARIZER_CONFIG_PATH = os.path.join(
    _TOOLS_DIR, "email_summarizer", "config.json"
)


def run_email_summary(
    window: str | None = None,
    start: date | None = None,
    end: date | None = None,
    use_cache: bool = True,
    show_omitted: bool = True,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> dict[str, Any]:
    """Run the email triage pipeline and return structured results.

    Args:
        window: Time window string (e.g. '24h', '3d', '1w'). Ignored if start/end set.
        start: Explicit start date. Use with end.
        end: Explicit end date. Use with start.
        use_cache: Whether to use cached Claude triage results.
        show_omitted: Whether to include omitted senders in output.
        progress_callback: Optional callable(stage, current, total) for UI updates.
            stage is one of: 'auth', 'fetch', 'filter', 'summarize', 'done'.

    Returns:
        Dict with keys: kept, omitted, stats, triage_stats, groups, markdown,
        window_desc, total_fetched, config.

    Raises:
        FileNotFoundError: If Gmail credentials.json is missing.
        EnvironmentError: If ANTHROPIC_API_KEY is not set.
        Exception: On Gmail API or other errors.
    """
    config = load_config(EMAIL_SUMMARIZER_CONFIG_PATH)

    def _progress(stage: str, current: int = 0, total: int = 0) -> None:
        if progress_callback:
            progress_callback(stage, current, total)

    # Determine time window
    if start and end:
        start_dt = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
        end_dt = datetime(end.year, end.month, end.day, tzinfo=timezone.utc) + timedelta(days=1)
        window_desc = f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"
    else:
        window_str = window or config.default_window
        delta = parse_window(window_str)
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - delta
        window_desc = f"Last {window_str} ({start_dt.strftime('%d %b')} — {end_dt.strftime('%d %b %Y')})"

    # Authenticate
    _progress("auth")
    service = authenticate()

    # Fetch
    _progress("fetch")
    emails = fetch_emails(service, start_dt, end_dt)
    total_fetched = len(emails)
    _progress("fetch", total_fetched, total_fetched)

    # Filter
    _progress("filter")
    kept, omitted = filter_emails(emails, config)
    _progress("filter", len(kept), total_fetched)

    # Triage
    stats = None
    if kept:
        def _summarize_progress(current: int, total: int) -> None:
            _progress("summarize", current, total)

        kept, stats = summarize_emails(
            kept,
            model=config.model,
            max_emails=config.max_emails_to_summarize,
            use_cache=use_cache,
            progress_callback=_summarize_progress,
        )

    if stats is None:
        stats = {"cached": 0, "newly_summarized": 0, "total_input_tokens": 0, "total_output_tokens": 0}

    # Compute triage stats and groups
    ts = _triage_stats(kept)
    high, medlow, fyi = _group_emails(kept)

    # Format markdown
    markdown = format_output(kept, omitted, window_desc, show_omitted=show_omitted, stats=stats)

    # Build omitted markdown separately for the UI
    omitted_md = ""
    if omitted:
        lines = ["| Sender | Subject | Reason |", "|---|---|---|"]
        for e in omitted:
            sender = e["from_email"]
            subject = e["subject"].replace("|", "\\|")[:80]
            reason = e.get("filter_reason", "unknown")
            lines.append(f"| {sender} | {subject} | {reason} |")
        omitted_md = "\n".join(lines)

    _progress("done")

    result = {
        "kept": kept,
        "omitted": omitted,
        "stats": stats,
        "triage_stats": ts,
        "groups": {"high": high, "medlow": medlow, "fyi": fyi},
        "markdown": markdown,
        "omitted_markdown": omitted_md,
        "window_desc": window_desc,
        "total_fetched": total_fetched,
        "config": config,
    }

    # Save to history
    save_run_to_history({
        "timestamp": datetime.now().isoformat(),
        "window_desc": window_desc,
        "total_fetched": total_fetched,
        "kept": len(kept),
        "omitted": len(omitted),
        "needs_reply": ts["reply_high"] + ts["reply_medlow"],
        "fyi": ts["fyi"],
        "cached": stats["cached"],
        "newly_summarized": stats["newly_summarized"],
    })

    return result


def save_run_to_history(run_metadata: dict) -> None:
    """Append a run record to the history file.

    Args:
        run_metadata: Dict with run details (timestamp, counts, etc.).
    """
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    history = _load_history_file()
    history.append(run_metadata)

    # Keep last 50 runs
    history = history[-50:]

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except IOError as e:
        logger.error("Failed to save run history: %s", e)


def load_recent_runs(n: int = 5) -> list[dict]:
    """Load the most recent N run records.

    Args:
        n: Number of recent runs to return.

    Returns:
        List of run metadata dicts, most recent first.
    """
    history = _load_history_file()
    return list(reversed(history[-n:]))


def _load_history_file() -> list[dict]:
    """Load the full run history from disk.

    Returns:
        List of run metadata dicts.
    """
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def load_email_config() -> dict:
    """Load the raw email_summarizer config.json as a dict.

    Returns:
        Raw config dict.
    """
    try:
        with open(EMAIL_SUMMARIZER_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error("Failed to load email config: %s", e)
        return {
            "allowlist_domains": [],
            "allowlist_addresses": [],
            "blocklist_domains": [],
            "blocklist_addresses": [],
        }


def save_email_config(config_data: dict) -> None:
    """Write updated config back to email_summarizer/config.json.

    Args:
        config_data: Full config dict to write.

    Raises:
        ValueError: If the data is not valid JSON-serializable.
    """
    # Validate it's serializable
    json.dumps(config_data)

    with open(EMAIL_SUMMARIZER_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    logger.info("Email config saved to %s", EMAIL_SUMMARIZER_CONFIG_PATH)
