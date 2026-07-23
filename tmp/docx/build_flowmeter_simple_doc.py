from pathlib import Path
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "docx" / "VIMS_Internship_Handoff_01_FlowMeter.docx"

BLACK = "000000"
GRAY = "555555"
LIGHT_GRAY = "F2F4F7"
BORDER = "B7B7B7"
CONTENT_DXA = 9360
TABLE_INDENT_DXA = 120


def set_run_font(run, size=11, bold=False, color=BLACK, italic=False):
    run.font.name = "Arial"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Arial")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Arial")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in("w:tcMar")
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tcMar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tcMar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_width(cell, width_dxa):
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = tcPr.first_child_found_in("w:tcW")
    if tcW is None:
        tcW = OxmlElement("w:tcW")
        tcPr.append(tcW)
    tcW.set(qn("w:w"), str(width_dxa))
    tcW.set(qn("w:type"), "dxa")


def set_cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcPr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = tblPr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tblPr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = borders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), BORDER)


def set_table_geometry(table, widths_dxa):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:w"), str(sum(widths_dxa)))
    tblW.set(qn("w:type"), "dxa")
    tblInd = tblPr.find(qn("w:tblInd"))
    if tblInd is None:
        tblInd = OxmlElement("w:tblInd")
        tblPr.append(tblInd)
    tblInd.set(qn("w:w"), str(TABLE_INDENT_DXA))
    tblInd.set(qn("w:type"), "dxa")
    grid = tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            set_cell_width(cell, widths_dxa[idx])
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_table_borders(table)


def set_repeat_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)


def add_table(doc, headers, rows, widths_dxa):
    table = doc.add_table(rows=1, cols=len(headers))
    set_table_geometry(table, widths_dxa)
    set_repeat_table_header(table.rows[0])
    for i, text in enumerate(headers):
        cell = table.rows[0].cells[i]
        set_cell_shading(cell, LIGHT_GRAY)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, size=10, bold=True)
    for values in rows:
        cells = table.add_row().cells
        for i, text in enumerate(values):
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            run = p.add_run(str(text))
            set_run_font(run, size=10)
    set_table_geometry(table, widths_dxa)
    after = doc.add_paragraph()
    after.paragraph_format.space_after = Pt(2)
    return table


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.add_run(text)
    return p


def add_numbered(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.1
    r = p.add_run(text)
    set_run_font(r, size=11)


doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1)
section.right_margin = Inches(1)
section.header_distance = Inches(0.492)
section.footer_distance = Inches(0.492)

# Plain Markdown-like override: Arial, black headings, no running header/footer.
normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
normal.font.size = Pt(11)
normal.font.color.rgb = RGBColor(0, 0, 0)
normal.paragraph_format.space_before = Pt(0)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.1

for style_name, size, before, after in (
    ("Heading 1", 16, 16, 8),
    ("Heading 2", 13, 12, 6),
    ("Heading 3", 12, 8, 4),
):
    style = doc.styles[style_name]
    style.font.name = "Arial"
    style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)
    style.paragraph_format.keep_with_next = True

# Simple opening block; intentionally no cover page, color band, or decorative rule.
title = doc.add_paragraph()
title.paragraph_format.space_before = Pt(0)
title.paragraph_format.space_after = Pt(4)
run = title.add_run("VIMS Internship Handoff - FlowMeter")
set_run_font(run, size=20, bold=True)

subtitle = doc.add_paragraph()
subtitle.paragraph_format.space_after = Pt(12)
run = subtitle.add_run("Main program: Code/FlowMeterMain/FlowMeterMain.ino")
set_run_font(run, size=10.5, color=GRAY)

intro = doc.add_paragraph()
intro.add_run(
    "This document explains the final FlowMeter setup, the main wiring, the settings that can be changed in the program, how to upload the program, and how to read the logged data from the microSD card."
)

add_heading(doc, "1. System Overview", 1)
doc.add_paragraph(
    "The final system has three main components: an Adafruit Feather M0, a YF-DN80 flowmeter, and a DS3231 real-time clock (RTC). The LiPo battery connects to the Feather. The flowmeter is powered from the Feather BAT pin, so it receives the battery voltage directly. The microSD card is inserted into the Feather's built-in SD card slot."
)
doc.add_paragraph(
    "The flowmeter sends a pulse signal to the Feather. A resistor voltage divider is used on the signal line before it reaches D11 so that the signal voltage is safe for the Feather's 3.3 V logic."
)

add_heading(doc, "2. Wiring", 1)
wiring_rows = [
    ("LiPo battery", "Feather battery connector", "Main power for the system."),
    ("Feather BAT", "YF-DN80 power / red wire", "Supplies the battery voltage directly to the flowmeter."),
    ("Feather GND", "YF-DN80 ground / black wire", "The Feather and flowmeter must share the same ground."),
    ("YF-DN80 signal / yellow wire", "Resistor voltage divider, then Feather D11", "D11 is the flow pulse input used by the main program."),
    ("Feather 3V", "DS3231 VCC", "Powers the RTC at 3.3 V."),
    ("Feather GND", "DS3231 GND", "Common ground."),
    ("Feather SDA", "DS3231 SDA", "I2C data connection."),
    ("Feather SCL", "DS3231 SCL", "I2C clock connection."),
    ("microSD card", "Feather built-in SD slot", "No extra SD wiring is required. The program uses CS pin D4."),
]
add_table(doc, ["From", "To", "Notes"], wiring_rows, [2800, 3200, 3360])

p = doc.add_paragraph()
r = p.add_run("Important: ")
set_run_font(r, bold=True)
r = p.add_run("the YF-DN80 requires at least about 3.5 V to operate. If the battery voltage becomes too low, the flowmeter may stop working before the Feather turns off.")
set_run_font(r)

add_heading(doc, "3. Main Program Settings", 1)
doc.add_paragraph("The following values are near the top of FlowMeterMain.ino and can be changed before uploading:")
settings_rows = [
    ("FLOW_PIN", "11", "Flowmeter signal input. Keep this at 11 unless the signal wire is moved."),
    ("SD_CS_PIN", "4", "Chip-select pin for the Feather's built-in SD card."),
    ("K_FACTOR_HZ_PER_L_MIN", "0.45", "Main flow conversion value. Change this only when a new calibration value is available."),
    ("CALIBRATION_SCALE", "1.0", "Optional multiplier for the calculated flow. Normally keep at 1.0."),
    ("FLOW_OFFSET_L_MIN", "0.0", "Optional flow offset. Normally keep at 0.0."),
    ("MIN_VALID_FLOW_L_MIN", "0.0", "Values below this limit are recorded as zero. It can be increased slightly if there is low-level noise when no water is flowing."),
    ("SAMPLE_INTERVAL_MS", "10000", "Logging interval in milliseconds. 10000 means one row every 10 seconds."),
    ("FORCE_SET_RTC_TO_COMPILE_TIME", "false", "Set to true for one upload to set the RTC, then return it to false and upload again."),
]
add_table(doc, ["Setting", "Current value", "Purpose"], settings_rows, [3300, 1600, 4460])

add_heading(doc, "4. Uploading the Main Program", 1)
doc.add_paragraph("Use the Arduino IDE with the Adafruit SAMD board package and the RTClib library installed.")
for step in (
    "Connect the Feather M0 to the computer with a USB cable.",
    "Open Code/FlowMeterMain/FlowMeterMain.ino in the Arduino IDE.",
    "Select Adafruit Feather M0 as the board and select the correct COM port.",
    "Check the program settings listed above.",
    "Click Upload.",
    "Open Serial Monitor at 115200 baud.",
    "Confirm that the RTC is detected, the SD card initializes, and the message 'Logger ready' appears.",
):
    add_numbered(doc, step)

add_heading(doc, "5. Setting the RTC", 1)
for step in (
    "Change FORCE_SET_RTC_TO_COMPILE_TIME to true.",
    "Compile and upload the program once.",
    "Check the RTC time in Serial Monitor.",
    "Change FORCE_SET_RTC_TO_COMPILE_TIME back to false and upload again.",
):
    add_numbered(doc, step)

add_heading(doc, "6. Logging and Reading the SD Card", 1)
doc.add_paragraph(
    "Insert a FAT16- or FAT32-formatted microSD card into the Feather before turning the system on. Each time the Feather starts, the program creates a new CSV file using the RTC date and time."
)

p = doc.add_paragraph()
r = p.add_run("File path: ")
set_run_font(r, bold=True)
r = p.add_run("/YYYYMMDD/HHMMSS.CSV")
set_run_font(r, size=10.5)

sd_rows = [
    ("timestamp", "Date and time from the RTC."),
    ("session_elapsed_seconds", "Seconds since the Feather restarted."),
    ("sample_number", "Sample number for the current session."),
    ("pulses", "Raw flowmeter pulse count for the sample interval."),
    ("frequency_hz", "Pulse frequency."),
    ("flow_rate_l_min", "Calculated flow rate in liters per minute."),
    ("total_volume_l", "Accumulated volume since the last restart."),
]
add_table(doc, ["CSV column", "Meaning"], sd_rows, [3000, 6360])

add_heading(doc, "To read the data", 2)
for step in (
    "Turn off power to the Feather.",
    "Remove the microSD card and insert it into a computer.",
    "Open the folder named with the logging date.",
    "Open the CSV file in Excel, Google Sheets, or a text editor.",
):
    add_numbered(doc, step)

p = doc.add_paragraph()
r = p.add_run("Note: ")
set_run_font(r, bold=True)
r = p.add_run("total_volume_l resets to zero whenever the Feather restarts. It is the total for one power-on session, not a permanent lifetime total.")
set_run_font(r)

add_heading(doc, "7. Quick Troubleshooting", 1)
trouble_rows = [
    ("No flow reading", "Check the BAT power connection, common ground, voltage-divider signal connection, and D11."),
    ("RTC not found", "Check 3V, GND, SDA, and SCL."),
    ("Wrong time", "Use the one-time RTC setting procedure, then return the setting to false."),
    ("SD initialization failed", "Check that the card is inserted and formatted as FAT16 or FAT32."),
    ("Flow value is too high or low", "Check K_FACTOR_HZ_PER_L_MIN and confirm the correct calibration value."),
]
add_table(doc, ["Problem", "Check"], trouble_rows, [3000, 6360])

doc.core_properties.title = "VIMS Internship Handoff - FlowMeter"
doc.core_properties.subject = "Simple FlowMeter wiring, upload, settings, and SD card guide"
doc.core_properties.author = "VIMS"
doc.core_properties.keywords = "FlowMeter, Feather M0, YF-DN80, DS3231, SD card"
doc.save(OUT)
print(OUT)
