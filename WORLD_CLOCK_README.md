# World Clock

A minimal world clock showing live times for New York, London, and Dubai. Single self-contained HTML file — no dependencies, no build step.

## How it works

- Uses `Intl.DateTimeFormat` with the `timeZone` option, so daylight saving transitions are handled automatically by the browser.
- Updates every second via `setInterval`.
- Dark theme, monospace digits, responsive (stacks vertically on mobile).

## Deploy to GitHub Pages

1. Push this repo (or just the `index.html` file) to a GitHub repository.
2. Go to **Settings → Pages**.
3. Under **Source**, select the branch containing `index.html` (e.g. `main`) and the folder (e.g. `/` or `/tools/dashboard`).
4. Click **Save**. The page will be live at `https://<username>.github.io/<repo>/`.

Or to test locally, just open `index.html` in a browser — no server needed.

## Customisation

To add or change cities, edit the `clocks` array in the `<script>` block and add a matching `<div class="clock">` in the HTML. Use any [IANA timezone name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) (e.g. `Asia/Tokyo`, `Australia/Sydney`).
