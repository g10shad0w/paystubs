#!/usr/bin/env python3
"""Local web app exposing three payroll tools, each as a one-button upload:

  1. Paystub -> Time Cards   (paystub PDF  -> multi-sheet .xlsx)
  2. Time Card -> PDF        (timecard .xlsx -> per-employee PDF)
  3. Combine Paystubs + Time Cards (two PDFs -> merged PDF, one employee/page)

Everything runs locally. Uploads and outputs live in per-run temp folders that
are cleaned up automatically.
"""
import json
import os
import subprocess
import sys
import tempfile
import uuid
import webbrowser
from threading import Timer

from flask import Flask, request, send_file, jsonify, render_template

BASE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.join(BASE, "skills")
WORK = os.path.join(tempfile.gettempdir(), "paystub_tools_work")
os.makedirs(WORK, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64 MB


def run_dir():
    d = os.path.join(WORK, uuid.uuid4().hex)
    os.makedirs(d, exist_ok=True)
    return d


def save_upload(file_storage, dest_dir):
    name = os.path.basename(file_storage.filename or "upload")
    path = os.path.join(dest_dir, name)
    file_storage.save(path)
    return path


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/paystub-to-timecards", methods=["POST"])
def paystub_to_timecards():
    if "pdf" not in request.files:
        return jsonify(error="Please choose a paystubs PDF."), 400
    d = run_dir()
    pdf = save_upload(request.files["pdf"], d)
    out = os.path.join(d, os.path.splitext(os.path.basename(pdf))[0] + "-timecards.xlsx")
    cmd = [sys.executable, os.path.join(SKILLS, "generate_timecards.py"),
           "--pdf", pdf, "--out", out]

    # optional days-off: JSON file upload OR pasted JSON text
    daysoff_path = None
    if request.files.get("daysoff") and request.files["daysoff"].filename:
        daysoff_path = save_upload(request.files["daysoff"], d)
    elif (request.form.get("daysoff_text") or "").strip():
        try:
            parsed = json.loads(request.form["daysoff_text"])
            daysoff_path = os.path.join(d, "daysoff.json")
            with open(daysoff_path, "w") as fh:
                json.dump(parsed, fh)
        except Exception as e:
            return jsonify(error=f"Days-off JSON is invalid: {e}"), 400
    if daysoff_path:
        cmd += ["--daysoff", daysoff_path]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.isfile(out):
        return jsonify(error=(proc.stderr or proc.stdout or "Generation failed").strip()), 500
    return send_file(out, as_attachment=True,
                     download_name=os.path.basename(out),
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route("/api/timecard-to-pdf", methods=["POST"])
def timecard_to_pdf():
    if "xlsx" not in request.files:
        return jsonify(error="Please choose a timecard .xlsx file."), 400
    d = run_dir()
    xlsx = save_upload(request.files["xlsx"], d)
    out = os.path.join(d, os.path.splitext(os.path.basename(xlsx))[0] + "-timecards.pdf")
    skip = request.form.get("skip_sheet", "Staff Schedule")
    cmd = [sys.executable, os.path.join(SKILLS, "timecard_to_pdf.py"),
           xlsx, out, "--skip-sheet", skip]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.isfile(out):
        return jsonify(error=(proc.stderr or proc.stdout or "Conversion failed").strip()), 500
    return send_file(out, as_attachment=True,
                     download_name=os.path.basename(out),
                     mimetype="application/pdf")


@app.route("/api/combine", methods=["POST"])
def combine():
    if "paystubs" not in request.files or "timecards" not in request.files:
        return jsonify(error="Please choose both a paystubs PDF and a time cards PDF."), 400
    d = run_dir()
    ps = save_upload(request.files["paystubs"], d)
    tc = save_upload(request.files["timecards"], d)
    out = os.path.join(d, "W2 Paystubs with Time Cards.pdf")
    cmd = [sys.executable, os.path.join(SKILLS, "combine.py"),
           "--paystubs", ps, "--timecards", tc, "--out", out]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.isfile(out):
        return jsonify(error=(proc.stderr or proc.stdout or "Combine failed").strip()), 500
    return send_file(out, as_attachment=True,
                     download_name=os.path.basename(out),
                     mimetype="application/pdf")


@app.route("/api/chain", methods=["POST"])
def chain():
    """One-step chain: paystubs PDF -> time cards (.xlsx) -> time cards PDF ->
    combined PDF (paystub on top, matching time card below, one per page).

    Only a paystubs PDF is required; days-off is optional (same as tool 1)."""
    if "pdf" not in request.files or not request.files["pdf"].filename:
        return jsonify(error="Please choose a paystubs PDF."), 400
    d = run_dir()
    pdf = save_upload(request.files["pdf"], d)
    stem = os.path.splitext(os.path.basename(pdf))[0]
    xlsx = os.path.join(d, stem + "-timecards.xlsx")
    tc_pdf = os.path.join(d, stem + "-timecards.pdf")
    out = os.path.join(d, "W2 Paystubs with Time Cards.pdf")

    # Step 1: paystubs PDF -> time cards .xlsx (with optional days-off)
    gen_cmd = [sys.executable, os.path.join(SKILLS, "generate_timecards.py"),
               "--pdf", pdf, "--out", xlsx]
    daysoff_path = None
    if request.files.get("daysoff") and request.files["daysoff"].filename:
        daysoff_path = save_upload(request.files["daysoff"], d)
    elif (request.form.get("daysoff_text") or "").strip():
        try:
            parsed = json.loads(request.form["daysoff_text"])
            daysoff_path = os.path.join(d, "daysoff.json")
            with open(daysoff_path, "w") as fh:
                json.dump(parsed, fh)
        except Exception as e:
            return jsonify(error=f"Days-off JSON is invalid: {e}"), 400
    if daysoff_path:
        gen_cmd += ["--daysoff", daysoff_path]
    proc = subprocess.run(gen_cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.isfile(xlsx):
        msg = (proc.stderr or proc.stdout or "Time card generation failed").strip()
        return jsonify(error=f"Step 1 (make time cards): {msg}"), 500

    # Step 2: time cards .xlsx -> time cards PDF
    skip = request.form.get("skip_sheet", "Staff Schedule")
    pdf_cmd = [sys.executable, os.path.join(SKILLS, "timecard_to_pdf.py"),
               xlsx, tc_pdf, "--skip-sheet", skip]
    proc = subprocess.run(pdf_cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.isfile(tc_pdf):
        msg = (proc.stderr or proc.stdout or "Time card PDF conversion failed").strip()
        return jsonify(error=f"Step 2 (time cards to PDF): {msg}"), 500

    # Step 3: combine original paystubs PDF + time cards PDF
    comb_cmd = [sys.executable, os.path.join(SKILLS, "combine.py"),
                "--paystubs", pdf, "--timecards", tc_pdf, "--out", out]
    proc = subprocess.run(comb_cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.isfile(out):
        msg = (proc.stderr or proc.stdout or "Combine failed").strip()
        return jsonify(error=f"Step 3 (combine): {msg}"), 500

    return send_file(out, as_attachment=True,
                     download_name=os.path.basename(out),
                     mimetype="application/pdf")


@app.route("/health")
def health():
    return jsonify(status="ok")


def open_browser(port):
    try:
        webbrowser.open(f"http://127.0.0.1:{port}/")
    except Exception:
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    if os.environ.get("NO_BROWSER") != "1":
        Timer(1.2, open_browser, args=[port]).start()
    print(f"\n  Payroll Tools running at  http://127.0.0.1:{port}/\n  Press Ctrl+C to stop.\n")
    app.run(host="127.0.0.1", port=port, debug=False)
