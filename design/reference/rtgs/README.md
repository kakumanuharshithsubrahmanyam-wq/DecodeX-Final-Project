# RTGS - Real Time Governance Society (Frontend Demo)

Frontend-only prototype. No backend, no build step, no dependencies.

## Run
Open `index.html` in a browser, or serve the folder:
    python3 -m http.server 8000   # then visit http://localhost:8000

## Files
- `index.html` - page shell
- `styles.css` - theme (CSS variables, dark mode via `data-theme`)
- `app.js` - state (LocalStorage key `rtgs1`), mock data, simulated AI rules, views, translation table (`TR`), login

## Working vs simulated
Working: login role picker, complaint filing flow, tracking, officer and admin dashboards, SLA/urgency rule editing, notifications, feedback, English/Telugu UI, LocalStorage persistence, reset.
Simulated: all "AI" (keyword rules), image analysis (manual category confirmation), chatbot (scripted), authentication (none), notifications (in-app only).

## Not built
Community forum, WhatsApp preview, before/after image slider, notification preferences, Telugu for user-entered text.
