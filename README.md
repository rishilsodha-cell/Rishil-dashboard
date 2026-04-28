# Rishil's Tools Dashboard

A local Streamlit dashboard that hosts personal operations tools. Currently includes the Email Summarizer, with WhatsApp-to-DomPortal and Payroll tools coming next. The architecture is modular — each tool is a self-contained page that can be added or removed without affecting others.

## One-Time Setup

```bash
cd /Users/rishil/Personal/tools/dashboard
./run.sh
```

This creates a Python virtual environment, installs dependencies, and launches the dashboard at `http://localhost:8501`.

**Prerequisites:**
- Python 3.10+
- Gmail API `credentials.json` in `../email_summarizer/` (see the email_summarizer README for Google Cloud setup)
- `ANTHROPIC_API_KEY` set in your shell environment

## How It Talks to the Email Summarizer

The dashboard imports the email_summarizer package directly as Python modules (no subprocess/CLI calls). The `shared/tool_runner.py` module adds the parent `tools/` directory to `sys.path` and imports from `email_summarizer.*`. This means:

- The email_summarizer's `credentials.json` and `token.json` are used directly
- Config changes made in the dashboard sidebar write to `email_summarizer/config.json`
- The same summary cache at `~/.email_summarizer/cache.json` is shared between CLI and dashboard usage

## How to Add a New Tool

1. **Create a page file** in `pages/` named `N_<emoji>_<Name>.py` (e.g., `2_💬_WhatsApp_DomPortal.py`). The number prefix controls sidebar order.

2. **Start with the shared theme:**
   ```python
   from shared.styling import apply_theme
   apply_theme()
   ```

3. **Build your UI** using Streamlit widgets. Use `shared/tool_runner.py` if you need run history tracking.

4. **Add a card** to `Home.py` in the `TOOLS` list:
   ```python
   {
       "icon": "💬",
       "name": "WhatsApp → DomPortal",
       "desc": "Forward WhatsApp messages into the DomPortal system.",
       "page": "pages/2_💬_WhatsApp_DomPortal.py",
       "enabled": True,
   },
   ```

5. **Delete to remove** — removing a page file from `pages/` cleanly removes that tool. No other files need editing (though you may want to update the Home.py card list).

## Project Structure

```
dashboard/
├── Home.py                              # Landing page with tool card grid
├── pages/
│   └── 1_📧_Email_Summarizer.py         # Email summarizer UI
├── shared/
│   ├── __init__.py
│   ├── styling.py                       # Shared CSS theme
│   └── tool_runner.py                   # Email summarizer wrapper + run history
├── .streamlit/
│   └── config.toml                      # Dark theme + server config
├── requirements.txt
├── run.sh                               # One-command launcher
└── README.md
```

## Troubleshooting

**Port already in use:**
```bash
streamlit run Home.py --server.port 8502
```

**OAuth flow not opening browser:**
Make sure you're running the dashboard locally (not over SSH). The Gmail OAuth flow requires a browser redirect. If running headless, authenticate via the email_summarizer CLI first (`cd ../email_summarizer && python main.py --dry-run --window 1d`) — the token is shared.

**Import errors:**
Ensure you're running from the `dashboard/` directory (or using `./run.sh` which handles this). The email_summarizer package must be at `../email_summarizer/` relative to the dashboard.

**Streamlit not found:**
Run `./run.sh` which installs dependencies automatically, or manually: `pip install -r requirements.txt`.
