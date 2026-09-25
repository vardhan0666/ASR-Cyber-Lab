"""
PDF report rendering service.

Renders the JSON report payload produced by app.services.report_service
into a PDF document using reportlab. This module performs no scoring or
enrichment of its own — it only formats data that has already been
computed and validated elsewhere in the pipeline. Every dynamic string is
HTML-escaped before being placed into a reportlab Paragraph, since
Paragraph markup is XML-based and raw service banners/descriptions may
contain characters such as '&', '<', or '>'.
"""

import html
import io
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPORTS_OUTPUT_DIR = os.path.join(os.getcwd(), "reports_output")

_SEVERITY_COLORS = {
    "critical": colors.HexColor("#7f1d1d"),
    "high": colors.HexColor("#b91c1c"),
    "medium": colors.HexColor("#b45309"),
    "low": colors.HexColor("#1d4ed8"),
    "info": colors.HexColor("#374151"),
}


def _esc(value: Optional[Any]) -> str:
    """HTML-escape a value for safe use inside a reportlab Paragraph."""
    if value is None:
        return ""
    return html.escape(str(value))


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            spaceBefore=14,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="FindingTitle",
            parent=styles["Heading3"],
            spaceBefore=10,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
        )
    )
    return styles


def generate_pdf_bytes(report_data: Dict[str, Any]) -> bytes:
    """Render the report payload (as built by
    app.services.report_service.build_scan_report) into PDF bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title="ASR-Cyber-Lab Security Report",
    )
    styles = _build_styles()
    elements: List[Any] = []

    metadata = report_data.get("report_metadata", {})
    scan = report_data.get("scan", {})
    target = report_data.get("target", {})
    hosts = report_data.get("hosts", [])
    findings = report_data.get("findings", [])
    summary = report_data.get("summary", {})

    elements.append(Paragraph("ASR-Cyber-Lab Security Report", styles["Title"]))
    elements.append(Paragraph(_esc(metadata.get("disclaimer", "")), styles["SmallBody"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Scan Overview", styles["SectionHeading"]))
    overview_rows = [
        ["Target Name", _esc(target.get("name"))],
        ["Target Address", _esc(target.get("address"))],
        ["Asset Importance", _esc(target.get("asset_importance"))],
        ["Scan Profile", _esc(scan.get("profile"))],
        ["Scan Status", _esc(scan.get("status"))],
        ["Started At", _esc(scan.get("started_at"))],
        ["Completed At", _esc(scan.get("completed_at"))],
        ["Report Generated At", _esc(metadata.get("generated_at"))],
    ]
    overview_table = Table(overview_rows, colWidths=[2.0 * inch, 4.3 * inch])
    overview_table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
            ]
        )
    )
    elements.append(overview_table)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Findings Summary", styles["SectionHeading"]))
    severity_counts = summary.get("findings_by_severity", {})
    summary_rows = [["Severity", "Count"]] + [
        [_esc(str(level).capitalize()), str(count)] for level, count in severity_counts.items()
    ]
    summary_table = Table(summary_rows, colWidths=[2.0 * inch, 2.0 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(
        Paragraph(
            f"Total hosts discovered: {summary.get('total_hosts', 0)} | "
            f"Total findings: {summary.get('total_findings', 0)}",
            styles["SmallBody"],
        )
    )
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Discovered Hosts", styles["SectionHeading"]))
    if not hosts:
        elements.append(
            Paragraph("No hosts were discovered during this scan.", styles["SmallBody"])
        )
    for host in hosts:
        host_header = _esc(host.get("ip_address"))
        if host.get("hostname"):
            host_header += f" ({_esc(host.get('hostname'))})"
        elements.append(Paragraph(host_header, styles["FindingTitle"]))

        os_line = "OS: "
        os_line += _esc(host.get("os_name")) if host.get("os_name") else "Not determined"
        if host.get("os_accuracy") is not None:
            os_line += f" (confidence {host.get('os_accuracy')}%)"
        elements.append(Paragraph(os_line, styles["SmallBody"]))

        ports = host.get("ports", [])
        if ports:
            port_rows = [["Port", "Protocol", "State", "Service", "Product", "Version"]]
            for p in ports:
                port_rows.append(
                    [
                        str(p.get("port_number")),
                        _esc(p.get("protocol")),
                        _esc(p.get("state")),
                        _esc(p.get("service_name")),
                        _esc(p.get("product")),
                        _esc(p.get("version")),
                    ]
                )
            port_table = Table(
                port_rows,
                colWidths=[
                    0.6 * inch,
                    0.7 * inch,
                    0.7 * inch,
                    1.2 * inch,
                    1.4 * inch,
                    1.4 * inch,
                ],
            )
            port_table.setStyle(
                TableStyle(
                    [
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ]
                )
            )
            elements.append(port_table)
        else:
            elements.append(Paragraph("No open ports discovered.", styles["SmallBody"]))
        elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph("Security Findings", styles["SectionHeading"]))
    if not findings:
        elements.append(
            Paragraph("No findings were generated for this scan.", styles["SmallBody"])
        )

    for finding in findings:
        severity = str(finding.get("severity", "info"))
        color = _SEVERITY_COLORS.get(severity, colors.black)
        title_style = ParagraphStyle(
            name="FindingTitleColored", parent=styles["FindingTitle"], textColor=color
        )
        elements.append(
            Paragraph(
                f"[{_esc(severity.upper())}] {_esc(finding.get('title'))}", title_style
            )
        )
        risk_score = finding.get("risk_score", 0) or 0
        elements.append(
            Paragraph(
                f"Risk Score: {risk_score:.1f}/100 | "
                f"Category: {_esc(finding.get('category'))} | "
                f"Status: {_esc(finding.get('status'))}",
                styles["SmallBody"],
            )
        )
        elements.append(Paragraph(_esc(finding.get("description")), styles["SmallBody"]))

        explanation = finding.get("risk_explanation", [])
        if explanation:
            elements.append(Paragraph("Risk Explanation:", styles["SmallBody"]))
            explanation_items = [
                ListItem(Paragraph(_esc(item), styles["SmallBody"])) for item in explanation
            ]
            elements.append(ListFlowable(explanation_items, bulletType="bullet"))

        for v in finding.get("vulnerabilities", []):
            if v.get("data_available"):
                vuln_line = (
                    f"Vulnerability: {_esc(v.get('cve_id'))} "
                    f"(CVSS {v.get('cvss_score')})"
                )
            else:
                vuln_line = (
                    "Vulnerability intelligence: unavailable for the "
                    "detected product/version."
                )
            elements.append(Paragraph(vuln_line, styles["SmallBody"]))

        if finding.get("remediation"):
            elements.append(
                Paragraph(f"Remediation: {_esc(finding.get('remediation'))}", styles["SmallBody"])
            )

        elements.append(Spacer(1, 0.15 * inch))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def save_pdf_report(report_data: Dict[str, Any], scan_id: str) -> str:
    """Render and persist a PDF report to disk, returning the file path."""
    os.makedirs(REPORTS_OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    filename = f"scan_{scan_id}_{timestamp}.pdf"
    file_path = os.path.join(REPORTS_OUTPUT_DIR, filename)

    pdf_bytes = generate_pdf_bytes(report_data)
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    return file_path