# Payroll Tools

A small website that runs on your own computer. Open it in Chrome and it gives you
three buttons — upload a file, get your file back:

1. **Paystub → Time Cards** — upload a W2 paystubs **PDF**, get an Excel workbook
   with one formatted time card per employee (hours total to each paystub).
2. **Time Card → PDF** — upload a timecard **.xlsx**, get a PDF with one employee
   per page (the "Staff Schedule" summary sheet is dropped automatically).
3. **Combine Paystubs + Time Cards** — upload a paystubs **PDF** and a time cards
   **PDF**, get one PDF with each employee's paystub on top and their matching
   time card below. Employees are matched automatically by name and hours.

Everything runs locally on the computer. Nothing is uploaded to the internet.

---

## One-time setup (do this once)

1. **Install Python** — go to https://www.python.org/downloads/ , download the
   latest Windows installer, run it, and on the first screen **check the box that
   says "Add Python to PATH"**, then click Install.
2. **Install LibreOffice** (needed only for the "Time Card → PDF" tool) — go to
   https://www.libreoffice.org/download/ and install it with the defaults.

That's it. You don't need to touch the code.

## Every day: starting the website

Double-click **`START-Windows.bat`**.

- The first time, it spends a minute installing a few components — that's normal.
- A black window opens and stays open (that's the engine — leave it open).
- Chrome opens automatically at **http://127.0.0.1:5000**.
- To stop it, just close the black window.

On a Mac, double-click **`start-mac.command`** instead.

## Keep it running all the time (optional)

To have the website start by itself whenever the laptop turns on:

1. Press **Windows key + R**, type `shell:startup`, press Enter. A folder opens.
2. **Right-click `START-Windows.bat` → Show more options → Send to → Desktop
   (create shortcut)**, then drag that shortcut into the Startup folder.

Now it launches on every login. Bookmark **http://127.0.0.1:5000** in Chrome for
one-click access.

---

## Notes

- The generated time cards are a **model** — the daily hours are made up to add up
  to each paystub's total. They are not a real attendance record.
- "Days off per employee" on tool 1 is optional. Paste JSON like
  `{"Mariya": ["Mon"], "Qadir": ["Tue","Fri"]}` to force specific days off.
- Files never leave the computer; each job is processed in a temporary folder.

## What's inside

- `app.py` — the local web server.
- `templates/index.html` — the page you see in the browser.
- `skills/generate_timecards.py` — paystub → time cards (unchanged skill script).
- `skills/timecard_to_pdf.py` — time card → PDF (unchanged skill script).
- `skills/combine.py` — combine paystubs + time cards (name matching, cropping,
  footer removal).
