import os
import json
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
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

# Lighthouse
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

doc.build(elements)