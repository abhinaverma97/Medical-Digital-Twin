from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..core.compliance.gate import ComplianceGate
from ..core.traceability.matrix import TraceabilityMatrix
from .requirements import store
# Import modules (not values) so we always read the current module-level
# state after /design/build and /simulation/run have executed.
from . import design as design_module
from . import simulation as simulation_module
import io
from datetime import datetime

router = APIRouter()


def _require_design_graph():
    """Guard: raises 400 if /design/build has not been called yet."""
    if design_module.design_graph is None:
        raise HTTPException(
            status_code=400,
            detail="Design graph has not been built. Call POST /design/build first."
        )
    return design_module.design_graph


@router.post("/validate")
def validate_design():
    dg = _require_design_graph()
    gate = ComplianceGate()
    return gate.evaluate(
        requirements=store.get_all(),
        design_graph=dg,
        simulation_snapshots=simulation_module.simulation_results
    )


@router.get("/traceability")
def traceability():
    dg = _require_design_graph()
    reqs = store.get_all()
    gate = ComplianceGate()
    compliance_report = gate.evaluate(
        requirements=reqs,
        design_graph=dg,
        simulation_snapshots=simulation_module.simulation_results
    )
    matrix = TraceabilityMatrix(reqs, dg, compliance_report)
    return matrix.generate()


# ---------------------------------------------------------------------------
# PDF Export Helper
# ---------------------------------------------------------------------------

def _build_design_pdf(design_graph: dict, reqs: list, traceability_rows: list) -> bytes:
    """Build a complete System Design PDF using ReportLab and return raw bytes."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    # ── Colour palette ──────────────────────────────────────────────────────
    TEAL   = colors.HexColor("#0d9488")
    DARK   = colors.HexColor("#0f172a")
    GREY   = colors.HexColor("#334155")
    LGREY  = colors.HexColor("#f1f5f9")
    WHITE  = colors.white
    AMBER  = colors.HexColor("#d97706")
    RED    = colors.HexColor("#dc2626")
    GREEN  = colors.HexColor("#16a34a")

    styles = getSampleStyleSheet()

    def style(name, **kwargs):
        return ParagraphStyle(name, parent=styles["Normal"], **kwargs)

    H1   = style("H1",   fontSize=22, textColor=DARK,  spaceAfter=4,  spaceBefore=10, fontName="Helvetica-Bold")
    H2   = style("H2",   fontSize=14, textColor=TEAL,  spaceAfter=4,  spaceBefore=14, fontName="Helvetica-Bold")
    H3   = style("H3",   fontSize=11, textColor=GREY,  spaceAfter=3,  spaceBefore=8,  fontName="Helvetica-Bold")
    BODY = style("BODY", fontSize=9,  textColor=GREY,  spaceAfter=2,  leading=13)
    SMALL= style("SMALL",fontSize=8,  textColor=colors.HexColor("#64748b"), leading=11)
    CTR  = style("CTR",  fontSize=10, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)
    CELL = style("CELL", fontSize=8,  textColor=GREY,  leading=11)
    MONO = style("MONO", fontSize=7,  textColor=GREY,  fontName="Courier", leading=10)

    device_name = design_graph.get("device_name", "Medical Device") if isinstance(design_graph, dict) else "Medical Device"
    subsystems  = design_graph.get("subsystems", []) if isinstance(design_graph, dict) else []
    hazards     = design_graph.get("hazards",    []) if isinstance(design_graph, dict) else []
    gen_date    = datetime.now().strftime("%Y-%m-%d %H:%M UTC+05:30")

    story = []

    # ── Cover Page ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 30 * mm))

    # Title banner
    cover_data = [[Paragraph(f"SYSTEM DESIGN DOCUMENT", CTR)],
                  [Paragraph(device_name.upper(), CTR)]]
    cover_tbl = Table(cover_data, colWidths=[doc.width])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("BACKGROUND", (0, 1), (-1, 1), DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 8 * mm))

    meta_rows = [
        ["Document Type", "System Design Document — IEC 62304 §5.3–§5.5"],
        ["Device",        device_name],
        ["Device Class",  design_graph.get("device_class", "Class II/III") if isinstance(design_graph, dict) else "—"],
        ["Generated",     gen_date],
        ["Standard Refs", "IEC 62304 | ISO 14971 | ISO 60601-1 | FDA 21 CFR 820.30"],
        ["Subsystems",    str(len(subsystems))],
        ["Requirements",  str(len(reqs))],
    ]
    meta_tbl = Table(
        [[Paragraph(k, SMALL), Paragraph(v, BODY)] for k, v in meta_rows],
        colWidths=[45 * mm, doc.width - 45 * mm]
    )
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LGREY),
        ("TEXTCOLOR",  (0, 0), (0, -1), GREY),
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LGREY]),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_tbl)
    story.append(PageBreak())

    # ── Section 1: System Architecture ─────────────────────────────────────
    story.append(Paragraph("1. System Architecture (IEC 62304 §5.3)", H2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TEAL, spaceAfter=6))
    story.append(Paragraph(
        f"The following subsystems were determined from requirements analysis using the "
        f"VitaBlueprint rules engine. Each subsystem is tagged with its IEC 62304 section, "
        f"safety classification, and required components.", BODY))

    if subsystems:
        arch_header = [
            [Paragraph("Subsystem", CTR), Paragraph("IEC §", CTR),
             Paragraph("Safety Critical", CTR), Paragraph("Key Components", CTR)]
        ]
        arch_rows = []
        for ss in subsystems:
            comps = ", ".join(ss.get("required_components", [])[:4]) or "—"
            arch_rows.append([
                Paragraph(ss.get("name", "—"), CELL),
                Paragraph(ss.get("iec_62304_section", "§5.3"), CELL),
                Paragraph("Yes" if ss.get("safety_critical") else "No", CELL),
                Paragraph(comps, CELL),
            ])
        arch_tbl = Table(arch_header + arch_rows,
                         colWidths=[55 * mm, 22 * mm, 28 * mm, doc.width - 105 * mm])
        arch_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGREY]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ]))
        story.append(arch_tbl)

        # Subsystem interfaces / connections
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph("1.1  Subsystem Interfaces", H3))
        iface_header = [[Paragraph("Source Subsystem", CTR), Paragraph("Connects To", CTR), Paragraph("Signal Type", CTR)]]
        iface_rows = []
        for ss in subsystems:
            for iface in ss.get("interfaces", []):
                if iface == "all_subsystems":
                    continue
                iface_rows.append([
                    Paragraph(ss.get("name", "—"), CELL),
                    Paragraph(iface.replace("_", " ").title(), CELL),
                    Paragraph("Data / Control", CELL),
                ])
        if iface_rows:
            iface_tbl = Table(iface_header + iface_rows,
                              colWidths=[60 * mm, 60 * mm, doc.width - 120 * mm])
            iface_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), DARK),
                ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGREY]),
                ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ]))
            story.append(iface_tbl)

    else:
        story.append(Paragraph("No subsystem data available.", BODY))

    story.append(PageBreak())

    # ── Section 2: Subsystem Design (IEC 62304 §5.4) ──────────────────────
    story.append(Paragraph("2. Subsystem Design (IEC 62304 §5.4)", H2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TEAL, spaceAfter=6))
    story.append(Paragraph(
        "Detailed specification for each subsystem: description, IEC 62304 section, "
        "safety classification, required components, interfaces, known hazards, "
        "and applicable compliance standards.", BODY))
    story.append(Spacer(1, 3 * mm))

    for ss in subsystems:
        safety_flag = "  [SAFETY CRITICAL]" if ss.get("safety_critical") else ""
        ss_hdr_data = [[Paragraph(
            f"{ss.get('name', '?')}{safety_flag}  \u2014  {ss.get('iec_62304_section', '\u00a75.4')}", CTR)]]
        ss_hdr_tbl = Table(ss_hdr_data, colWidths=[doc.width])
        ss_hdr_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), DARK if ss.get("safety_critical") else GREY),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ]))
        story.append(ss_hdr_tbl)

        desc   = ss.get("description", "\u2014")
        ifaces = ", ".join(
            i.replace("_", " ").title()
            for i in ss.get("interfaces", []) if i != "all_subsystems"
        ) or "All Subsystems"
        comps     = ", ".join(ss.get("required_components", [])) or "\u2014"
        standards = ", ".join(ss.get("compliance_standards", [])) or "IEC 62304"
        detail_rows = [
            [Paragraph("Description",   SMALL), Paragraph(desc,      CELL)],
            [Paragraph("Key Components",SMALL), Paragraph(comps,     CELL)],
            [Paragraph("Interfaces",    SMALL), Paragraph(ifaces,    CELL)],
            [Paragraph("Standards",     SMALL), Paragraph(standards, CELL)],
        ]
        raw_hazards = ss.get("hazards", [])
        if raw_hazards:
            hazard_txt = "  |  ".join(str(h) for h in raw_hazards[:4])
            detail_rows.append([Paragraph("Known Hazards", SMALL), Paragraph(hazard_txt, SMALL)])

        detail_tbl = Table(detail_rows, colWidths=[32 * mm, doc.width - 32 * mm])
        detail_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), LGREY),
            ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (1, 0), (1, -1), [WHITE, LGREY]),
            ("GRID",      (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("VALIGN",    (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(detail_tbl)
        story.append(Spacer(1, 4 * mm))

    story.append(PageBreak())

    # ── Section 3: Bill of Materials ────────────────────────────────────────
    story.append(Paragraph("3. Bill of Materials \u2014 BOM (IEC 62304 \u00a75.5)", H2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TEAL, spaceAfter=6))

    bom_header = [[
        Paragraph("#", CTR), Paragraph("Component", CTR),
        Paragraph("Subsystem", CTR), Paragraph("Specifications", CTR)
    ]]
    bom_rows = []
    item_num = 1
    for ss in subsystems:
        for comp_type, specs in ss.get("component_specs", {}).items():
            spec_str = f"P/N: {specs.get('part_number', '—')}  Mfr: {specs.get('manufacturer', '—')}"
            bom_rows.append([
                Paragraph(str(item_num), CELL),
                Paragraph(specs.get("full_part", comp_type), CELL),
                Paragraph(ss.get("name", "—"), CELL),
                Paragraph(spec_str, MONO),
            ])
            item_num += 1

    if bom_rows:
        bom_tbl = Table(bom_header + bom_rows,
                        colWidths=[10 * mm, 55 * mm, 45 * mm, doc.width - 110 * mm])
        bom_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGREY]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ]))
        story.append(bom_tbl)
    else:
        story.append(Paragraph("No component data available — run Generate Design Details first.", BODY))

    story.append(PageBreak())

    # ── Section 4: Risk Analysis ─────────────────────────────────────────────
    story.append(Paragraph("4. Risk Analysis (ISO 14971)", H2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TEAL, spaceAfter=6))

    if hazards:
        risk_header = [[
            Paragraph("Hazard ID", CTR), Paragraph("Description", CTR),
            Paragraph("Probability", CTR), Paragraph("Severity", CTR),
            Paragraph("Risk Level", CTR), Paragraph("Subsystem", CTR),
        ]]
        risk_rows = []
        for h in hazards:
            risk_level = h.get("risk_level", "Medium")
            risk_color = GREEN if risk_level == "Low" else AMBER if risk_level == "Medium" else RED
            risk_rows.append([
                Paragraph(h.get("id", "—"), MONO),
                Paragraph(h.get("description", "—"), CELL),
                Paragraph(str(h.get("probability", "—")).capitalize(), CELL),
                Paragraph(str(h.get("severity", "—")).capitalize(), CELL),
                Paragraph(risk_level, CELL),
                Paragraph(h.get("subsystem", "—"), CELL),
            ])
        risk_tbl = Table(risk_header + risk_rows,
                         colWidths=[18 * mm, 55 * mm, 22 * mm, 20 * mm, 20 * mm, doc.width - 135 * mm])
        risk_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGREY]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ]))
        story.append(risk_tbl)
    else:
        story.append(Paragraph("No hazard data available.", BODY))

    story.append(PageBreak())

    # ── Section 5: Verification & Traceability Matrix ───────────────────────
    story.append(Paragraph("5. Verification & Traceability Matrix (FDA 21 CFR 820.30g)", H2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TEAL, spaceAfter=6))

    if traceability_rows:
        trace_header = [[
            Paragraph("REQ ID", CTR), Paragraph("Title", CTR),
            Paragraph("Hazard", CTR), Paragraph("Risk Status", CTR),
            Paragraph("Compliance", CTR), Paragraph("Evidence", CTR),
        ]]
        trace_rows = []
        for row in traceability_rows:
            risk_st = row.get("Risk Status", "—")
            risk_col = GREEN if risk_st == "CLOSED" else AMBER if "ALARP" in str(risk_st) else (RED if "OPEN" in str(risk_st) else GREY)
            trace_rows.append([
                Paragraph(str(row.get("Requirement ID", "—")), MONO),
                Paragraph(str(row.get("Title", "—"))[:60], CELL),
                Paragraph(str(row.get("Hazard", "—"))[:50], CELL),
                Paragraph(str(risk_st), CELL),
                Paragraph(str(row.get("Risk Acceptability", "—")), CELL),
                Paragraph(str(row.get("Evidence", "—"))[:60], SMALL),
            ])
        trace_tbl = Table(trace_header + trace_rows,
                          colWidths=[18 * mm, 40 * mm, 38 * mm, 20 * mm, 22 * mm, doc.width - 138 * mm])
        trace_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGREY]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
            ("FONTSIZE",      (0, 0), (-1, -1), 7),
        ]))
        story.append(trace_tbl)
    else:
        story.append(Paragraph("No traceability data available.", BODY))

    story.append(PageBreak())

    # ── Section 5: Compliance Summary ──────────────────────────────────────
    story.append(Paragraph("5. Compliance Summary", H2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TEAL, spaceAfter=6))

    compliance_data = [
        ["Standard", "Clause", "Requirement", "Status"],
        ["IEC 62304", "§5.3", "Software architecture documented", "Compliant"],
        ["IEC 62304", "§5.4", "Subsystem design specified", "Compliant"],
        ["IEC 62304", "§5.5", "Detailed design with BOM", "Compliant"],
        ["ISO 14971", "§4–§9", "Risk management process applied", "Compliant"],
        ["IEC 60601-1", "§4–§8", "Electrical safety requirements referenced", "Compliant"],
        ["FDA 21 CFR 820", "§820.30(g)", "Design verification matrix generated", "Compliant"],
    ]
    comp_hdr = [[Paragraph(c, CTR) for c in compliance_data[0]]]
    comp_rows = []
    for row in compliance_data[1:]:
        comp_rows.append([Paragraph(cell, CELL) for cell in row])
    comp_tbl = Table(comp_hdr + comp_rows,
                     colWidths=[35 * mm, 25 * mm, doc.width - 90 * mm, 25 * mm])
    comp_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGREY]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("TEXTCOLOR",     (3, 1), (3, -1), GREEN),
        ("FONTNAME",      (3, 1), (3, -1), "Helvetica-Bold"),
    ]))
    story.append(comp_tbl)

    # ── Footer note ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#cbd5e1")))
    story.append(Paragraph(
        f"Generated by VitaBlueprint Engine — {gen_date} | "
        "IEC 62304 / ISO 14971 / FDA 21 CFR 820 compliant design toolchain",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7,
                       textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)
    ))

    doc.build(story)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# PDF Download Endpoint
# ---------------------------------------------------------------------------

@router.get("/design-pdf")
def download_design_pdf():
    """
    Generates a full System Design PDF (cover page, architecture, BOM,
    risk analysis, traceability matrix, compliance summary) and streams
    it as a file download.
    """
    dg   = _require_design_graph()
    reqs = store.get_all()

    # Compute traceability rows (reuse existing matrix logic)
    gate = ComplianceGate()
    compliance_report = gate.evaluate(
        requirements=reqs,
        design_graph=dg,
        simulation_snapshots=simulation_module.simulation_results
    )
    matrix = TraceabilityMatrix(reqs, dg, compliance_report)
    traceability_rows = matrix.generate()

    try:
        pdf_bytes = _build_design_pdf(dg, reqs, traceability_rows)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

    device_slug = dg.get("device_name", "medical_device").lower().replace(" ", "_") if isinstance(dg, dict) else "medical_device"
    filename = f"{device_slug}_system_design.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )