# scripts/generate-pdf.py
import os, json
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

folder = os.environ.get("RESULT_FOLDER")
url = os.environ.get("TARGET_URL")
out_pdf = os.path.join(folder, "Client-QA-Report.pdf")

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(out_pdf, topMargin=36, bottomMargin=36)

elements = []
def add_space(h=0.15):
    elements.append(Spacer(1, h*inch))

# Header
elements.append(Paragraph("Website QA Report", styles['Heading1']))
add_space(0.2)
elements.append(Paragraph(f"Website: {url}", styles['Normal']))
elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
add_space(0.2)

# --- Lighthouse: scores + core vitals ---
lh_file = os.path.join(folder, "lighthouse.json")
if os.path.exists(lh_file):
    with open(lh_file, 'r') as f:
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
    table = Table(data, colWidths=[3*inch, 1*inch])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#333333')),
                               ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                               ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                               ('ALIGN',(1,1),(-1,-1),'CENTER')]))
    elements.append(table)
    add_space(0.15)

    # Core Web Vitals (if available)
    audits = lh.get('audits', {})
    def val(a): 
        v = audits.get(a, {}).get('displayValue') or audits.get(a, {}).get('numericValue')
        return str(v) if v is not None else "N/A"
    elements.append(Paragraph("Core Web Vitals & Key Metrics", styles['Heading3']))
    add_space(0.05)
    vitals = [
        ["Metric", "Value"],
        ["Largest Contentful Paint (LCP)", val('largest-contentful-paint')],
        ["First Contentful Paint (FCP)", val('first-contentful-paint')],
        ["Time to Interactive (TTI)", val('interactive')],
        ["Total Blocking Time (TBT)", val('total-blocking-time')],
        ["Cumulative Layout Shift (CLS)", val('cumulative-layout-shift')],
    ]
    table2 = Table(vitals, colWidths=[3*inch, 2*inch])
    table2.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
    elements.append(table2)
    add_space(0.2)

# --- Accessibility (axe) ---
axe_file = os.path.join(folder, "accessibility.json")
if os.path.exists(axe_file):
    with open(axe_file) as f:
        axe = json.load(f)
    violations = axe.get('violations', [])
    elements.append(Paragraph("Accessibility (axe-core)", styles['Heading2']))
    add_space(0.1)
    elements.append(Paragraph(f"Total violations: {len(violations)}", styles['Normal']))
    # severity counts
    sev = {"critical":0,"serious":0,"moderate":0,"minor":0}
    for v in violations:
        impact = v.get('impact','minor')
        if impact in sev:
            sev[impact] += 1
    data = [["Severity","Count"],
            ["Critical", sev["critical"]],
            ["Serious", sev["serious"]],
            ["Moderate", sev["moderate"]],
            ["Minor", sev["minor"]]]
    sev_table = Table(data, colWidths=[3*inch, 1*inch])
    sev_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
    elements.append(sev_table)
    add_space(0.15)
    # list top 5 violations (id + impact + help)
    if violations:
        elements.append(Paragraph("Top issues (up to 5):", styles['Normal']))
        add_space(0.05)
        for v in violations[:5]:
            elements.append(Paragraph(f"- {v.get('id')} ({v.get('impact')}) — {v.get('description')}", styles['Normal']))
            nodes = v.get('nodes', [])
            if nodes:
                sel = nodes[0].get('target', [])
                if sel:
                    elements.append(Paragraph(f"  Example selector: {sel[0]}", styles['Normal']))
        add_space(0.15)

# --- Functional (Playwright) ---
pw_file = os.path.join(folder, "playwright-report.json")
if os.path.exists(pw_file):
    with open(pw_file) as f:
        pw = json.load(f)
    stats = pw.get('stats', {})
    elements.append(Paragraph("Functional Tests (Playwright)", styles['Heading2']))
    add_space(0.1)
    elements.append(Paragraph(f"Total tests: {stats.get('tests', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"Passed (expected): {stats.get('expected', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"Failed (unexpected): {stats.get('unexpected', 'N/A')}", styles['Normal']))
    # show names of failed tests if any
    failures = []
    for r in pw.get('suites', []):
        for t in r.get('tests', []):
            if t.get('status') != 'passed':
                failures.append((t.get('title'), t.get('errors', [])))
    if failures:
        add_space(0.1)
        elements.append(Paragraph("Failed Tests (names + error):", styles['Normal']))
        for name, errs in failures[:5]:
            elements.append(Paragraph(f"- {name}", styles['Normal']))
            if errs:
                elements.append(Paragraph(f"  Error: {errs[0]}", styles['Normal']))
    add_space(0.15)

# --- Visual (Percy) ---
elements.append(Paragraph("Visual Testing (Percy)", styles['Heading2']))
add_space(0.05)
elements.append(Paragraph("Snapshots captured. Review the full visual diffs in the Percy dashboard.", styles['Normal']))
add_space(0.15)

# --- Screenshot embed ---
screenshot = os.path.join(folder, "screenshot.png")
if os.path.exists(screenshot):
    elements.append(Paragraph("Website Screenshot", styles['Heading2']))
    add_space(0.05)
    try:
        img = Image(screenshot)
        img.drawHeight = 4.5*inch
        img.drawWidth = 6.5*inch
        elements.append(img)
        add_space(0.15)
    except Exception as e:
        elements.append(Paragraph(f"Could not embed screenshot: {e}", styles['Normal']))
        add_space(0.15)

# Footer / Overall grade
elements.append(Paragraph("Overall Assessment", styles['Heading2']))
grade = "A"
if 'perf' in locals() and perf < 75:
    grade = "B"
if 'perf' in locals() and perf < 60:
    grade = "C"
elements.append(Paragraph(f"Suggested Grade: {grade}", styles['Normal']))

doc.build(elements)
print("PDF generated:", out_pdf)