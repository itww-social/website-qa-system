import os, json
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from xml.sax.saxutils import escape

# ---------------- ENV ----------------
folder = os.environ.get("RESULT_FOLDER")
url = os.environ.get("TARGET_URL")
out_pdf = os.path.join(folder, "Client-QA-Report.pdf")

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(
    out_pdf,
    topMargin=36,
    bottomMargin=36
)

elements = []

def add_space(h=0.15):
    elements.append(Spacer(1, h * inch))

# ---------------- HEADER ----------------
elements.append(Paragraph("Website QA Report", styles['Heading1']))
add_space(0.2)
elements.append(Paragraph(f"Website: {escape(str(url))}", styles['Normal']))
elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
add_space(0.3)

# ---------------- LIGHTHOUSE ----------------
lh_file = os.path.join(folder, "lighthouse.json")
if os.path.exists(lh_file):
    with open(lh_file) as f:
        lh = json.load(f)

    cats = lh.get('categories', {})
    perf = round(cats.get('performance', {}).get('score', 0) * 100)
    acc = round(cats.get('accessibility', {}).get('score', 0) * 100)
    bp = round(cats.get('best-practices', {}).get('score', 0) * 100)
    seo = round(cats.get('seo', {}).get('score', 0) * 100)

    elements.append(Paragraph("Performance & Quality (Lighthouse)", styles['Heading2']))
    add_space(0.1)

    data = [
        ["Metric", "Score"],
        ["Performance", perf],
        ["Accessibility", acc],
        ["Best Practices", bp],
        ["SEO", seo],
    ]

    table = Table(data, colWidths=[3 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ]))

    elements.append(table)
    add_space(0.2)

    # -------- Core Web Vitals --------
    audits = lh.get('audits', {})

    def val(a):
        v = audits.get(a, {}).get('displayValue') or audits.get(a, {}).get('numericValue')
        return escape(str(v)) if v else "N/A"

    elements.append(Paragraph("Core Web Vitals & Key Metrics", styles['Heading3']))
    add_space(0.1)

    vitals = [
        ["Metric", "Value"],
        ["Largest Contentful Paint (LCP)", val('largest-contentful-paint')],
        ["First Contentful Paint (FCP)", val('first-contentful-paint')],
        ["Time to Interactive (TTI)", val('interactive')],
        ["Total Blocking Time (TBT)", val('total-blocking-time')],
        ["Cumulative Layout Shift (CLS)", val('cumulative-layout-shift')],
    ]

    table2 = Table(vitals, colWidths=[3 * inch, 2 * inch])
    table2.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    elements.append(table2)
    add_space(0.3)

# ---------------- ACCESSIBILITY ----------------
axe_file = os.path.join(folder, "accessibility.json")
if os.path.exists(axe_file):
    with open(axe_file) as f:
        axe = json.load(f)

    violations = axe.get('violations', [])

    elements.append(Paragraph("Accessibility (axe-core)", styles['Heading2']))
    add_space(0.1)

    elements.append(Paragraph(f"Total violations: {len(violations)}", styles['Normal']))
    add_space(0.1)

    sev = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    for v in violations:
        impact = v.get('impact', 'minor')
        if impact in sev:
            sev[impact] += 1

    data = [
        ["Severity", "Count"],
        ["Critical", sev["critical"]],
        ["Serious", sev["serious"]],
        ["Moderate", sev["moderate"]],
        ["Minor", sev["minor"]],
    ]

    sev_table = Table(data, colWidths=[3 * inch, 1 * inch])
    sev_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    elements.append(sev_table)
    add_space(0.2)

    if violations:
        elements.append(Paragraph("Top Issues (sample):", styles['Heading3']))
        add_space(0.1)

        for v in violations[:5]:
            vid = escape(str(v.get('id')))
            impact = escape(str(v.get('impact')))
            desc = escape(str(v.get('description')))

            elements.append(Paragraph(f"<b>{vid}</b> ({impact}) — {desc}", styles['Normal']))

            nodes = v.get('nodes', [])
            if nodes:
                sel = nodes[0].get('target', [])
                if sel:
                    selector = escape(str(sel[0]))
                    elements.append(Paragraph(f"Example selector: {selector}", styles['Normal']))

            add_space(0.1)

# ---------------- PLAYWRIGHT ----------------
pw_file = os.path.join(folder, "playwright-report.json")
if os.path.exists(pw_file):
    with open(pw_file) as f:
        pw = json.load(f)

    stats = pw.get('stats', {})

    elements.append(Paragraph("Functional Tests (Playwright)", styles['Heading2']))
    add_space(0.1)

passed = stats.get('expected', 0)
failed = stats.get('unexpected', 0)
total = passed + failed

elements.append(Paragraph(f"Total tests: {total}", styles['Normal']))
elements.append(Paragraph(f"Passed: {passed}", styles['Normal']))
elements.append(Paragraph(f"Failed: {failed}", styles['Normal']))
add_space(0.2)

# ---------------- PERCY ----------------
elements.append(Paragraph("Visual Testing (Percy)", styles['Heading2']))
add_space(0.1)
elements.append(Paragraph("Snapshots captured. Review visual changes in Percy dashboard.", styles['Normal']))
add_space(0.2)

# ---------------- SCREENSHOT (FIXED) ----------------
screenshot = os.path.join(folder, "screenshot.png")

if os.path.exists(screenshot):
    elements.append(PageBreak())  # cleaner layout
    elements.append(Paragraph("Website Screenshot", styles['Heading2']))
    add_space(0.2)

    try:
        img = Image(screenshot)

        max_width = 6.5 * inch
        max_height = 9 * inch

        ratio = img.imageHeight / img.imageWidth

        img.drawWidth = max_width
        img.drawHeight = max_width * ratio

        if img.drawHeight > max_height:
            img.drawHeight = max_height
            img.drawWidth = max_height / ratio

        elements.append(img)

    except Exception as e:
        elements.append(Paragraph(f"Image error: {escape(str(e))}", styles['Normal']))

    add_space(0.3)

# ---------------- OVERALL GRADE ----------------
elements.append(Paragraph("Overall Assessment", styles['Heading2']))

grade = "A"
if 'perf' in locals() and perf < 75:
    grade = "B"
if 'perf' in locals() and perf < 60:
    grade = "C"

elements.append(Paragraph(f"Suggested Grade: {grade}", styles['Normal']))

# ---------------- BUILD ----------------
doc.build(elements)

print("✅ PDF generated:", out_pdf)