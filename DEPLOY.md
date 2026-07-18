# Getting an https:// address

You have two ways to reach the site at an `https://` link. Pick one.

---

## Option A — ngrok (fastest, you already have it)

This keeps the app on the laptop but gives it a public `https://` address.
It only works while the laptop is on and both the app and ngrok are running.

1. Start the app as usual: double-click **START-Windows.bat**.
   (It's now running at http://127.0.0.1:5000 — leave that black window open.)
2. Open a **second** window: in the paystub-tools folder, click the address bar,
   type `cmd`, press Enter.
3. Run:

       ngrok http 5000

4. ngrok prints a line like:

       Forwarding   https://abc123.ngrok-free.app -> http://localhost:5000

   That **https://abc123.ngrok-free.app** is your public link — open it in Chrome
   from any device, or share it.

Notes:
- The free ngrok link **changes every time you restart ngrok**. To keep one fixed
  address, in your ngrok dashboard create a free **Static Domain**, then run
  `ngrok http --domain=YOUR-NAME.ngrok-free.app 5000`.
- Free ngrok shows a one-time "You are about to visit..." warning page — click
  **Visit Site**. That's ngrok's, not a problem with your app.
- Anyone with the link can use it (no login), so only share it with people you trust.

---

## Option B — Render (always-on, no laptop needed)

Hosts the site online 24/7 at a real `https://onrender.com` address. Free tier
sleeps after ~15 min idle and takes ~30s to wake on the next visit.

1. Make a free account at https://render.com  (sign in with GitHub is easiest).
2. Put this whole `paystub-tools` folder in a GitHub repository
   (github.com → New repository → upload the files).
3. In Render: **New + → Web Service → Build and deploy from a Git repository →**
   pick your repo.
4. Render detects the **Dockerfile** automatically. Leave everything default,
   choose the **Free** plan, click **Create Web Service**.
5. Wait for the first build (~5 min — it installs LibreOffice). When it says
   **Live**, your address is shown at the top, like
   `https://payroll-tools.onrender.com`.

The `render.yaml` and `Dockerfile` in this folder are already set up for this —
you don't edit anything.

---

## Which should I use?

- Want it working in **2 minutes** and don't mind the laptop staying on → **ngrok**.
- Want it **always available** with nothing running on the laptop → **Render**.
