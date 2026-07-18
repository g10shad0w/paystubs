#!/usr/bin/env python3
"""Convert a timecard .xlsx into a PDF: one employee sheet per page.

Drops a summary sheet (default "Staff Schedule") and scales each remaining
sheet to fit a single page before converting via LibreOffice headless.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import openpyxl
from openpyxl.worksheet.properties import PageSetupProperties


def main():
    ap = argparse.ArgumentParser(description="Timecard xlsx -> per-employee PDF")
    ap.add_argument("input", help="path to the timecard .xlsx")
    ap.add_argument("output", help="path to write the .pdf")
    ap.add_argument("--skip-sheet", default="Staff Schedule",
                    help='sheet name to exclude (default "Staff Schedule"; '
                         'pass "" to keep all)')
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(f"Input not found: {args.input}")

    wb = openpyxl.load_workbook(args.input)

    if args.skip_sheet and args.skip_sheet in wb.sheetnames:
        wb.remove(wb[args.skip_sheet])

    if not wb.worksheets:
        sys.exit("No sheets left after removing the skip sheet.")

    for ws in wb.worksheets:
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)

    with tempfile.TemporaryDirectory() as tmp:
        staged = os.path.join(tmp, "book.xlsx")
        wb.save(staged)
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf",
             "--outdir", tmp, staged],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        produced = os.path.join(tmp, "book.pdf")
        if not os.path.isfile(produced):
            sys.exit("LibreOffice did not produce a PDF.")
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        shutil.copyfile(produced, args.output)

    try:
        import pypdf
        n = len(pypdf.PdfReader(args.output).pages)
        print(f"Wrote {args.output} ({n} pages, {len(wb.worksheets)} sheets)")
    except Exception:
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
