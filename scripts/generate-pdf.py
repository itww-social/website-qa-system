import os
import json
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

folder = os.environ.get("RESULT_FOLDER")
url = os.environ.get("TARGET_URL")

doc = SimpleDocTemplate(os.path.join(folder, "Client-QA-Report.pdf"))
elements = []
styles = getSampleStyleSheet()

elements.append(Paragraph("<b>Website QA Report</b>", styles["Heading1"]))
elements.append(Spacer(1, 0.2 * inch))
elements.append(Paragraph(f"Website: {url}", styles["Normal"]))
elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
elements.append(Spacer(1, 0.3 * inch))

# -----------------------
# Lighthouse Section
# -----------------------
lh_path = os.path.join(folder, "lighthouse.json")
if os.path.exists(lh_path):
    with open(lh_path) as f:
        lh = json.load(f)

    categories = lh["categories"]

    data = [
        ["Metric", "Score"],
        ["Performance", round(categories["performance"]["score"] * 100)],
        ["Accessibility", round(categories["accessibility"]["score"] * 100)],
        ["Best Practices", round(categories["best-practices"]["score"] * 100)],
        ["SEO", round(categories["seo"]["score"] * 100)],
    ]

    elements.append(Paragraph("<b>Lighthouse Scores</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Table(data))
    elements.append(Spacer(1, 0.3 * inch))

# -----------------------
# Accessibility Section
# -----------------------
axe_path = os.path.join(folder, "accessibility.json")
if os.path.exists(axe_path):
    with open(axe_path) as f:
        axe = json.load(f)

    violations = axe.get("violations", [])

    elements.append(Paragraph("<b>Accessibility (axe)</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Total Violations: {len(violations)}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

# -----------------------
# Playwright Section
# -----------------------
pw_path = os.path.join(folder, "playwright-report.json")
if os.path.exists(pw_path):
    with open(pw_path) as f:
        pw = json.load(f)

    stats = pw.get("stats", {})

    elements.append(Paragraph("<b>Functional Testing (Playwright)</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Passed: {stats.get('expected', 0)}", styles["Normal"]))
    elements.append(Paragraph(f"Failed: {stats.get('unexpected', 0)}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

# -----------------------
# Percy Section
# -----------------------
elements.append(Paragraph("<b>Visual Testing (Percy)</b>", styles["Heading2"]))
elements.append(Spacer(1, 0.2 * inch))
elements.append(Paragraph("Visual comparison available in Percy dashboard.", styles["Normal"]))

# -----------------------
# Screenshot Section
# -----------------------
screenshot_path = os.path.join(folder, "screenshot.png")

if os.path.exists(screenshot_path):
    elements.append(Paragraph("<b>Website Screenshot</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    img = Image(screenshot_path)
    img.drawHeight = 5 * inch
    img.drawWidth = 6 * inch

    elements.append(img)
    elements.append(Spacer(1, 0.3 * inch))

doc.build(elements)