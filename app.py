"""
VEDA Technology - Task 29
Build a PDF Report Generator
Uses only Python standard library + Pandas + ReportLab.
Run: python app.py
Then open: http://127.0.0.1:8000
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from io import BytesIO
from datetime import datetime
import html
import json
import mimetypes
import os
import re
import uuid
from email.parser import BytesParser
from email.policy import default

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "sample_data.csv"
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)
HOST, PORT = "127.0.0.1", 8000

ACCENT = colors.HexColor("#6D43C5")
ORANGE = colors.HexColor("#FF6B1A")
INK = colors.HexColor("#17213A")
MUTED = colors.HexColor("#667085")
LIGHT = colors.HexColor("#F4F1FB")

def load_data():
    df = pd.read_csv(DATA_FILE)
    required = {"date","region","product","customer","quantity","unit_price","revenue"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    return df

def metrics(df):
    total = float(df["revenue"].sum())
    qty = int(df["quantity"].sum())
    avg = total / len(df) if len(df) else 0
    top = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    top_product = top.index[0] if len(top) else "—"
    region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    top_region = region.index[0] if len(region) else "—"
    return {
        "records": len(df), "revenue": total, "quantity": qty,
        "avg": avg, "top_product": top_product, "top_region": top_region
    }

def money(x):
    return f"₹{x:,.0f}"

def make_pdf(df, title="Business Performance Report"):
    m = metrics(df)
    filename = REPORT_DIR / f"VEDA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        str(filename), pagesize=A4,
        rightMargin=14*mm, leftMargin=14*mm,
        topMargin=14*mm, bottomMargin=14*mm
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleX", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=22, leading=26, textColor=INK, alignment=TA_LEFT, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="SubX", parent=styles["Normal"], fontSize=9.5,
        textColor=MUTED, spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name="SectionX", parent=styles["Heading2"], fontSize=12,
        textColor=ACCENT, spaceBefore=8, spaceAfter=7
    ))
    story = []
    story.append(Paragraph("VEDA TECHNOLOGY", styles["SubX"]))
    story.append(Paragraph(html.escape(title), styles["TitleX"]))
    story.append(Paragraph(
        f"Generated automatically • {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        styles["SubX"]
    ))

    summary = [
        ["REPORT SNAPSHOT", "", "", ""],
        ["Records", str(m["records"]), "Total Revenue", money(m["revenue"])],
        ["Units Sold", f'{m["quantity"]:,}', "Average Record", money(m["avg"])],
        ["Top Product", m["top_product"], "Top Region", m["top_region"]],
    ]
    t = Table(summary, colWidths=[35*mm, 50*mm, 35*mm, 55*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),INK), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("SPAN",(0,0),(-1,0)), ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9), ("LEADING",(0,0),(-1,-1),12),
        ("BACKGROUND",(0,1),(-1,-1),LIGHT), ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#D8D2E7")),
        ("TEXTCOLOR",(0,1),(0,-1),MUTED), ("TEXTCOLOR",(2,1),(2,-1),MUTED),
        ("FONTNAME",(1,1),(1,-1),"Helvetica-Bold"),
        ("FONTNAME",(3,1),(3,-1),"Helvetica-Bold"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("TOPPADDING",(0,0),(-1,-1),7),
        ("BOTTOMPADDING",(0,0),(-1,-1),7),
    ]))
    story += [t, Spacer(1, 10)]
    story.append(Paragraph("Revenue by Region", styles["SectionX"]))
    reg = df.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    reg_rows = [["Region", "Revenue", "Share"]]
    for _, r in reg.iterrows():
        share = (r["revenue"]/m["revenue"]*100) if m["revenue"] else 0
        reg_rows.append([str(r["region"]), money(r["revenue"]), f"{share:.1f}%"])
    rt = Table(reg_rows, colWidths=[55*mm, 60*mm, 60*mm], repeatRows=1)
    rt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),ACCENT), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,-1),9),
        ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#D8D2E7")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),
        ("ALIGN",(1,1),(-1,-1),"RIGHT"), ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
    ]))
    story += [rt, Spacer(1, 10)]
    story.append(Paragraph("Detailed Sales Records", styles["SectionX"]))
    detail = df.copy()
    detail["revenue"] = detail["revenue"].map(money)
    detail["unit_price"] = detail["unit_price"].map(money)
    rows = [["Date","Region","Product","Qty","Unit Price","Revenue"]]
    for _, r in detail.head(25).iterrows():
        rows.append([
            str(r["date"]), str(r["region"]), str(r["product"]),
            f'{int(r["quantity"]):,}', str(r["unit_price"]), str(r["revenue"])
        ])
    dt = Table(rows, colWidths=[25*mm, 23*mm, 45*mm, 15*mm, 31*mm, 42*mm], repeatRows=1)
    dt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),ORANGE), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,-1),7.5),
        ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#D8D2E7")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, LIGHT]),
        ("ALIGN",(3,1),(-1,-1),"RIGHT"), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    story.append(dt)
    story += [Spacer(1, 12), Paragraph(
        "Generated with Python + Pandas + ReportLab. Missing/invalid numeric values are safely converted to zero before report generation.",
        styles["SubX"]
    )]
    doc.build(story)
    return filename

def page():
    df = load_data()
    m = metrics(df)
    recent = df.tail(8).iloc[::-1]
    rows = "".join(
        f"<tr><td>{html.escape(str(r['date']))}</td><td>{html.escape(str(r['region']))}</td>"
        f"<td>{html.escape(str(r['product']))}</td><td>{int(r['quantity'])}</td>"
        f"<td>{money(r['revenue'])}</td></tr>" for _, r in recent.iterrows()
    )
    top_regions = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    bars = ""
    maxv = top_regions.max() if len(top_regions) else 1
    for region, value in top_regions.items():
        pct = (value/maxv*100) if maxv else 0
        bars += f'<div class="bar-row"><span>{html.escape(str(region))}</span><div class="bar"><i style="width:{pct:.1f}%"></i></div><b>{money(value)}</b></div>'
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>VEDA | PDF Report Generator</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#f6f7fb;color:#17213a}}
header{{height:72px;background:#fff;border-bottom:1px solid #e8eaf0;display:flex;align-items:center;justify-content:space-between;padding:0 7vw;position:sticky;top:0;z-index:5}}
.logo{{font-weight:800;font-size:20px;letter-spacing:.3px}} .logo span{{color:#ff6b1a}} .logo em{{font-style:normal;color:#6d43c5}}
.wrap{{max-width:1180px;margin:34px auto;padding:0 22px}} .hero{{display:flex;justify-content:space-between;gap:25px;align-items:flex-end;margin-bottom:24px}}
.kicker{{color:#ff6b1a;font-size:12px;font-weight:800;letter-spacing:2px}} h1{{font-size:34px;margin:7px 0 8px}} .sub{{color:#667085;max-width:650px}}
.pill{{background:#eee9fb;color:#5a35a8;padding:9px 13px;border-radius:99px;font-size:12px;font-weight:700}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}} .card{{background:#fff;border:1px solid #e7e9f0;border-radius:18px;padding:20px;box-shadow:0 8px 25px #17213a0b}}
.card small{{color:#667085}} .value{{font-size:24px;font-weight:800;margin-top:8px}} .accent{{color:#6d43c5}}
.grid{{display:grid;grid-template-columns:1.25fr .75fr;gap:18px;margin-top:18px}} .panel{{background:#fff;border:1px solid #e7e9f0;border-radius:18px;padding:22px;box-shadow:0 8px 25px #17213a08}}
.panel h2{{font-size:17px;margin:0 0 16px}} table{{width:100%;border-collapse:collapse;font-size:13px}} th,td{{padding:11px 8px;border-bottom:1px solid #edf0f5;text-align:left}} th{{color:#667085;font-size:11px;text-transform:uppercase;letter-spacing:.7px}} td:last-child,th:last-child{{text-align:right}}
.bar-row{{display:grid;grid-template-columns:55px 1fr 75px;gap:10px;align-items:center;margin:15px 0;font-size:12px}} .bar{{height:9px;background:#eee9fb;border-radius:99px;overflow:hidden}} .bar i{{display:block;height:100%;background:linear-gradient(90deg,#6d43c5,#ff6b1a);border-radius:99px}}
.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}} button,.btn{{border:0;border-radius:11px;padding:12px 16px;font-weight:750;cursor:pointer;text-decoration:none;display:inline-block}}
.primary{{background:#17213a;color:white}} .orange{{background:#ff6b1a;color:white}} .soft{{background:#eee9fb;color:#55329d}}
.upload{{margin-top:18px;border:1px dashed #bdb3d7;border-radius:14px;padding:16px;background:#fbfaff}} input[type=file]{{max-width:100%}}
.note{{font-size:12px;color:#667085;margin-top:10px}} footer{{text-align:center;color:#98a2b3;padding:35px 0;font-size:12px}}
@media(max-width:850px){{.cards{{grid-template-columns:1fr 1fr}}.grid{{grid-template-columns:1fr}}.hero{{display:block}}}}
@media(max-width:520px){{.cards{{grid-template-columns:1fr}}}}
</style></head>
<body>
<header><div class="logo"><em>VEDA</em> <span>TECHNOLOGY</span></div><div class="pill">TASK 29 · REPORT LAB</div></header>
<main class="wrap">
<section class="hero"><div><div class="kicker">AUTOMATED DOCUMENT STUDIO</div><h1>PDF Report Generator</h1><div class="sub">Turn structured business data into a clean, professional PDF report with summary metrics, regional analysis and detailed records.</div></div>
<div class="pill">{m['records']} records loaded</div></section>
<section class="cards">
<div class="card"><small>Total Revenue</small><div class="value accent">{money(m['revenue'])}</div></div>
<div class="card"><small>Units Sold</small><div class="value">{m['quantity']:,}</div></div>
<div class="card"><small>Top Product</small><div class="value" style="font-size:19px">{html.escape(m['top_product'])}</div></div>
<div class="card"><small>Top Region</small><div class="value" style="font-size:19px">{html.escape(m['top_region'])}</div></div>
</section>
<section class="grid">
<div class="panel"><h2>Latest records</h2><table><thead><tr><th>Date</th><th>Region</th><th>Product</th><th>Qty</th><th>Revenue</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="panel"><h2>Regional revenue</h2>{bars}</div>
</section>
<section class="panel" style="margin-top:18px"><h2>Create your report</h2>
<div class="actions"><a class="btn orange" href="/generate">Generate PDF Report</a><a class="btn soft" href="/download">Open Latest PDF</a></div>
<form class="upload" method="post" action="/upload" enctype="multipart/form-data">
<b>Optional: use your own CSV</b><br><input name="file" type="file" accept=".csv" required>
<button class="primary" type="submit">Load CSV</button>
<div class="note">Required columns: date, region, product, customer, quantity, unit_price, revenue. A sample dataset is already included.</div>
</form></section>
</main><footer>Task 29 • Python + Pandas + ReportLab • Built as a reusable local reporting tool</footer>
</body></html>"""

def latest_report():
    files = sorted(REPORT_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, data, ctype, status=200, filename=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/":
                data = page().encode("utf-8")
                self.send_bytes(data, "text/html; charset=utf-8")
            elif path == "/generate":
                pdf = make_pdf(load_data())
                data = pdf.read_bytes()
                self.send_bytes(data, "application/pdf", filename=pdf.name)
            elif path == "/download":
                pdf = latest_report()
                if not pdf:
                    pdf = make_pdf(load_data())
                self.send_bytes(pdf.read_bytes(), "application/pdf", filename=pdf.name)
            elif path == "/health":
                self.send_bytes(b'{"status":"ok","task":29}', "application/json")
            else:
                self.send_bytes(b"Not found", "text/plain", 404)
        except Exception as e:
            self.send_bytes(f"Application error: {e}".encode(), "text/plain", 500)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/upload":
            self.send_bytes(b"Not found", "text/plain", 404); return
        try:
            content_type = self.headers.get("Content-Type", "")
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            if "multipart/form-data" not in content_type:
                raise ValueError("Please upload a CSV file.")
            # Parse multipart using the stdlib email parser; works on modern Python versions.
            msg = BytesParser(policy=default).parsebytes(
                b"Content-Type: " + content_type.encode() + b"\r\nMIME-Version: 1.0\r\n\r\n" + body
            )
            part = next((p for p in msg.iter_attachments() if p.get_filename()), None)
            if part is None:
                raise ValueError("No file was uploaded.")
            filename = part.get_filename()
            if not filename.lower().endswith(".csv"):
                raise ValueError("Only .csv files are supported.")
            payload = part.get_payload(decode=True)
            temp = pd.read_csv(BytesIO(payload))
            required = {"date","region","product","customer","quantity","unit_price","revenue"}
            missing = required - set(temp.columns)
            if missing:
                raise ValueError("CSV is missing: " + ", ".join(sorted(missing)))
            temp["revenue"] = pd.to_numeric(temp["revenue"], errors="coerce").fillna(0)
            temp["quantity"] = pd.to_numeric(temp["quantity"], errors="coerce").fillna(0)
            temp.to_csv(DATA_FILE, index=False)
            self.send_response(303); self.send_header("Location","/"); self.end_headers()
        except Exception as e:
            self.send_bytes(f"Upload failed: {e}".encode(), "text/plain", 400)

if __name__ == "__main__":
    print(f"VEDA Task 29 running at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
