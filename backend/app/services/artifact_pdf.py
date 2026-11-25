from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)
from reportlab.platypus.tableofcontents import TableOfContents


def _register_fonts() -> None:
    candidates = (
        (Path("/usr/share/fonts/truetype/dejavu"), "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),
        (Path("/System/Library/Fonts/Supplemental"), "Arial.ttf", "Arial Bold.ttf"),
    )
    for folder, regular, bold in candidates:
        if (folder / regular).is_file() and (folder / bold).is_file():
            pdfmetrics.registerFont(TTFont("LoanScope", str(folder / regular)))
            pdfmetrics.registerFont(TTFont("LoanScope-Bold", str(folder / bold)))
            pdfmetrics.registerFontFamily("LoanScope", normal="LoanScope", bold="LoanScope-Bold")
            return


_register_fonts()
FONT = "LoanScope" if "LoanScope" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
BOLD = f"{FONT}-Bold"
INK = HexColor("#172331")
ACCENT = HexColor("#27604e")
MUTED = HexColor("#526170")
TITLE = ParagraphStyle(
    "Title", fontName=BOLD, fontSize=23, leading=29, textColor=INK, spaceAfter=19
)
SECTION = ParagraphStyle(
    "Section",
    fontName=BOLD,
    fontSize=12,
    leading=16,
    textColor=ACCENT,
    spaceBefore=8,
    spaceAfter=7,
    keepWithNext=True,
)
BODY = ParagraphStyle(
    "Body", fontName=FONT, fontSize=10, leading=15, textColor=INK, alignment=TA_LEFT, spaceAfter=4
)
IDENTIFIERS = {"id": "ID", "requirement_id": "Requirement ID"}
SRS_SECTION = ParagraphStyle("SRS section", parent=SECTION, fontSize=15, leading=20)


class SrsHeading(Paragraph):
    def __init__(self, title: str, level: int, anchor: str) -> None:
        super().__init__(escape(title), SECTION if level else SRS_SECTION)
        self.title = title
        self.level = level
        self.anchor = anchor


class ContentsDocument(SimpleDocTemplate):
    def afterFlowable(self, flowable: Flowable) -> None:
        if isinstance(flowable, SrsHeading):
            self.canv.bookmarkPage(flowable.anchor)
            self.notify(
                "TOCEntry", (flowable.level, escape(flowable.title), self.page, flowable.anchor)
            )


def _fill_pdf(story: list[Flowable], value: Any, indent: int = 0, label: str = "") -> None:
    style = ParagraphStyle("Field", parent=BODY, leftIndent=indent)
    prefix = f"<b>{escape(label)}</b> " if label else ""
    if isinstance(value, dict) and value:
        if label:
            style.keepWithNext = True
            story.append(Paragraph(prefix, style))
        for key in sorted(value, key=lambda key: key not in IDENTIFIERS):
            field = IDENTIFIERS.get(
                key, key if key.isupper() else key.replace("_", " ").capitalize()
            )
            entry = value[key]
            _fill_pdf(story, entry, indent + (12 if label else 0), f"{field}:")
    elif isinstance(value, list) and value:
        if label:
            style.keepWithNext = True
            story.append(Paragraph(prefix, style))
        for entry in value:
            entry_indent = indent + (12 if label else 0)
            if not label and indent == 0 and isinstance(entry, dict):
                record: list[Flowable] = []
                _fill_pdf(record, entry, entry_indent)
                story.append(KeepTogether([*record, Spacer(1, 8)]))
            else:
                _fill_pdf(story, entry, entry_indent)
    else:
        text = str(value) if value is not None and value != [] and value != {} else "None recorded"
        story.append(Paragraph(prefix + escape(text).replace("\n", "<br/>"), style))


def render_artifact_pdf(title: str, version: int, sections: list[dict[str, Any]]) -> bytes:
    output = BytesIO()
    with_contents = bool(sections and "level" in sections[0])
    template = ContentsDocument if with_contents else SimpleDocTemplate
    document = template(
        output,
        pagesize=A4,
        title=title,
        author="LoanScope",
        leftMargin=46,
        rightMargin=46,
        topMargin=44,
        bottomMargin=55,
    )
    story: list[Flowable] = [Paragraph(escape(title), TITLE)]
    if with_contents:
        story.append(Paragraph(escape(str(sections[0]["subtitle"])), BODY))
        contents = TableOfContents()
        contents.levelStyles = [
            ParagraphStyle("Contents heading", parent=BODY, fontName=BOLD),
            ParagraphStyle("Contents entry", parent=BODY, leftIndent=16),
        ]
        contents.dotsMinLevel = 0
        story.extend([Paragraph("Table of Contents", SRS_SECTION), contents, PageBreak()])
    for index, section in enumerate(sections):
        heading = str(section["heading"])
        content = section["content"]
        if with_contents:
            header = SrsHeading(heading, section["level"], f"section-{index}")
            if isinstance(content, list) and content and isinstance(content[0], dict):
                first_record: list[Flowable] = [header]
                _fill_pdf(first_record, content[0])
                story.append(KeepTogether([*first_record, Spacer(1, 8)]))
                content = content[1:] or None
            else:
                story.append(header)
        else:
            story.append(Paragraph(escape(heading), SECTION))
        if content is not None:
            _fill_pdf(story, content)

    def footer(canvas: Canvas, _document: SimpleDocTemplate) -> None:
        canvas.saveState()
        width, _ = A4
        canvas.setStrokeColor(HexColor("#d4dedb"))
        canvas.line(46, 39, width - 46, 39)
        canvas.setFillColor(MUTED)
        canvas.setFont(FONT, 9)
        canvas.drawString(46, 25, f"LoanScope  /  Version {version}")
        canvas.drawRightString(width - 46, 25, str(canvas.getPageNumber()))
        canvas.restoreState()

    if with_contents:
        document.multiBuild(story, onFirstPage=footer, onLaterPages=footer)
    else:
        document.build(story, onFirstPage=footer, onLaterPages=footer)
    return output.getvalue()
