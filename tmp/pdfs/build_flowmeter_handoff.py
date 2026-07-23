from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Flowable, HRFlowable
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "VIMS_Internship_Handoff_01_FlowMeter.pdf"

NAVY = HexColor("#123044")
TEAL = HexColor("#0B7A75")
TEAL_DARK = HexColor("#075E5A")
MINT = HexColor("#E8F4F2")
SKY = HexColor("#EAF2F8")
AMBER = HexColor("#D98E04")
AMBER_BG = HexColor("#FFF5DA")
RED = HexColor("#A93A3A")
RED_BG = HexColor("#FCECEC")
INK = HexColor("#24323D")
MUTED = HexColor("#5D6B75")
LINE = HexColor("#C7D3D8")
LIGHT = HexColor("#F5F7F8")
WHITE = colors.white

FONT_PATH = Path(r"C:\Windows\Fonts\NotoSansTC-VF.ttf")
MONO_PATH = Path(r"C:\Windows\Fonts\consola.ttf")
pdfmetrics.registerFont(TTFont("NotoTC", str(FONT_PATH)))
pdfmetrics.registerFont(TTFont("NotoTCBold", str(FONT_PATH)))
pdfmetrics.registerFont(TTFont("Consolas", str(MONO_PATH)))

PAGE_W, PAGE_H = A4
MARGIN_X = 18 * mm
TOP = 18 * mm
BOTTOM = 17 * mm

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="BodyTC", fontName="NotoTC", fontSize=9.2, leading=14,
    textColor=INK, spaceAfter=5
))
styles.add(ParagraphStyle(
    name="SmallTC", parent=styles["BodyTC"], fontSize=7.8, leading=11.3,
    textColor=MUTED, spaceAfter=3
))
styles.add(ParagraphStyle(
    name="TinyTC", parent=styles["SmallTC"], fontSize=6.9, leading=9.5
))
styles.add(ParagraphStyle(
    name="H1TC", fontName="NotoTCBold", fontSize=22, leading=28,
    textColor=NAVY, spaceAfter=9
))
styles.add(ParagraphStyle(
    name="H2TC", fontName="NotoTCBold", fontSize=14, leading=19,
    textColor=TEAL_DARK, spaceBefore=4, spaceAfter=7
))
styles.add(ParagraphStyle(
    name="H3TC", fontName="NotoTCBold", fontSize=10.5, leading=15,
    textColor=NAVY, spaceBefore=4, spaceAfter=4
))
styles.add(ParagraphStyle(
    name="CoverTitle", fontName="NotoTCBold", fontSize=29, leading=36,
    textColor=WHITE, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    name="CoverSub", fontName="NotoTC", fontSize=12, leading=18,
    textColor=HexColor("#D8EBEC")
))
styles.add(ParagraphStyle(
    name="TableHead", fontName="NotoTCBold", fontSize=7.8, leading=10.5,
    textColor=WHITE, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    name="TableCell", fontName="NotoTC", fontSize=7.4, leading=10.4,
    textColor=INK
))
styles.add(ParagraphStyle(
    name="TableCellSmall", fontName="NotoTC", fontSize=6.7, leading=9.2,
    textColor=INK
))
styles.add(ParagraphStyle(
    name="CodeTC", fontName="Consolas", fontSize=7.1, leading=10,
    textColor=HexColor("#16313E"), backColor=HexColor("#EDF2F4"),
    borderColor=LINE, borderWidth=0.5, borderPadding=6, spaceAfter=6
))
styles.add(ParagraphStyle(
    name="BulletTC", parent=styles["BodyTC"], leftIndent=13, firstLineIndent=-8,
    bulletIndent=2, spaceAfter=2
))
styles.add(ParagraphStyle(
    name="StepNum", fontName="NotoTCBold", fontSize=14, leading=17,
    textColor=WHITE, alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    name="TOC", parent=styles["BodyTC"], fontSize=9.4, leading=14.5,
    textColor=NAVY
))


def P(text, style="BodyTC"):
    return Paragraph(text, styles[style])


def bullet(text, color=TEAL):
    return Paragraph(f'<font color="{color.hexval()}">&#8226;</font> {text}', styles["BulletTC"])


def section_title(kicker, title, subtitle=None):
    items = [
        P(kicker.upper(), "SmallTC"),
        P(title, "H1TC"),
        HRFlowable(width="100%", thickness=1.2, color=TEAL, spaceAfter=8),
    ]
    if subtitle:
        items.append(P(subtitle, "BodyTC"))
    return items


def callout(title, body, kind="info"):
    palette = {
        "info": (TEAL, MINT),
        "warn": (AMBER, AMBER_BG),
        "danger": (RED, RED_BG),
        "neutral": (NAVY, SKY),
    }
    accent, bg = palette[kind]
    data = [[
        Paragraph("!" if kind in ("warn", "danger") else "i", ParagraphStyle(
            name=f"Icon{kind}", fontName="NotoTCBold", fontSize=14,
            textColor=WHITE, alignment=TA_CENTER, leading=16
        )),
        P(f"<b>{title}</b><br/>{body}", "SmallTC")
    ]]
    t = Table(data, colWidths=[10*mm, 156*mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), accent),
        ("BACKGROUND", (1,0), (1,0), bg),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOX", (0,0), (-1,-1), 0.6, accent),
        ("LEFTPADDING", (1,0), (1,0), 7),
        ("RIGHTPADDING", (1,0), (1,0), 7),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return t


def table(headers, rows, widths, small=False, repeat=1):
    cell_style = "TableCellSmall" if small else "TableCell"
    data = [[P(h, "TableHead") for h in headers]]
    for row in rows:
        data.append([P(str(x), cell_style) for x in row])
    t = Table(data, colWidths=widths, repeatRows=repeat, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.35, LINE),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]
    for i in range(1, len(data)):
        commands.append(("BACKGROUND", (0,i), (-1,i), WHITE if i % 2 else LIGHT))
    t.setStyle(TableStyle(commands))
    return t


class ArchitectureDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 166*mm
        self.height = 68*mm

    def draw_box(self, c, x, y, w, h, title, lines, fill, stroke=TEAL):
        c.setFillColor(fill)
        c.setStrokeColor(stroke)
        c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
        c.setFont("NotoTCBold", 8.5)
        c.setFillColor(NAVY)
        c.drawCentredString(x+w/2, y+h-12, title)
        c.setFont("NotoTC", 6.8)
        c.setFillColor(INK)
        yy = y+h-24
        for line in lines:
            c.drawCentredString(x+w/2, yy, line)
            yy -= 9

    def arrow(self, c, x1, y1, x2, y2, label=""):
        c.setStrokeColor(TEAL_DARK)
        c.setFillColor(TEAL_DARK)
        c.setLineWidth(1.2)
        c.line(x1, y1, x2, y2)
        ang = 4
        c.line(x2, y2, x2-ang, y2+ang/2)
        c.line(x2, y2, x2-ang, y2-ang/2)
        if label:
            c.setFont("NotoTC", 6.3)
            c.setFillColor(MUTED)
            c.drawCentredString((x1+x2)/2, y1+5, label)

    def draw(self):
        c = self.canv
        self.draw_box(c, 0, 37*mm, 43*mm, 25*mm, "YF-DN80", ["水流 -> Hall pulse", "黃色訊號線"], AMBER_BG, AMBER)
        self.draw_box(c, 60*mm, 31*mm, 48*mm, 35*mm, "Adafruit Feather M0", ["D11 pulse interrupt", "I2C RTC / SPI SD", "流量計算與 CSV"], MINT)
        self.draw_box(c, 125*mm, 43*mm, 41*mm, 21*mm, "microSD", ["日期資料夾", "每次上電一個 CSV"], SKY, NAVY)
        self.draw_box(c, 125*mm, 8*mm, 41*mm, 22*mm, "DS3231 RTC", ["時間戳記", "備援電池續時"], SKY, NAVY)
        self.draw_box(c, 0, 3*mm, 43*mm, 23*mm, "外部電源 / 轉位準", ["感測器依銘牌供電", "Pulse 轉為 3.3 V logic"], RED_BG, RED)
        self.arrow(c, 43*mm, 49*mm, 60*mm, 49*mm, "level-shifted pulse")
        self.arrow(c, 108*mm, 49*mm, 125*mm, 49*mm, "SPI / CS D4")
        self.arrow(c, 108*mm, 25*mm, 125*mm, 19*mm, "I2C")
        self.arrow(c, 43*mm, 15*mm, 60*mm, 39*mm, "power + common GND")


class PlacementDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 166*mm
        self.height = 74*mm

    def draw(self):
        c = self.canv
        # pipe and sensor
        c.setStrokeColor(HexColor("#718A96")); c.setLineWidth(10)
        c.line(4*mm, 43*mm, 162*mm, 43*mm)
        c.setFillColor(AMBER); c.setStrokeColor(AMBER)
        c.roundRect(63*mm, 32*mm, 40*mm, 22*mm, 4, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont("NotoTCBold", 9)
        c.drawCentredString(83*mm, 43*mm, "YF-DN80")
        c.setFillColor(TEAL_DARK); c.setStrokeColor(TEAL_DARK); c.setLineWidth(2)
        c.line(109*mm, 43*mm, 126*mm, 43*mm)
        c.line(126*mm, 43*mm, 120*mm, 47*mm); c.line(126*mm, 43*mm, 120*mm, 39*mm)
        c.setFont("NotoTC", 7); c.drawString(108*mm, 49*mm, "依外殼箭頭")
        # enclosure
        c.setFillColor(MINT); c.setStrokeColor(TEAL); c.setLineWidth(1)
        c.roundRect(55*mm, 58*mm, 56*mm, 14*mm, 4, fill=1, stroke=1)
        c.setFillColor(NAVY); c.setFont("NotoTCBold", 8)
        c.drawCentredString(83*mm, 65*mm, "防濺電子盒：MCU / RTC / SD")
        c.setStrokeColor(TEAL_DARK); c.setLineWidth(1)
        c.line(83*mm, 58*mm, 83*mm, 54*mm)
        # labels
        labels = [
            (4*mm, 21*mm, 48*mm, "管路", "先洩壓再施工；接頭止漏後做靜態與流動測漏"),
            (59*mm, 5*mm, 48*mm, "電子盒", "高於可能積水處；USB、SD 可維修；線材加固定與拉力緩解"),
            (114*mm, 21*mm, 48*mm, "訊號線", "遠離馬達與高電流線；與 MCU 共地；進盒前做滴水彎"),
        ]
        for x, y, w, title, text in labels:
            c.setFillColor(LIGHT); c.setStrokeColor(LINE)
            c.roundRect(x, y, w, 16*mm, 3, fill=1, stroke=1)
            c.setFillColor(NAVY); c.setFont("NotoTCBold", 7.3); c.drawString(x+3*mm, y+11*mm, title)
            c.setFillColor(MUTED); c.setFont("NotoTC", 5.8)
            words = [text[i:i+18] for i in range(0, len(text), 18)]
            yy = y+7*mm
            for ln in words[:2]:
                c.drawString(x+3*mm, yy, ln); yy -= 3.2*mm


def footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(LINE)
        canvas.line(MARGIN_X, 13*mm, PAGE_W-MARGIN_X, 13*mm)
        canvas.setFont("NotoTC", 6.8)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN_X, 8.5*mm, "VIMS Internship Handoff | 01 FlowMeter")
        canvas.drawRightString(PAGE_W-MARGIN_X, 8.5*mm, f"{doc.page:02d}")
    canvas.restoreState()


class HandoffDoc(BaseDocTemplate):
    pass


doc = HandoffDoc(
    str(OUT), pagesize=A4,
    leftMargin=MARGIN_X, rightMargin=MARGIN_X,
    topMargin=TOP, bottomMargin=BOTTOM,
    title="VIMS Internship 工作交接文件 - FlowMeter",
    author="VIMS internship handoff",
    subject="FlowMeter hardware, firmware, calibration, operation, and troubleshooting handoff"
)
frame = Frame(MARGIN_X, BOTTOM, PAGE_W-2*MARGIN_X, PAGE_H-TOP-BOTTOM, id="normal")
doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])

story = []

# Cover
cover = Table([[P("VIMS", "CoverSub")]], colWidths=[166*mm], rowHeights=[12*mm])
cover.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), TEAL),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
]))
story += [Spacer(1, 16*mm), cover, Spacer(1, 4*mm)]
title_box = Table([[
    P("Internship<br/>工作交接文件", "CoverTitle")
]], colWidths=[166*mm], rowHeights=[56*mm])
title_box.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), NAVY),
    ("LEFTPADDING", (0,0), (-1,-1), 10*mm),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
]))
story += [title_box, Spacer(1, 4*mm)]
project_box = Table([[P("01", "StepNum"), P("FLOWMETER", "H1TC")],
                     ["", P("YF-DN80 水流量記錄器<br/><font size='10' color='#5D6B75'>硬體安裝、接線、韌體、校正、操作與除錯</font>", "H2TC")]],
                    colWidths=[18*mm, 148*mm])
project_box.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (0,0), AMBER),
    ("SPAN", (0,0), (0,1)),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("BOX", (0,0), (-1,-1), 0.8, LINE),
    ("LEFTPADDING", (1,0), (1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
]))
story += [project_box, Spacer(1, 18*mm)]
meta = table(["文件角色", "版本基準", "狀態"], [[
    "三份交接文件中的第 1 份",
    "工作區內容截至 2026-07-22",
    "可供接手與現場驗證"
]], [50*mm, 62*mm, 54*mm])
story += [meta, Spacer(1, 7*mm), P("文件原則：以現行原始碼為主要依據；無現場照片或料號可證實的接法，均標示為「需現場確認」。", "SmallTC"), PageBreak()]

# Document control / TOC
story += section_title("DOCUMENT CONTROL", "如何使用這份交接文件", "接手者可先走完「15 分鐘快速檢查」，再依需求查閱接線、校正、資料格式與除錯章節。")
story += [callout("最重要的版本事實", "現行主程式位於 <b>Code/FlowMeterMain/FlowMeterMain.ino</b>；它尚未是 Git HEAD 中的追蹤版本。Git 內原本的 <b>FlowMeterFirst</b> 已在工作區刪除，README 尚未完全同步。交接前應先整理並提交版本。", "warn"), Spacer(1, 7)]
toc_rows = [
    ("01", "系統概覽與資料流", "3"),
    ("02", "硬體配置與 MCU 放置", "4"),
    ("03", "完整接線表與電氣注意事項", "5"),
    ("04", "開發環境、燒錄與程式架構", "6"),
    ("05", "可修改的控制參數", "7"),
    ("06", "校正 SOP", "8"),
    ("07", "日常操作與 CSV 資料", "9"),
    ("08", "分階段測試與驗收", "10"),
    ("09", "故障排除", "11"),
    ("10", "已知問題、優先工作與交接清單", "12-13"),
]
story += [table(["章", "內容", "頁"], toc_rows, [18*mm, 128*mm, 20*mm]), Spacer(1, 8)]
story += [P("15 分鐘快速檢查", "H2TC")]
quick = [
    ("1", "確認板型與 SD", "若是 Feather M0 Adalogger，microSD 為板載且 CS=D4；若是外接模組，依第 5 頁接 SPI。"),
    ("2", "確認供電與共地", "感測器電源依實體銘牌；MCU 為 3.3 V logic。黃色 pulse 必須先轉為 3.3 V，所有 GND 共接。"),
    ("3", "先跑元件測試", "用 Serial Monitor 115200 baud，確認 D11 有 pulse，再測 RTC 與 SD。"),
    ("4", "校正後更新 K", "用多次量桶法取得 combined K，寫入主程式，CALIBRATION_SCALE 維持 1.0。"),
    ("5", "跑主程式驗證 CSV", "確認時間、資料夾/檔名、流量與累積量合理，安全斷電後讀卡。"),
]
story += [table(["步驟", "檢查點", "通過條件"], quick, [15*mm, 43*mm, 108*mm], small=True), PageBreak()]

# Overview
story += section_title("01 / SYSTEM OVERVIEW", "系統概覽與資料流", "目的：把 YF-DN80 的 pulse 訊號換算為瞬時流量與本次開機累積體積，配上 RTC 時間後持續寫入 microSD CSV。")
story += [ArchitectureDiagram(), Spacer(1, 4)]
story += [P("核心組成", "H2TC")]
components = [
    ("MCU", "Adafruit Feather M0", "3.3 V logic；D11 計數 pulse；I2C 讀 RTC；SPI 寫 SD。"),
    ("流量感測", "YF-DN80", "Hall-effect pulse 輸出；專案採 F(Hz)=K×Q(L/min)。原始 datasheet 預設 K=0.5。"),
    ("時間", "DS3231 RTC", "提供 CSV timestamp；備援電池在主電源關閉時續時。"),
    ("儲存", "microSD", "FAT16/FAT32；每次上電建立一個 session CSV，逐列開檔、寫入、關檔。"),
    ("電平介面", "Level shifter", "將感測器 pulse 降到 Feather M0 可接受的 3.3 V logic。"),
]
story += [table(["功能", "元件", "專案用途"], components, [27*mm, 44*mm, 95*mm])]
story += [Spacer(1, 7), P("計算鏈", "H2TC"), P("<b>pulses / elapsed seconds = frequency (Hz)</b><br/><b>flow (L/min) = frequency / K</b><br/><b>sample volume (L) = flow × elapsed seconds / 60</b><br/><b>total volume = 累加每個 sample volume</b>", "CodeTC")]
story += [callout("目前主程式的 K 不是 datasheet 預設值", "FlowMeterMain 目前為 <b>K_FACTOR_HZ_PER_L_MIN = 0.45</b>；舊版與校正工具的 CURRENT_K_FACTOR 仍是 0.5。0.45 是否為實測校正值，需由原作者或校正紀錄確認。", "warn"), PageBreak()]

# Placement
story += section_title("02 / PHYSICAL INSTALLATION", "硬體配置與 MCU 放置", "此頁把水路元件與低壓電子元件分開處理。現場沒有照片或機構圖，因此尺寸、支架與盒體開孔需依實物確認。")
story += [PlacementDiagram(), Spacer(1, 5)]
story += [P("建議配置", "H2TC")]
placement_rows = [
    ("YF-DN80", "安裝在可洩壓、可隔離、可拆卸的管段；外殼箭頭與水流方向一致。", "鎖接前確認 G3 / DN80 接口與轉接件；通水後檢漏。"),
    ("MCU / RTC / SD", "放入防濺電子盒，位置高於可能積水處，遠離冷凝與直接噴水。", "保留 USB、reset 與 SD 卡的維修空間；不要讓板底接觸金屬。"),
    ("Level shifter", "與 MCU 同盒、靠近 MCU 端，縮短 3.3 V 訊號段。", "高壓側/低壓側方向依模組標示，不可顛倒。"),
    ("線材", "感測器線與馬達、泵浦 AC 或高電流 DC 線分開走線。", "進盒前做滴水彎，並使用 cable gland / strain relief。"),
    ("RTC 電池", "電池座可維修且不會被板件擠壓。", "更換後檢查 lostPower，重新設定並核對時間。"),
]
story += [table(["部位", "放置方式", "施工 / 維修重點"], placement_rows, [31*mm, 68*mm, 67*mm], small=True)]
story += [Spacer(1, 6), callout("施工安全", "任何管路安裝、拆卸或調整前先停泵、隔離並洩壓。電子盒上電前先量測感測器電源與 level shifter 輸出，確認 D11 端不超過 3.3 V。", "danger"), PageBreak()]

# Wiring
story += section_title("03 / WIRING", "完整接線表與電氣注意事項", "表內「確定」來自現行程式或官方 Feather pinout；「需確認」代表專案沒有保存實物照片或模組精確料號。")
wiring = [
    ("YF-DN80 黃線 Signal", "Level shifter 高壓/感測器側 input", "確定訊號用途；端子名稱需確認", "程式以 FALLING edge 計數。不可直接進 Feather。"),
    ("Level shifter 低壓側 output", "Feather D11", "確定", "FLOW_PIN=11；所有現行主要 sketch 都是 D11。"),
    ("YF-DN80 紅線 V+", "外部 DC 供電正端", "線色屬常見配置，現場確認", "製造商頁面列 3.5-24 VDC；本機應以銘牌/料號為準。"),
    ("YF-DN80 黑線 GND", "外部電源 GND + Feather GND", "線色屬常見配置，現場確認", "必須共地，否則 pulse 無共同參考。"),
    ("Level shifter LV", "Feather 3V", "依模組確認", "低壓側必須為 3.3 V logic。"),
    ("Level shifter HV", "感測器 logic 供電參考", "依模組確認", "不同類型轉位準器接法不同；依 PCB 標示。"),
    ("DS3231 VCC / GND", "Feather 3V / GND", "建議且需確認模組", "讓 I2C pull-up 位於 3.3 V；不要把 SDA/SCL 拉到 5 V。"),
    ("DS3231 SDA", "Feather SDA (GPIO 20)", "確定", "Wire.begin() 使用板上 SDA。"),
    ("DS3231 SCL", "Feather SCL (GPIO 21)", "確定", "Wire.begin() 使用板上 SCL。"),
    ("microSD CS", "Feather D4", "確定", "SD_CS_PIN=4。若為 M0 Adalogger，D4 是板載 SD CS。"),
    ("microSD SCK/MOSI/MISO", "Feather 對應硬體 SPI 腳", "外接 SD 時才需要", "依板上 SCK/MO/MI 標示，不要套用 UNO 的 11/12/13。"),
    ("microSD VCC / GND", "依模組規格 / 共地", "外接 SD 時需確認", "只用支援 3.3 V logic 的模組，或確認其內建 regulator/level shift。"),
]
story += [table(["來源", "接到", "可信度", "注意"], wiring, [39*mm, 46*mm, 33*mm, 48*mm], small=True)]
story += [Spacer(1, 6), callout("板型判斷", "CS=D4 與官方 <b>Feather M0 Adalogger</b> 的板載 microSD 配置完全一致。如果現場板子就是 Adalogger，SD 不需另拉 SPI 線，只要插入格式正確的卡；README 中的「SD card module」可能只是泛稱。", "info")]
story += [Spacer(1, 6), P("上電前萬用表檢查", "H3TC")]
for t in [
    "斷電時確認 3V 與 GND 無短路；外部 sensor V+ 與 GND 無反接。",
    "上電後量測 Feather 3V 約為 3.3 V；D11 靜態與 pulse 峰值不得超過 3.3 V。",
    "確認 MCU GND、感測器 GND、level shifter GND 導通。",
]: story.append(bullet(t))
story += [PageBreak()]

# Environment + architecture
story += section_title("04 / FIRMWARE", "開發環境、燒錄與程式架構", "程式為 Arduino sketches，目標板為 Adafruit Feather M0 (ATSAMD21, 3.3 V logic)。")
story += [P("建置環境", "H2TC")]
env = [
    ("Arduino IDE", "安裝目前可用的 2.x 版", "選擇正確 COM port。"),
    ("Board package", "Adafruit SAMD Boards", "Board 選 Adafruit Feather M0；若實物為 Feather M0 Adalogger，仍用同系列板設定。"),
    ("內建 libraries", "SPI、SD、Wire", "主程式與 SD 測試會使用。"),
    ("外部 library", "RTClib by Adafruit", "主程式與 RTCTest 會使用 DS3231。"),
    ("Serial Monitor", "115200 baud；Newline", "校正工具指令需以換行送出。"),
]
story += [table(["項目", "設定", "備註"], env, [37*mm, 69*mm, 60*mm])]
story += [Spacer(1, 7), P("燒錄順序", "H2TC")]
upload_steps = [
    ("1", "確認板型 / port", "插 USB，選 Feather M0 與正確序列埠。"),
    ("2", "單元測試", "先用 FlowMeterComponetTest、RTCTest、FlowMeterTest 排除硬體問題。"),
    ("3", "校正", "燒錄 FlowMeterCalibration，完成多次量測並抄下 combined K。"),
    ("4", "更新主程式", "把 K 寫入 FlowMeterMain；確認 sample interval、RTC flag 與 pin。"),
    ("5", "上線", "燒錄 FlowMeterMain，核對 Serial 與 SD CSV。"),
]
story += [table(["", "動作", "通過條件"], upload_steps, [13*mm, 47*mm, 106*mm], small=True)]
story += [Spacer(1, 7), P("主程式生命週期", "H2TC")]
story += [P("setup(): Serial -> D11 interrupt -> I2C/RTC -> RTC battery oscillator -> SD.begin(D4) -> 建立 session CSV -> ready<br/><br/>loop(): 等待 SAMPLE_INTERVAL_MS -> 原子性複製並清零 pulses -> 算 frequency/flow/volume -> 讀 RTC -> append CSV -> Serial 列印", "CodeTC")]
story += [callout("RTC 設定規則", "正式運行時 FORCE_SET_RTC_TO_COMPILE_TIME 必須為 false。若要強制校時：設 true、編譯上傳一次、核對時間，立刻改回 false 再上傳；否則每次重啟都可能重設時間。", "warn"), PageBreak()]

# Config variables
story += section_title("05 / CONFIGURATION", "可修改的控制參數", "修改前先保留原值與校正紀錄。下表以現行 FlowMeterMain 為準。")
params = [
    ("FLOW_PIN", "11", "Pulse interrupt 輸入", "只有實際改線才改；註解與所有測試 sketch 要同步。"),
    ("SD_CS_PIN", "4", "SD chip select", "板載 Adalogger 固定 D4；外接模組改線才更動。"),
    ("K_FACTOR_HZ_PER_L_MIN", "0.45", "F=K×Q 的核心校正值", "優先使用校正工具的 combined K。現值來源需確認。"),
    ("CALIBRATION_SCALE", "1.0", "流量乘法修正", "更新 K 後維持 1.0；避免同時用 K 與 scale 重複校正。"),
    ("FLOW_OFFSET_L_MIN", "0.0", "流量加法偏移", "非必要不改；非零會連零流量一起偏移。"),
    ("MIN_VALID_FLOW_L_MIN", "0.0", "低於門檻視為 0", "確認噪聲分布後才調高；會犧牲低流量靈敏度。"),
    ("SAMPLE_INTERVAL_MS", "10000", "記錄間隔 10 秒", "縮短會增加 SD 寫入次數；加長會降低瞬時變化解析度。"),
    ("FORCE_SET_RTC_TO_COMPILE_TIME", "false / 0", "強制以編譯時間校時", "只在維護校時時暫時 true。"),
]
story += [table(["變數", "現值", "作用", "修改原則"], params, [46*mm, 22*mm, 44*mm, 54*mm], small=True)]
story += [Spacer(1, 7), P("控制邏輯的實際順序", "H2TC"), P("flow = frequency / K<br/>flow = flow * CALIBRATION_SCALE + FLOW_OFFSET_L_MIN<br/>if flow &lt; MIN_VALID_FLOW_L_MIN: flow = 0", "CodeTC")]
story += [callout("門檻不是除噪濾波器", "MIN_VALID_FLOW_L_MIN 只是把小值直接歸零，沒有平均、去彈跳或異常值偵測。若現場訊號受泵浦或馬達干擾，應先改善接地、遮蔽、走線與電平，再決定是否加軟體濾波。", "info")]
story += [Spacer(1, 6), P("其他 sketch 可調參數", "H2TC")]
other = [
    ("FlowMeterCalibration", "MAX_TRIALS=20；CURRENT_K_FACTOR=0.5；LIVE_PRINT_INTERVAL_MS=1000", "若主程式 K 已改，CURRENT_K_FACTOR 也應同步，否則輸出的 suggested scale 僅供比較且會失真。"),
    ("FlowMeterComponetTest", "K=0.5；sample=1000 ms；threshold=0", "用於看原始 pulse/frequency；目前註解 D5 但程式 D11。"),
    ("FlowMeterTest", "sample=1000 ms；TOTAL_SAMPLES=30", "30 秒 dummy.csv 的 SD 測試。"),
]
story += [table(["程式", "參數", "交接注意"], other, [45*mm, 58*mm, 63*mm], small=True), PageBreak()]

# Calibration
story += section_title("06 / CALIBRATION", "YF-DN80 多次量測校正 SOP", "校正工具採「總 pulses / 總 liters」的加權方式，體積較大的 trial 自然權重較高。")
story += [P("準備", "H2TC")]
prep = [
    "已完成 level shifter 與 D11 pulse 測試；Serial Monitor 設 115200 baud + Newline。",
    "可安全承接的量桶/儲槽，以及可信賴的體積基準；準備至少 3-5 次、涵蓋實際使用流量的 trial。",
    "排除管線空氣、漏水與回流；每次 trial 都從穩定且一致的操作條件開始。",
]
for t in prep: story.append(bullet(t))
story += [Spacer(1, 4), P("操作指令", "H2TC")]
cal_steps = [
    ("1", "輸入 trial 數", "例如 5；允許 1-20。"),
    ("2", "輸入 s", "開始計數；Serial 每秒顯示 elapsed_s 與 pulses。"),
    ("3", "通水並量取", "讓水進入量桶；避免 trial 太短造成起停誤差占比過高。"),
    ("4", "輸入 e", "結束計數，記錄 total pulses 與 elapsed time。"),
    ("5", "輸入 v <liters>", "例如 v 18.92；工具計算該 trial 的 K。"),
    ("6", "完成全部 trial", "工具印出 combined K、各 trial 差異百分比與建議值。"),
    ("7", "更新 logger", "將 combined K 寫入 K_FACTOR_HZ_PER_L_MIN；scale=1.0。"),
]
story += [table(["步驟", "指令 / 動作", "結果"], cal_steps, [16*mm, 49*mm, 101*mm], small=True)]
story += [Spacer(1, 7), P("公式與判讀", "H2TC")]
story += [P("combined pulses per liter = Σ pulses / Σ measured liters<br/>combined K = combined pulses per liter / 60<br/>建議 logger 設定：K_FACTOR_HZ_PER_L_MIN = combined K；CALIBRATION_SCALE = 1.0", "CodeTC")]
story += [callout("何時重做", "更換感測器、改變供電/level shifter、修改 pulse edge 或 pin、管路配置大改、讀值長期偏移，或 trial 間 K 差異明顯時，都應重新校正並保存原始表格。", "info")]
story += [Spacer(1, 6), P("校正紀錄模板", "H3TC")]
record_rows = [(str(i), "", "", "", "", "") for i in range(1,6)]
story += [table(["Trial", "Pulses", "Liters", "Seconds", "K", "備註"], record_rows, [15*mm, 27*mm, 27*mm, 29*mm, 29*mm, 39*mm], small=True), PageBreak()]

# Operations + data
story += section_title("07 / OPERATIONS & DATA", "日常操作與 CSV 資料", "主程式每次上電建立新的 session 檔；累積量只代表本次開機，斷電後從 0 重新累積。")
story += [P("正常啟動", "H2TC")]
ops = [
    ("1", "插入 SD 卡、確認 RTC 電池與接線", "不要在 MCU 正寫入時拔卡。"),
    ("2", "上電並開啟 115200 Serial（可選）", "應依序看到 RTC、SD initialized 與 logger ready。"),
    ("3", "核對 startup time 與 logFilePath", "日期時間錯誤時先停用資料收集並校時。"),
    ("4", "通水觀察至少 3 個 samples", "pulses > 0、frequency/flow 合理、total volume 單調增加。"),
    ("5", "結束時先停水，再安全斷電", "因每列寫完即 close，最近成功列通常已保存。"),
    ("6", "斷電後取卡備份 CSV", "保留原檔；分析時另存副本。"),
]
story += [table(["步驟", "動作", "檢查"], ops, [16*mm, 77*mm, 73*mm], small=True)]
story += [Spacer(1, 7), P("檔案結構", "H2TC"), P("/YYYYMMDD/HHMMSS.CSV<br/>例如 /20260609/153245.CSV<br/><br/># session_start=2026-06-09 15:32:45<br/>timestamp,session_elapsed_seconds,sample_number,pulses,frequency_hz,flow_rate_l_min,total_volume_l", "CodeTC")]
csv_rows = [
    ("timestamp", "RTC 時間", "核對時區與 RTC 校時紀錄。"),
    ("session_elapsed_seconds", "自 MCU reset 後的 millis()/1000", "近似 session elapsed；包含 setup 時間。"),
    ("sample_number", "本次開機 sample 序號", "從 1 開始。"),
    ("pulses", "本 interval 的下降緣數", "原始診斷最重要欄位。"),
    ("frequency_hz", "pulses / 實際 elapsed seconds", "保留 3 位小數。"),
    ("flow_rate_l_min", "校正後瞬時流量", "K/scale/offset/threshold 都會影響。"),
    ("total_volume_l", "本次開機累積量", "保留 4 位小數；重啟即歸零。"),
]
story += [table(["欄位", "意義", "分析注意"], csv_rows, [53*mm, 56*mm, 57*mm], small=True)]
story += [Spacer(1, 6), callout("檔名碰撞", "檔名只精確到秒；如果 RTC 時間錯誤或同一秒內再次建立 session，程式會因同名檔已存在而停止。遇到此錯誤先核對 RTC，再備份/整理 SD 卡。", "warn"), PageBreak()]

# Testing
story += section_title("08 / TEST & ACCEPTANCE", "分階段測試與驗收", "不要直接以主程式一次測全部。用最小 sketch 逐段確認，可以快速定位是感測器、RTC、SD 還是整合問題。")
tests = [
    ("1", "FlowMeterComponetTest", "D11 / level shifter / pulse", "Serial 每秒出現 pulses、Hz、L/min；停水時接近 0，通水時 pulses 穩定增加。"),
    ("2", "RTCTest", "DS3231 / I2C / 時間", "每秒時間遞增；斷主電後重新上電仍保留正確時間。"),
    ("3", "FlowMeterTest", "SD 初始化與寫檔", "約 30 秒後完成；卡內 dummy.csv 有 30 筆資料與 header。"),
    ("4", "FlowMeterCalibration", "實際 K factor", "完成 3-5 次量測；trial 間差異可解釋；combined K 已記錄。"),
    ("5", "FlowMeterMain", "整機記錄", "每 10 秒一列；CSV、Serial、實測體積三者一致且時間正確。"),
]
story += [table(["階段", "Sketch", "驗證項目", "通過條件"], tests, [15*mm, 43*mm, 41*mm, 67*mm], small=True)]
story += [Spacer(1, 7), P("整機驗收紀錄", "H2TC")]
accept = [
    ("板型 / serial", "□", "Board: __________  Port: __________  Baud: 115200"),
    ("D11 電壓", "□", "Low: ____ V / High: ____ V（High 不超過 3.3 V）"),
    ("RTC", "□", "斷電 ____ 分鐘後誤差 ____ 秒；lostPower: YES / NO"),
    ("SD", "□", "格式: FAT16 / FAT32；容量: ____；dummy.csv 30 rows"),
    ("校正", "□", "Trials: ____；combined K: __________；日期: __________"),
    ("主程式", "□", "K: ____；interval: ____ ms；檔名: ____________________"),
    ("量桶比對", "□", "實測: ____ L；logger: ____ L；誤差: ____ %"),
    ("安裝", "□", "流向 / 漏水 / 防濺 / 線材固定 / SD 可維修皆完成"),
]
story += [table(["項目", "完成", "結果"], accept, [35*mm, 17*mm, 114*mm], small=True)]
story += [Spacer(1, 7), callout("RTCTest 的特殊行為", "現行 RTCTest 在 setup 一開始就執行 rtc.adjust(compile time)，因此每次燒錄/重啟都會重設 RTC，後面的 lostPower 判斷失去原意。它可用來快速校時，但不適合驗證斷電續時；驗證續時應改掉第一個 adjust 或用主程式。", "warn"), PageBreak()]

# Troubleshooting
story += section_title("09 / TROUBLESHOOTING", "故障排除", "先看 Serial 的第一個錯誤，再回到對應的單元測試。不要同時更改多個參數。")
troubles = [
    ("一直 0 pulse / 0 L/min", "水未流、方向/閥件錯誤；黃線/level shifter/D11 斷路；未共地；pin 設定不一致。", "量 D11 pulse；跑 component test；核對實際 D11，不要照舊註解接 D5。"),
    ("停水仍有小流量", "線路干擾、接地差、長線感應、floating level-shifter output。", "先改善共地/走線/遮蔽；確認 INPUT_PULLUP 適用；最後才設 MIN_VALID_FLOW。"),
    ("讀值固定比例偏高/偏低", "K factor 未校正或 0.45/0.5 版本混用；scale 重複套用。", "重跑 multi-trial；只更新 K，scale=1.0。"),
    ("RTC not found", "VCC/GND/SDA/SCL 錯；I2C pull-up 電壓不對；模組故障。", "確認 SDA=GPIO20、SCL=GPIO21；以 3.3 V 供電並檢查 pull-up。"),
    ("RTC 時間錯 / 回到編譯時間", "電池失效、lostPower；FORCE flag=true；使用 RTCTest 重設。", "換電池、重新校時；正式主程式 flag=false；重跑斷電測試。"),
    ("SD initialization failed", "卡未插、格式不支援、CS 錯、外接 SPI/供電錯。", "確認 D4；先跑 FlowMeterTest；使用 FAT16/FAT32；核對板型。"),
    ("Could not create session file", "日期資料夾無法建立；同秒檔名已存在；卡唯讀/損壞。", "核對 RTC；在電腦備份並檢查卡；清出正確目錄後再試。"),
    ("Could not append data", "卡接觸不良、空間/檔案系統問題、瞬間掉電。", "停止測試，備份並檢查 SD；不要假設缺列期間的 total volume 可回補。"),
    ("USB 上傳失敗", "選錯板/port；SAMD bootloader 未進入。", "重新選 Feather M0；必要時雙擊 reset 進 bootloader，再選新出現的 port。"),
]
story += [table(["症狀", "可能原因", "處理順序"], troubles, [43*mm, 61*mm, 62*mm], small=True)]
story += [Spacer(1, 7), P("Serial 啟動訊息判讀", "H2TC")]
story += [P("RTC not found -> 程式永久停在 stopProgram()<br/>SD initialization failed -> 程式永久停住<br/>same timestamp already exists -> session 建檔失敗並停住<br/>Could not append -> 該列未寫入，但 loop 會繼續；totalVolumeLiters 仍在 RAM 累加", "CodeTC")]
story += [callout("資料完整性界線", "每一列寫完即 close 可降低突然斷電的損失，但不是完整的斷電保護。若 append 失敗，Serial 有錯誤而 CSV 會缺列；程式沒有重試、buffer 補寫或錯誤 LED。", "danger"), PageBreak()]

# Known issues / priorities
story += section_title("10 / KNOWN ISSUES", "已知問題與接手後優先事項", "以下是從 2026-07-22 工作區與程式行為直接辨識出的交接風險。")
issues = [
    ("P0", "確認 D11 電平", "Feather M0 是 3.3 V logic；YF-DN80 在 5 V 供電時高位可能接近 5 V。", "以示波器/萬用表確認 level shifter 後高位 <=3.3 V。"),
    ("P0", "建立單一可追蹤主版本", "FlowMeterMain 為未追蹤資料夾；舊 FlowMeterFirst 在工作區刪除；README 尚指向舊路徑。", "review 後 git add/commit，並更新 README 與檔名。"),
    ("P1", "釐清 K=0.45 來源", "主程式 0.45、校正工具 CURRENT_K=0.5、元件測試 0.5。", "找到校正紀錄或重做校正，統一所有 sketch 與文件。"),
    ("P1", "修正 D5 / D11 註解", "FlowMeterComponetTest 註解寫 D5，實際常數是 D11。", "統一為 D11，避免下一位照註解誤接。"),
    ("P1", "修正 RTCTest", "setup 無條件 rtc.adjust，會讓斷電續時測試失真。", "移除第一個 adjust，只在 lostPower 或明確 flag 時校時。"),
    ("P1", "保存校正紀錄", "工具只在 Serial 顯示結果，repo 內沒有 trial 原始紀錄。", "新增 calibration CSV/Markdown：日期、安裝、體積、pulses、K。"),
    ("P2", "改善 logger 韌性", "SD append 無重試/告警輸出；total volume 不跨重啟保存；同秒檔名會碰撞。", "依實際可靠度需求加 retry、LED、持久化或序號檔名。"),
    ("P2", "建立實物圖", "沒有照片、盒內配置、level shifter/RTC/SD 料號。", "拍正面/背面/端子近照，標 pin、線色、電源與流向。"),
]
story += [table(["優先", "事項", "目前風險", "完成標準"], issues, [15*mm, 43*mm, 57*mm, 51*mm], small=True)]
story += [Spacer(1, 8), P("目前程式檔案地圖", "H2TC")]
filemap = [
    ("Code/FlowMeterMain/FlowMeterMain.ino", "正式整合 logger", "目前工作區主版本；未追蹤。"),
    ("Code/FlowMeterCalibration/FlowMeterCalibration.ino", "互動式多次校正", "未追蹤；D11。"),
    ("Code/FlowMeterComponetTest/FlowMeterComponetTest.ino", "pulse / flow 單元測試", "tracked 但有修改；資料夾拼字 Componet。"),
    ("Code/FlowMeterTest/FlowMeterTest.ino", "SD 30 秒 dummy 測試", "tracked。"),
    ("Code/RTCTest/RTCTest.ino", "RTC 顯示 / 快速校時", "tracked；有無條件 adjust 問題。"),
    ("README.md", "專案入口", "tracked 但有修改；仍列舊 FlowMeterFirst。"),
]
story += [table(["路徑", "用途", "狀態（2026-07-22）"], filemap, [83*mm, 44*mm, 39*mm], small=True), PageBreak()]

# Handoff checklist + sources
story += section_title("HANDOFF CHECKLIST", "交接完成清單與參考資料", "這頁建議與實物一起逐項簽核；空白欄位可列印後手寫。")
checklist = [
    ("□", "硬體", "已確認 Feather 精確型號、sensor 銘牌、RTC/level shifter/SD 模組料號。"),
    ("□", "照片", "已有水流方向、端子、盒內配置、MCU 正反面與電源接法照片。"),
    ("□", "電氣", "D11 pulse high <=3.3 V；共地與極性已量測。"),
    ("□", "韌體", "FlowMeterMain 與 Calibration 已納入 Git；README/註解路徑同步。"),
    ("□", "RTC", "正式程式 flag=false；備援電池與斷電續時已驗證。"),
    ("□", "SD", "FAT16/FAT32；dummy test 與主程式 CSV 均通過。"),
    ("□", "校正", "combined K 有原始 trial 記錄；所有 sketch 使用一致值。"),
    ("□", "驗收", "量桶比對誤差符合專案需求；漏水、線材固定與防濺完成。"),
    ("□", "備份", "原始碼、PDF、校正資料、CSV 範例與照片已放入共同位置。"),
]
story += [table(["", "類別", "完成條件"], checklist, [12*mm, 25*mm, 129*mm], small=True)]
story += [Spacer(1, 8), P("簽核", "H2TC")]
sign = [["交接人", "________________________", "日期", "________________"], ["接手人", "________________________", "日期", "________________"]]
story += [table(["角色", "姓名 / 簽名", "", "日期"], sign, [25*mm, 70*mm, 20*mm, 51*mm], small=True)]
story += [Spacer(1, 9), P("依據與外部參考", "H2TC")]
refs = [
    ("專案原始碼", "README.md 與 Code/ 下五支現行 .ino；另查 Git HEAD 的原始 FlowMeterFirst。"),
    ("Adafruit Feather M0 Adalogger pinouts", '<link href="https://learn.adafruit.com/adafruit-feather-m0-adalogger/pinouts" color="#0B7A75">learn.adafruit.com/adafruit-feather-m0-adalogger/pinouts</link> - 3.3 V logic、SDA/SCL、SPI、板載 SD CS=D4。'),
    ("Adafruit Feather M0 Basic Proto", '<link href="https://learn.adafruit.com/adafruit-feather-m0-basic-proto" color="#0B7A75">learn.adafruit.com/adafruit-feather-m0-basic-proto</link> - ATSAMD21 / 3.3 V / board overview。'),
    ("YF-DN80 製造商產品頁", '<link href="https://www.seadijiang.cn/product_detail/84.html" color="#0B7A75">seadijiang.cn/product_detail/84.html</link> - 3.5-24 VDC、G3、溫度與壓力規格。'),
    ("YF-DN80 pulse 參數交叉核對", '<link href="https://www.ato.com/turbine-water-flow-sensor" color="#0B7A75">ato.com/turbine-water-flow-sensor</link> - F=0.5×Q、20-500 L/min、5 V 時 pulse high 規格。'),
]
story += [table(["來源", "用途"], refs, [55*mm, 111*mm], small=True)]
story += [Spacer(1, 8), callout("文件範圍", "這份 PDF 已完整涵蓋 repo 可證實的 FlowMeter 設計與交接流程，但無法替代現場實物核對。特別是感測器紅/黑線定義、外部電源電壓、level shifter 型號與 SD 是否板載，應以實物標籤和量測為最終依據。", "neutral")]
story += [Spacer(1, 8), P("下一份文件：02 Android Switchboard　｜　第三份文件：03 自動串流程", "SmallTC")]

doc.build(story)
print(OUT)

