from pathlib import Path
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "docx" / "VIMS_Internship_Handoff_02_Autonomous_Boat.docx"

BLACK = "000000"
GRAY = "555555"
LIGHT_GRAY = "F2F4F7"
BORDER = "B7B7B7"
TABLE_INDENT_DXA = 120


def set_run_font(run, size=10.5, bold=False, color=BLACK, italic=False):
    run.font.name = "Arial"
    rpr = run._element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:ascii"), "Arial")
    rpr.rFonts.set(qn("w:hAnsi"), "Arial")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def set_cell_margins(cell, top=70, start=110, bottom=70, end=110):
    tcPr = cell._tc.get_or_add_tcPr()
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


def set_repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    marker = OxmlElement("w:tblHeader")
    marker.set(qn("w:val"), "true")
    trPr.append(marker)


def add_table(doc, headers, rows, widths_dxa):
    table = doc.add_table(rows=1, cols=len(headers))
    set_repeat_header(table.rows[0])
    for i, text in enumerate(headers):
        cell = table.rows[0].cells[i]
        set_cell_shading(cell, LIGHT_GRAY)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(text)
        set_run_font(r, size=9.5, bold=True)
    for values in rows:
        cells = table.add_row().cells
        for i, text in enumerate(values):
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(str(text))
            set_run_font(r, size=9.2)
    set_table_geometry(table, widths_dxa)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(1)
    return table


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.add_run(text)
    return p


def add_numbered(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.left_indent = Inches(0.42)
    p.paragraph_format.first_line_indent = Inches(-0.22)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(text)
    set_run_font(r, size=10.2)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.42)
    p.paragraph_format.first_line_indent = Inches(-0.22)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(text)
    set_run_font(r, size=10.2)
    return p


def add_bold_lead(doc, lead, text):
    p = doc.add_paragraph()
    r = p.add_run(lead)
    set_run_font(r, bold=True)
    r = p.add_run(text)
    set_run_font(r)
    return p


def page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = Inches(0.72)
section.bottom_margin = Inches(0.72)
section.left_margin = Inches(0.8)
section.right_margin = Inches(0.8)
section.header_distance = Inches(0.4)
section.footer_distance = Inches(0.4)

# Plain text-and-table style matching the approved FlowMeter handoff.
normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
normal.font.size = Pt(10.5)
normal.font.color.rgb = RGBColor(0, 0, 0)
normal.paragraph_format.space_before = Pt(0)
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.05

for style_name, size, before, after in (
    ("Heading 1", 15, 11, 6),
    ("Heading 2", 12, 8, 4),
    ("Heading 3", 11, 6, 3),
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

# PAGE 1
title = doc.add_paragraph()
title.paragraph_format.space_after = Pt(3)
r = title.add_run("VIMS Internship Handoff - Autonomous Boat")
set_run_font(r, size=19, bold=True)

subtitle = doc.add_paragraph()
subtitle.paragraph_format.space_after = Pt(9)
r = subtitle.add_run("Mission Planner operation and RC controller guide")
set_run_font(r, size=10.2, color=GRAY)

doc.add_paragraph(
    "This guide covers the final operating configuration and the normal workflow for creating and running an autonomous survey mission. It intentionally leaves out most of the development history and tuning process."
)

add_heading(doc, "1. Final System Overview", 1)
overview_rows = [
    ("Autopilot", "Pixhawk 4 running ArduPilot Rover/Boat firmware."),
    ("Propulsion", "Two Blue Robotics T500 thrusters with differential thrust; there is no conventional rudder."),
    ("Motor outputs", "Reported mapping: MAIN OUT 1 to the left ESC and MAIN OUT 3 to the right ESC. Confirm before the first run."),
    ("RC control", "RC receiver connected to Pixhawk RC input using SBUS."),
    ("Navigation", "GPS and compass provide position and heading for Auto mode."),
    ("Ground station", "Mission Planner connects through the telemetry radio for planning and monitoring."),
]
add_table(doc, ["Item", "Final configuration"], overview_rows, [2200, 7600])

add_heading(doc, "2. RC Controller Switches", 1)
doc.add_paragraph(
    "The controller has two three-position switches. In this document, forward means away from the operator and backward means toward the operator. Always confirm the mode shown in the Mission Planner HUD after moving a switch."
)
switch_rows = [
    ("Front switch - farther from operator", "Forward", "ARM", "Enables propulsion after all arming checks pass."),
    ("Front switch - farther from operator", "Middle", "Neutral", "No new arm/disarm command; use as a neutral position."),
    ("Front switch - farther from operator", "Backward", "DISARM", "Disables propulsion. Use after the boat has stopped."),
    ("Rear switch - closer to operator", "Forward", "AUTO", "Runs the mission stored in the Pixhawk."),
    ("Rear switch - closer to operator", "Middle", "HOLD", "Stops commanded propulsion. The boat can still drift with wind or current."),
    ("Rear switch - closer to operator", "Backward", "MANUAL", "Steering and throttle are controlled directly by the RC sticks."),
]
add_table(doc, ["Switch", "Position", "Function", "Meaning"], switch_rows, [2800, 1300, 1500, 4200])

add_bold_lead(doc, "Recommended idle position: ", "rear switch in HOLD, front switch in DISARM, and throttle centered.")
add_bold_lead(doc, "Important: ", "HOLD stops the thrusters but does not actively keep the boat at one GPS position. The vessel may drift.")

page_break(doc)

# PAGE 2
add_heading(doc, "3. Create a Simple Grid Mission in Mission Planner", 1)
doc.add_paragraph(
    "Use a small rectangle in open water for the first mission. Keep the rectangle away from shore, docks, shallow water, and obstacles. The boat should remain disarmed while the plan is created and uploaded."
)

mission_steps = [
    "Turn on the RC transmitter, power the boat, and connect the telemetry radio to the computer.",
    "Open Mission Planner. Select the correct telemetry COM port and baud rate, then click Connect.",
    "Wait for a valid GPS position and confirm that the boat location and heading look correct on the map.",
    "Open the PLAN tab. Make sure the planning layer is set to MISSION, not FENCES or RALLY.",
    "Move the map to the survey area and zoom in far enough to place the boundary accurately.",
    "Right-click the map and choose Polygon -> Draw a Polygon. In some versions this is shown as Draw Polygon -> Add Polygon Point.",
    "Click the four corners of the survey area to draw a rectangle. Leave a safety buffer inside the shoreline and around obstacles.",
    "Right-click the map again and choose Auto WP -> Simple Grid.",
    "Set the grid angle so the long survey lines follow the preferred direction of travel. Set line spacing for the required survey coverage.",
    "If the Simple Grid window shows aircraft or altitude fields, they are not important for the surface boat. Focus on the waypoint path, angle, and line spacing.",
    "Click Accept. Mission Planner will create a back-and-forth set of waypoints inside the rectangle.",
    "Review every waypoint. Confirm that the first path is safe from the launch point, all turns stay in open water, and no waypoint is on land.",
    "Click Write WPs to upload the mission to the Pixhawk. Drawing the route on the map alone does not store it in the boat.",
    "Click Read WPs and confirm that the same mission is read back from the Pixhawk. Optionally save a local waypoint file as a backup.",
]
for step in mission_steps:
    add_numbered(doc, step)

add_heading(doc, "Simple Grid Settings", 2)
grid_rows = [
    ("Angle", "Direction of the parallel survey lines. Choose a direction that reduces difficult turns and keeps the boat in open water."),
    ("Line spacing", "Distance between adjacent survey lines. Do not make the spacing so tight that the boat must make continuous sharp corrections."),
    ("Start point", "Review the first waypoint and the path from the launch area. Change the plan if the boat would cross shore or an obstacle."),
    ("End point", "The boat will not automatically return to launch unless the mission includes an RTL or return path. Confirm the desired final behavior."),
]
add_table(doc, ["Item", "Guidance"], grid_rows, [2200, 7600])

page_break(doc)

# PAGE 3
add_heading(doc, "4. Run the Mission", 1)
run_steps = [
    "Place the boat at the intended launch and home location. The Rover home position is normally set where the vehicle is armed.",
    "Confirm the mission with Read WPs, then return to the DATA screen and verify GPS, heading, battery status, and telemetry.",
    "Set the rear switch to HOLD and keep the front switch in DISARM. Center the throttle and steering controls.",
    "When the area is clear and all status messages are normal, move the front switch forward to ARM. Confirm ARMED in Mission Planner.",
    "Move the rear switch forward to AUTO. Confirm AUTO in the Mission Planner HUD. The boat should begin following the uploaded waypoints.",
    "Monitor the map, cross-track behavior, battery, RC link, telemetry, and nearby traffic throughout the mission.",
    "At the end of the mission, move the rear switch to HOLD. After the boat has stopped, move the front switch backward to DISARM.",
]
for step in run_steps:
    add_numbered(doc, step)

add_heading(doc, "5. Takeover and Recovery", 1)
takeover_rows = [
    ("Pause immediately", "Move the rear switch to the middle HOLD position. The thrusters stop, but the boat may drift."),
    ("Take direct control", "Move the rear switch backward to MANUAL and use the steering and throttle sticks."),
    ("Disarm", "Use HOLD first, wait for the propellers to stop, then move the front switch backward to DISARM."),
    ("Mission interrupted", "Before returning to AUTO, check the active waypoint in Mission Planner. The mission may resume from its current mission position."),
    ("Telemetry lost", "Use the RC controller for MANUAL or HOLD recovery. Mission Planner cannot command the boat without telemetry."),
]
add_table(doc, ["Situation", "Action"], takeover_rows, [2600, 7200])

add_heading(doc, "6. Quick Troubleshooting", 1)
trouble_rows = [
    ("Cannot arm", "Set HOLD, center throttle, and read the red pre-arm message in Mission Planner. Check GPS, compass, safety state, and RC input."),
    ("AUTO is rejected", "Confirm the vehicle is armed, GPS/navigation is healthy, and the mission was uploaded with Write WPs."),
    ("Boat does not follow the planned route", "Move to HOLD or MANUAL. Verify Read WPs, heading direction, left/right motor response, and waypoint locations before retrying."),
    ("Strong left-right oscillation", "Abort to HOLD or MANUAL. Retry with a smaller mission, lower speed, wider waypoint spacing, and more open turns before changing controller parameters."),
    ("No RC response", "Check receiver power, SBUS connection to RC input, transmitter link, and Mission Planner Radio Calibration."),
]
add_table(doc, ["Problem", "First action"], trouble_rows, [2900, 6900])

add_bold_lead(doc, "Final reminder: ", "Always verify the actual mode and armed state in Mission Planner. Do not rely only on the physical switch position.")

refs = doc.add_paragraph()
refs.paragraph_format.space_before = Pt(5)
r = refs.add_run("Official reference: ")
set_run_font(r, size=9, bold=True, color=GRAY)
r = refs.add_run("https://ardupilot.org/planner/docs/mission-planner-flight-plan.html")
set_run_font(r, size=9, color=GRAY)

doc.core_properties.title = "VIMS Internship Handoff - Autonomous Boat"
doc.core_properties.subject = "Pixhawk 4, SBUS RC, Mission Planner Simple Grid, and autonomous mission operation"
doc.core_properties.author = "VIMS"
doc.core_properties.keywords = "autonomous boat, Pixhawk 4, T500, SBUS, Mission Planner, Simple Grid"
doc.save(OUT)
print(OUT)
