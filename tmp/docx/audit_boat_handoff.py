from pathlib import Path
from docx import Document

p = Path(r"D:\VIMS\FlowMeter\output\docx\VIMS_Internship_Handoff_02_Autonomous_Boat.docx")
d = Document(p)
text = "\n".join(x.text for x in d.paragraphs)
text += "\n" + "\n".join(c.text for t in d.tables for row in t.rows for c in row.cells)
page_breaks = sum(x._p.xml.count('w:type="page"') for x in d.paragraphs)
s = d.sections[0]

print("file_bytes=", p.stat().st_size)
print("paragraphs=", len(d.paragraphs), "tables=", len(d.tables))
print("manual_page_breaks=", page_breaks, "target_pages=", page_breaks + 1)
print("table_shapes=", [(len(t.rows), len(t.columns)) for t in d.tables])
print("empty_cells=", sum(1 for t in d.tables for row in t.rows for c in row.cells if not c.text.strip()))
print("page_size=", round(s.page_width.inches, 2), "x", round(s.page_height.inches, 2))
print("has_final_hardware=", all(x in text for x in ["Pixhawk 4", "T500", "SBUS"]))
print("has_simple_grid=", "Auto WP -> Simple Grid" in text)
print("has_write_read=", all(x in text for x in ["Write WPs", "Read WPs"]))
print("has_rc_modes=", all(x in text for x in ["ARM", "DISARM", "AUTO", "HOLD", "MANUAL"]))
print("mentions_old_t200=", "T200" in text)
print("mentions_ppm=", "PPM" in text)
print("mentions_unconfirmed_gains=", any(x in text for x in ["PSC_VEL", "PSC_POS", "TURN_RADIUS"]))
