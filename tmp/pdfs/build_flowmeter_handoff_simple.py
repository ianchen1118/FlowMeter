from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Flowable, HRFlowable
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "VIMS_Internship_Handoff_01_FlowMeter.pdf"

NAVY = HexColor("#173447")
TEAL = HexColor("#087D78")
TEAL_DARK = HexColor("#075E5A")
MINT = HexColor("#E7F4F2")
BLUE_BG = HexColor("#EAF2F8")
AMBER = HexColor("#D79000")
AMBER_BG = HexColor("#FFF4D6")
RED = HexColor("#A43C3C")
INK = HexColor("#263640")
MUTED = HexColor("#60717B")
LINE = HexColor("#CAD5DA")
LIGHT = HexColor("#F5F7F8")
WHITE = colors.white

pdfmetrics.registerFont(TTFont("Noto", r"C:\Windows\Fonts\NotoSansTC-VF.ttf"))
pdfmetrics.registerFont(TTFont("NotoBold", r"C:\Windows\Fonts\NotoSansTC-VF.ttf"))
pdfmetrics.registerFont(TTFont("Consolas", r"C:\Windows\Fonts\consola.ttf"))

PAGE_W, PAGE_H = A4
MX = 18 * mm
TOP = 18 * mm
BOTTOM = 17 * mm

ss = getSampleStyleSheet()
ss.add(ParagraphStyle(name="BodyX", fontName="Noto", fontSize=9.5, leading=14, textColor=INK, spaceAfter=5))
ss.add(ParagraphStyle(name="SmallX", parent=ss["BodyX"], fontSize=7.8, leading=11, textColor=MUTED))
ss.add(ParagraphStyle(name="H1X", fontName="NotoBold", fontSize=22, leading=28, textColor=NAVY, spaceAfter=8))
ss.add(ParagraphStyle(name="H2X", fontName="NotoBold", fontSize=14, leading=19, textColor=TEAL_DARK, spaceBefore=5, spaceAfter=6))
ss.add(ParagraphStyle(name="H3X", fontName="NotoBold", fontSize=10.5, leading=14, textColor=NAVY, spaceBefore=3, spaceAfter=4))
ss.add(ParagraphStyle(name="CoverX", fontName="NotoBold", fontSize=30, leading=37, textColor=WHITE))
ss.add(ParagraphStyle(name="CoverSubX", fontName="Noto", fontSize=12, leading=18, textColor=HexColor("#D8EBEC")))
ss.add(ParagraphStyle(name="THX", fontName="NotoBold", fontSize=7.8, leading=10.5, textColor=WHITE))
ss.add(ParagraphStyle(name="TCX", fontName="Noto", fontSize=7.4, leading=10.4, textColor=INK))
ss.add(ParagraphStyle(name="CodeX", fontName="Consolas", fontSize=7.5, leading=10.5, textColor=NAVY,
                      backColor=HexColor("#EDF2F4"), borderColor=LINE, borderWidth=0.5,
                      borderPadding=6, spaceAfter=6))
ss.add(ParagraphStyle(name="BulletX", parent=ss["BodyX"], leftIndent=13, firstLineIndent=-8, bulletIndent=2, spaceAfter=2))


def P(text, style="BodyX"):
    return Paragraph(text, ss[style])


def bullet(text):
    return Paragraph(f'<font color="{TEAL.hexval()}">&#8226;</font> {text}', ss["BulletX"])


def title(kicker, heading, subtitle=""):
    out = [P(kicker.upper(), "SmallX"), P(heading, "H1X"), HRFlowable(width="100%", thickness=1.2, color=TEAL, spaceAfter=8)]
    if subtitle:
        out.append(P(subtitle))
    return out


def table(headers, rows, widths):
    data = [[P(h, "THX") for h in headers]] + [[P(str(v), "TCX") for v in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        style.append(("BACKGROUND", (0, i), (-1, i), WHITE if i % 2 else LIGHT))
    t.setStyle(TableStyle(style))
    return t


def note(title_text, body, kind="info"):
    colorset = {
        "info": (TEAL, MINT),
        "warn": (AMBER, AMBER_BG),
        "danger": (RED, HexColor("#FCECEC")),
    }
    accent, bg = colorset[kind]
    t = Table([[P("!" if kind != "info" else "i", "H2X"), P(f"<b>{title_text}</b><br/>{body}", "SmallX")]], colWidths=[10*mm, 156*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), accent),
        ("BACKGROUND", (1, 0), (1, 0), bg),
        ("TEXTCOLOR", (0, 0), (0, 0), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.6, accent),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (1, 0), (1, 0), 7),
        ("RIGHTPADDING", (1, 0), (1, 0), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


class SimpleDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 166 * mm
        self.height = 65 * mm

    def box(self, c, x, y, w, h, name, detail, fill, stroke):
        c.setFillColor(fill); c.setStrokeColor(stroke)
        c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
        c.setFillColor(NAVY); c.setFont("NotoBold", 9)
        c.drawCentredString(x+w/2, y+h-13, name)
        c.setFillColor(MUTED); c.setFont("Noto", 6.5)
        c.drawCentredString(x+w/2, y+9, detail)

    def arrow(self, c, x1, y1, x2, y2, label):
        c.setStrokeColor(TEAL_DARK); c.setFillColor(TEAL_DARK); c.setLineWidth(1.2)
        c.line(x1, y1, x2, y2)
        c.line(x2, y2, x2-4, y2+2); c.line(x2, y2, x2-4, y2-2)
        c.setFont("Noto", 6); c.setFillColor(MUTED)
        c.drawCentredString((x1+x2)/2, y1+5, label)

    def draw(self):
        c = self.canv
        self.box(c, 0, 36*mm, 40*mm, 22*mm, "YF-DN80", "flow pulse output", AMBER_BG, AMBER)
        self.box(c, 61*mm, 30*mm, 45*mm, 34*mm, "Feather M0", "FlowMeterMain.ino", MINT, TEAL)
        self.box(c, 126*mm, 40*mm, 40*mm, 20*mm, "microSD", "CSV storage", BLUE_BG, NAVY)
        self.box(c, 126*mm, 5*mm, 40*mm, 20*mm, "DS3231", "date and time", BLUE_BG, NAVY)
        self.box(c, 0, 4*mm, 40*mm, 20*mm, "Level shifter", "pulse to 3.3 V", HexColor("#FCECEC"), RED)
        self.arrow(c, 40*mm, 47*mm, 61*mm, 47*mm, "to D11")
        self.arrow(c, 106*mm, 47*mm, 126*mm, 47*mm, "SPI / D4")
        self.arrow(c, 106*mm, 20*mm, 126*mm, 15*mm, "I2C")
        self.arrow(c, 40*mm, 14*mm, 61*mm, 37*mm, "3.3 V pulse")


def footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(LINE); canvas.line(MX, 13*mm, PAGE_W-MX, 13*mm)
        canvas.setFont("Noto", 6.8); canvas.setFillColor(MUTED)
        canvas.drawString(MX, 8.5*mm, "VIMS Internship Handoff | FlowMeter")
        canvas.drawRightString(PAGE_W-MX, 8.5*mm, str(doc.page))
    canvas.restoreState()


doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=MX, rightMargin=MX, topMargin=TOP, bottomMargin=BOTTOM,
                      title="VIMS Internship Handoff - FlowMeter", author="VIMS")
frame = Frame(MX, BOTTOM, PAGE_W-2*MX, PAGE_H-TOP-BOTTOM, id="main")
doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])

story = []

# Cover
story += [Spacer(1, 18*mm)]
banner = Table([[P("VIMS INTERNSHIP", "CoverSubX")]], colWidths=[166*mm], rowHeights=[12*mm])
banner.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), TEAL), ("LEFTPADDING", (0,0), (-1,-1), 9), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
story += [banner, Spacer(1, 4*mm)]
cover = Table([[P("FlowMeter<br/>Handoff Guide", "CoverX")]], colWidths=[166*mm], rowHeights=[66*mm])
cover.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), NAVY), ("LEFTPADDING", (0,0), (-1,-1), 10*mm), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
story += [cover, Spacer(1, 6*mm), P("A short guide for wiring, uploading the main program, changing settings, and reading the SD card.", "H2X"), Spacer(1, 13*mm)]
story += [table(["Main program", "Board", "Last reviewed"], [["Code/FlowMeterMain/FlowMeterMain.ino", "Adafruit Feather M0", "July 22, 2026"]], [82*mm, 48*mm, 36*mm]), Spacer(1, 9*mm)]
story += [note("Scope", "This guide only covers the main logger program. It does not describe the separate test or calibration sketches.", "info"), PageBreak()]

# Connections
story += title("01 / HARDWARE", "Component Connections", "Place the Feather M0, RTC, SD card, and level shifter in a dry enclosure. Install the YF-DN80 in the pipe with its flow arrow pointing in the actual flow direction.")
story += [SimpleDiagram(), Spacer(1, 5)]
rows = [
    ("YF-DN80 signal (yellow)", "Level shifter input", "The sensor pulse must be shifted to 3.3 V logic."),
    ("Level shifter output", "Feather D11", "This is FLOW_PIN in the main program."),
    ("YF-DN80 power and ground", "External supply + common GND", "Use the voltage printed on the actual sensor. Connect sensor GND to Feather GND."),
    ("DS3231 VCC / GND", "Feather 3V / GND", "Powering the module at 3.3 V keeps I2C logic safe."),
    ("DS3231 SDA", "Feather SDA", "GPIO 20 on the Feather M0."),
    ("DS3231 SCL", "Feather SCL", "GPIO 21 on the Feather M0."),
    ("microSD CS", "Feather D4", "The main program uses SD_CS_PIN = 4."),
    ("microSD SPI", "Feather SCK / MOSI / MISO", "Only needed for an external SD module."),
]
story += [table(["Component wire", "Connect to", "Note"], rows, [55*mm, 48*mm, 63*mm]), Spacer(1, 7)]
story += [note("Likely board configuration", "D4 matches the built-in SD card on an Adafruit Feather M0 Adalogger. If that is the installed board, simply insert the microSD card; no external SPI wiring is needed.", "info"), Spacer(1, 5)]
story += [note("Electrical safety", "The Feather M0 uses 3.3 V logic. Do not connect a 5 V sensor pulse directly to D11. Confirm the level-shifter output is no higher than 3.3 V before connecting the MCU.", "danger"), PageBreak()]

# Settings
story += title("02 / MAIN PROGRAM", "Settings You Can Change", "Open FlowMeterMain.ino and edit the values near the top of the file before uploading.")
settings = [
    ("FLOW_PIN", "11", "Flow sensor pulse input. Change only if the wire is moved to a different interrupt-capable pin."),
    ("SD_CS_PIN", "4", "SD card chip-select pin. Keep D4 for the Feather M0 Adalogger built-in SD card."),
    ("K_FACTOR_HZ_PER_L_MIN", "0.45", "Main flow conversion value. This directly changes the calculated flow rate."),
    ("CALIBRATION_SCALE", "1.0", "Optional multiplier. Normally leave at 1.0."),
    ("FLOW_OFFSET_L_MIN", "0.0", "Optional flow offset. Normally leave at 0.0."),
    ("MIN_VALID_FLOW_L_MIN", "0.0", "Readings below this value are changed to zero. Increase only if small noise appears when there is no flow."),
    ("SAMPLE_INTERVAL_MS", "10000", "Logging interval in milliseconds. 10000 means one CSV row every 10 seconds."),
    ("FORCE_SET_RTC_TO_COMPILE_TIME", "false", "Temporarily set true to set the RTC from the computer's compile time."),
]
story += [table(["Setting", "Current value", "What it controls"], settings, [56*mm, 31*mm, 79*mm]), Spacer(1, 7)]
story += [P("Flow calculation", "H2X"), P("frequency_hz = pulses / elapsed_seconds<br/>flow_l_min = frequency_hz / K_FACTOR_HZ_PER_L_MIN<br/>flow_l_min = flow_l_min * CALIBRATION_SCALE + FLOW_OFFSET_L_MIN", "CodeX")]
story += [note("Current K factor", "The main program currently uses 0.45, while the YF-DN80 nominal relationship is commonly F = 0.5 x Q. Keep 0.45 only if it came from the installed sensor's field calibration; otherwise verify it with a measured-volume test.", "warn"), Spacer(1, 6)]
story += [P("Setting the RTC", "H2X")]
for text in [
    "Set FORCE_SET_RTC_TO_COMPILE_TIME to true.",
    "Compile and upload once, then check the printed RTC time.",
    "Change the setting back to false and upload again for normal operation.",
]: story.append(bullet(text))
story += [PageBreak()]

# Upload and run
story += title("03 / UPLOAD", "Upload and Start Logging", "Use the Arduino IDE to compile and upload the main program to the Feather M0.")
story += [P("Arduino IDE setup", "H2X")]
ide = [
    ("Board package", "Install Adafruit SAMD Boards in Boards Manager."),
    ("Board", "Select Adafruit Feather M0."),
    ("Library", "Install RTClib by Adafruit. SPI, SD, and Wire are standard Arduino libraries."),
    ("Serial Monitor", "115200 baud."),
]
story += [table(["Item", "Required setting"], ide, [48*mm, 118*mm]), Spacer(1, 8)]
story += [P("Upload steps", "H2X")]
steps = [
    ("1", "Connect the Feather M0 to the computer by USB."),
    ("2", "Open Code/FlowMeterMain/FlowMeterMain.ino in Arduino IDE."),
    ("3", "Select Adafruit Feather M0 and the correct COM port."),
    ("4", "Check the settings on the previous page, then click Upload."),
    ("5", "Open Serial Monitor at 115200 baud."),
    ("6", "Confirm that the RTC is found, the SD card initializes, and the message Logger ready appears."),
]
story += [table(["Step", "Action"], steps, [18*mm, 148*mm]), Spacer(1, 8)]
story += [P("Expected startup messages", "H2X"), P("Starting YF-DN80 + DS3231 + SD logger...<br/>RTC startup time: YYYY-MM-DD HH:MM:SS<br/>Initializing SD card...<br/>SD card initialized.<br/>Logger ready. Writing to: /YYYYMMDD/HHMMSS.CSV", "CodeX")]
story += [note("If upload fails", "Recheck the selected board and COM port. On some Feather M0 boards, double-pressing Reset starts the bootloader and creates a temporary upload port.", "info"), Spacer(1, 6)]
story += [note("Before normal logging", "Insert the SD card before powering the logger. If the RTC or SD card cannot initialize, the program stops and does not create data rows.", "warn"), PageBreak()]

# SD card
story += title("04 / SD CARD", "Writing and Reading Data", "The logger creates one new CSV file every time it powers on. It writes and closes the file after each sample.")
story += [P("Card preparation", "H2X")]
for text in [
    "Use a microSD card formatted as FAT16 or FAT32.",
    "Insert the card before the Feather M0 starts.",
    "Do not remove the card while the board is powered and logging.",
]: story.append(bullet(text))
story += [Spacer(1, 5), P("File location", "H2X"), P("/YYYYMMDD/HHMMSS.CSV<br/>Example: /20260722/143015.CSV", "CodeX")]
story += [P("CSV columns", "H2X")]
columns = [
    ("timestamp", "Date and time from the DS3231 RTC."),
    ("session_elapsed_seconds", "Seconds since the board restarted."),
    ("sample_number", "Row number for the current power-on session."),
    ("pulses", "Raw flow-sensor pulse count during the sample interval."),
    ("frequency_hz", "Pulse frequency."),
    ("flow_rate_l_min", "Calculated flow in liters per minute."),
    ("total_volume_l", "Accumulated volume for the current power-on session."),
]
story += [table(["Column", "Meaning"], columns, [62*mm, 104*mm]), Spacer(1, 7)]
story += [P("How to read the card", "H2X")]
read_steps = [
    ("1", "Stop the water flow and turn off power to the logger."),
    ("2", "Remove the microSD card and insert it into a computer."),
    ("3", "Open the folder named with the date, then open the CSV file named with the start time."),
    ("4", "Open the CSV in Excel, Google Sheets, or a text editor. Keep a copy of the original file."),
]
story += [table(["Step", "Action"], read_steps, [18*mm, 148*mm]), Spacer(1, 7)]
story += [note("Important", "total_volume_l resets to zero whenever the MCU restarts. It is a session total, not a permanent lifetime total.", "warn"), PageBreak()]

# Quick troubleshooting / handoff
story += title("05 / QUICK REFERENCE", "Basic Troubleshooting", "Start with the first error printed in Serial Monitor.")
trouble = [
    ("No pulses / zero flow", "Check water flow, common ground, level shifter, and the D11 signal wire."),
    ("Small flow when water is off", "Check electrical noise and grounding first. If needed, increase MIN_VALID_FLOW_L_MIN slightly."),
    ("Flow is consistently high or low", "Verify K_FACTOR_HZ_PER_L_MIN. Do not change K and CALIBRATION_SCALE at the same time."),
    ("RTC not found", "Check 3V, GND, SDA, and SCL wiring."),
    ("Wrong date or time", "Use the one-time FORCE_SET_RTC_TO_COMPILE_TIME procedure, then return it to false."),
    ("SD initialization failed", "Check that the card is inserted, FAT16/FAT32 formatted, and using CS D4."),
    ("CSV file is missing", "Check the RTC date folder, Serial errors, card format, and available space."),
]
story += [table(["Problem", "What to check"], trouble, [63*mm, 103*mm]), Spacer(1, 8)]
story += [P("Final handoff checklist", "H2X")]
checks = [
    "The installed board and SD configuration are identified.",
    "The sensor pulse reaches D11 through a 3.3 V level shifter.",
    "RTC time is correct and FORCE_SET_RTC_TO_COMPILE_TIME is false.",
    "The correct K factor and 10-second logging interval are confirmed.",
    "A CSV file has been created and opened successfully on a computer.",
]
for item in checks: story.append(P(f"[ ] {item}"))
story += [Spacer(1, 9), note("Main source file", "Code/FlowMeterMain/FlowMeterMain.ino", "info")]

doc.build(story)
print(OUT)

