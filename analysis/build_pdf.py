"""
Assemble the polished, client-ready PDF report for the RZR analytics case study.
Visual language matches the RZR brand and the interactive site: black/ink
type, an amber-to-crimson accent gradient, and a bold editorial-proposal
layout (big plus-marked headlines, a gradient info block, solid accent
stat boxes).
"""
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem, Flowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ---------------- palette (matches charts.py and site/template.html) ----------------
INK = colors.HexColor("#0b0b0b")
INK_SECONDARY = colors.HexColor("#52514e")
INK_MUTED = colors.HexColor("#898781")
ORANGE = colors.HexColor("#ff5a2e")
AMBER = colors.HexColor("#ffb020")
CRIMSON = colors.HexColor("#e0203f")
GREEN_GOOD = colors.HexColor("#0ca30c")
GRID = colors.HexColor("#e1e0d9")
SURFACE = colors.HexColor("#fcfcfb")
LIGHT_ORANGE_BG = colors.HexColor("#fff0e9")
GRAY_BOX_BG = colors.HexColor("#eeece9")
GRADIENT_STOPS = [colors.HexColor("#ffb020"), colors.HexColor("#ff5a2e"), colors.HexColor("#e0203f")]
GRADIENT_POS = [0, 0.55, 1]

CHARTS = "../output/charts"
SITE_URL = "https://analyticschallengerzr.vercel.app/"
AUTHOR_NAME = "Mark Jerome De Chavez"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/markdechavez128/"
AUTHOR_PORTFOLIO = "https://port2026-chi.vercel.app/"
AUTHOR_GITHUB = "https://github.com/markdechavez28"

styles = getSampleStyleSheet()

styles.add(ParagraphStyle("RZRTitle", fontName="Helvetica-Bold", fontSize=32,
                           textColor=INK, spaceAfter=4, leading=36))
styles.add(ParagraphStyle("RZRSubtitle", fontName="Helvetica-Bold", fontSize=12.5,
                           textColor=INK_SECONDARY, spaceAfter=2, leading=16))
styles.add(ParagraphStyle("RZRBlurb", fontName="Helvetica", fontSize=9.5,
                           textColor=INK_SECONDARY, spaceAfter=2, leading=14))
styles.add(ParagraphStyle("Byline", fontName="Helvetica", fontSize=9.3,
                           textColor=INK_MUTED, spaceAfter=2, leading=13))
styles.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=17, textColor=INK,
                           spaceBefore=22, spaceAfter=10, leading=20))
styles.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=12.5, textColor=INK,
                           spaceBefore=14, spaceAfter=6, leading=16))
styles.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=10, textColor=INK,
                           leading=15, spaceAfter=8, alignment=TA_LEFT))
styles.add(ParagraphStyle("BodySecondary", fontName="Helvetica", fontSize=9.3,
                           textColor=INK_SECONDARY, leading=13.5, spaceAfter=6))
styles.add(ParagraphStyle("Caption", fontName="Helvetica-Oblique", fontSize=8.5,
                           textColor=INK_MUTED, leading=11, spaceAfter=14, spaceBefore=2))
styles.add(ParagraphStyle("BulletBody", fontName="Helvetica", fontSize=10, textColor=INK,
                           leading=14.5, spaceAfter=4))
styles.add(ParagraphStyle("TableHeader", fontName="Helvetica-Bold", fontSize=8.7,
                           textColor=colors.white, alignment=TA_CENTER, leading=11))
styles.add(ParagraphStyle("TableCell", fontName="Helvetica", fontSize=8.7,
                           textColor=INK, alignment=TA_CENTER, leading=11))
styles.add(ParagraphStyle("TableCellLeft", fontName="Helvetica", fontSize=8.7,
                           textColor=INK, alignment=TA_LEFT, leading=11))


def h1(text):
    """Section heading with the brand plus-mark accent."""
    return Paragraph(f'<font color="#ff5a2e"><b>+</b></font>&nbsp;&nbsp;{text}', styles["H1"])


def site_link_markup(link_color="#ff5a2e", underline=False):
    """Renders the companion-site URL as a live hyperlink once a real URL
    is set; falls back to plain bold placeholder text until then."""
    if SITE_URL.startswith("["):
        return f"<b>{SITE_URL}</b>"
    label = f"<b>{SITE_URL}</b>"
    if underline:
        label = f"<u>{label}</u>"
    return f'<a href="{SITE_URL}"><font color="{link_color}">{label}</font></a>'


def callout(text, bg=LIGHT_ORANGE_BG, border=ORANGE, text_color=INK):
    p = Paragraph(text, ParagraphStyle("callout", parent=styles["Body"], textColor=text_color,
                                        fontSize=10, leading=14.5))
    t = Table([[p]], colWidths=[6.6 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 1, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def make_table(header, rows, col_widths, highlight_rows=None, align_left_col0=True):
    highlight_rows = highlight_rows or []
    data = [[Paragraph(h, styles["TableHeader"]) for h in header]]
    for r in rows:
        row_cells = []
        for i, cell in enumerate(r):
            style = styles["TableCellLeft"] if (i == 0 and align_left_col0) else styles["TableCell"]
            row_cells.append(Paragraph(str(cell), style))
        data.append(row_cells)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), CRIMSON),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SURFACE, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for ridx in highlight_rows:
        style_cmds.append(("BACKGROUND", (0, ridx + 1), (-1, ridx + 1), colors.HexColor("#fbe9e9")))
    t.setStyle(TableStyle(style_cmds))
    return t


def stat_box(label, value, bg, text_color):
    label_style = ParagraphStyle("sbl", fontName="Helvetica-Bold", fontSize=8,
                                  textColor=text_color, leading=10)
    value_style = ParagraphStyle("sbv", fontName="Helvetica-Bold", fontSize=25,
                                  textColor=text_color, leading=29, spaceBefore=5)
    return [Paragraph(label.upper(), label_style), Paragraph(value, value_style)]


def stat_box_row(boxes, col_width=3.25 * inch):
    """boxes: list of (label, value, bg, text_color) tuples, rendered as
    solid-color side-by-side cards."""
    row = [stat_box(l, v, bg, tc) for (l, v, bg, tc) in boxes]
    t = Table([row], colWidths=[col_width] * len(boxes))
    style_cmds = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]
    for i, (l, v, bg, tc) in enumerate(boxes):
        style_cmds.append(("BACKGROUND", (i, 0), (i, 0), bg))
    t.setStyle(TableStyle(style_cmds))
    return t


class GradientBlock(Flowable):
    """A rounded rect filled with the brand amber-to-crimson gradient,
    with simple stacked white-text content laid out via a top-down cursor
    (paragraph heights vary with wrapped text, so positions are computed
    from actual wrap() results rather than guessed coordinates)."""

    def __init__(self, width, height, left_lines, right_lines, footer_para=None, pad=18, col_gap=18):
        super().__init__()
        self.width = width
        self.height = height
        self.left_lines = left_lines
        self.right_lines = right_lines
        self.footer_para = footer_para
        self.pad = pad
        self.col_gap = col_gap

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def _stack(self, c, lines, x, top_y, col_w):
        cursor = top_y
        for para, gap_after in lines:
            pw, ph = para.wrap(col_w, 999)
            para.drawOn(c, x, cursor - ph)
            cursor -= ph + gap_after
        return cursor

    def draw(self):
        c = self.canv
        w, h, pad = self.width, self.height, self.pad
        c.saveState()
        path = c.beginPath()
        path.roundRect(0, 0, w, h, 10)
        c.clipPath(path, stroke=0)
        c.linearGradient(0, 0, w, 0, GRADIENT_STOPS, GRADIENT_POS)
        c.restoreState()

        col_w = (w - 2 * pad - self.col_gap) / 2
        top_y = h - pad
        self._stack(c, self.left_lines, pad, top_y, col_w)
        self._stack(c, self.right_lines, pad + col_w + self.col_gap, top_y, col_w)

        if self.footer_para:
            fw, fh = self.footer_para.wrap(w - 2 * pad, 999)
            self.footer_para.drawOn(c, pad, pad - 2)


def chart_image(path, width=6.6 * inch):
    img = Image(path, width=width, height=width * 0.52)
    return img


doc = SimpleDocTemplate(
    "../output/RZR_Lead_Quality_Analysis.pdf",
    pagesize=LETTER,
    topMargin=1.05 * inch, bottomMargin=0.95 * inch,
    leftMargin=0.9 * inch, rightMargin=0.9 * inch,
    title="RZR Lead Quality Analysis", author="Analytics Case Study",
)

story = []

# =========================================================================
# COVER / TITLE
# =========================================================================
header_left = Paragraph(
    '<font size="16" face="Helvetica-Bold">RZR</font> '
    '<font size="8" color="#898781" face="Helvetica-Bold">ANALYTICS</font>',
    ParagraphStyle("hdr_left", fontName="Helvetica", leading=18)
)
header_right = Paragraph(
    "CASE STUDY SUBMISSION<br/>ASSOCIATE ANALYST, LEAD GENERATION",
    ParagraphStyle("hdr_right", fontName="Helvetica-Bold", fontSize=7.5,
                   textColor=INK_MUTED, leading=10.5, alignment=TA_RIGHT)
)
header_table = Table([[header_left, header_right]], colWidths=[3.3 * inch, 3.3 * inch])
header_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
]))
story.append(Spacer(1, 0.3 * inch))
story.append(header_table)
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=1.6, color=INK, spaceAfter=28))

story.append(Paragraph(
    '<font color="#ff5a2e" size="30"><b>+</b></font>&nbsp;&nbsp;Lead Quality Analysis',
    styles["RZRTitle"]
))
story.append(Spacer(1, 4))
story.append(Paragraph("DebtReductionInc Publisher x Debt-Settlement Advertiser, Apr to Sep 2009",
                        styles["RZRSubtitle"]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "A lead-generation case study: one publisher, one debt-settlement advertiser, about 3,021 "
    "leads sold between April and September 2009. This report answers three questions: is lead "
    "quality trending, what drives it, and how do we get to the advertiser's +20% quality target.",
    styles["RZRBlurb"]
))
story.append(Spacer(1, 0.5 * inch))

# ---- gradient info block (prepared for / prepared by / site pointer) ----
label_style = ParagraphStyle("cib_label", fontName="Helvetica-Bold", fontSize=7.5,
                              textColor=colors.white, leading=10)
value_style = ParagraphStyle("cib_value", fontName="Helvetica-Bold", fontSize=13,
                              textColor=colors.white, leading=16)
sub_style = ParagraphStyle("cib_sub", fontName="Helvetica", fontSize=8.5,
                            textColor=colors.HexColor("#fff2ea"), leading=11)
link_style = ParagraphStyle("cib_link", fontName="Helvetica", fontSize=8.5,
                             textColor=colors.HexColor("#fff2ea"), leading=11)
footer_style = ParagraphStyle("cib_foot", fontName="Helvetica", fontSize=8.3,
                               textColor=colors.white, leading=12.5)

left_lines = [
    (Paragraph("PREPARED FOR", label_style), 4),
    (Paragraph("RZR Analytics, Hiring Team", value_style), 3),
    (Paragraph("Associate Analyst Case Study", sub_style), 0),
]
right_lines = [
    (Paragraph("PREPARED BY", label_style), 4),
    (Paragraph(AUTHOR_NAME, value_style), 3),
    (Paragraph(
        f'<a href="{AUTHOR_LINKEDIN}"><u>LinkedIn</u></a>&nbsp;&nbsp;&middot;&nbsp;&nbsp;'
        f'<a href="{AUTHOR_PORTFOLIO}"><u>Portfolio</u></a>&nbsp;&nbsp;&middot;&nbsp;&nbsp;'
        f'<a href="{AUTHOR_GITHUB}"><u>GitHub</u></a>', link_style), 0),
]
footer_para = Paragraph(
    f"<b>More at:</b> an interactive companion site covering all three questions "
    f"(filterable trend view, segment explorer, opportunity sizing) is available at "
    f"{site_link_markup(link_color='#ffffff', underline=True)}. This PDF is the complete, "
    f"standalone report; the site is a bonus exploration layer.",
    footer_style
)
story.append(GradientBlock(6.6 * inch, 2.05 * inch, left_lines, right_lines, footer_para))
story.append(PageBreak())

# ---- Executive summary ----
story.append(h1("Executive Summary"))
story.append(Paragraph(
    "Across the ~3,021 leads sold to the advertiser between April and September 2009, the "
    "blended Closed rate was <b>8.11%</b>, matching the advertiser's stated 8.0% baseline. "
    "Three findings stand out.", styles["Body"]))

story.append(ListFlowable([
    ListItem(Paragraph(
        "<b>Lead quality is declining, and it's statistically significant.</b> The Closed rate "
        "fell from roughly 12-13% in early April to under 5% by late September (logistic "
        "regression p=0.007, Mann-Kendall p=0.013). Notably, the broader \"Good lead\" rate "
        "(Closed + EP-stage progress) shows <i>no</i> significant trend (p=0.81); the decline is "
        "concentrated in final closing, not in raw lead quality reaching the advertiser. That "
        "points toward a downstream sales/closing execution issue as much as a traffic-quality one.",
        styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>Traffic source is the strongest quality driver we can act on.</b> Leads from Google's "
        "Display/Content Network (\"Google-Display\", identifiable by doubleclick.net referrals) "
        "close at just <b>4.1%</b>, less than half the rate of Google-Search (9.9%), AdKnowledge "
        "(12.3%), or Call Center (9.6%) leads, on a real volume of 639 leads (21% of the dataset). "
        "This survives a multivariate model controlling for widget, state, and debt level "
        "(p&lt;0.001). Consumers with debt over $100k also close far less often (3.7% vs 7-14% "
        "elsewhere, p=0.043 controlling for other factors).",
        styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>Redirecting Google-Display spend to Search-equivalent traffic, combined with "
        "excluding the &gt;$100k-debt segment, gets to the 9.6% target</b>, projected blended "
        "rate of <b>9.75%</b>, holding total sold volume constant. This is the headline "
        "recommendation for the advertiser's +20%-quality-for-+20%-CPL offer.",
        styles["BulletBody"])),
], bulletType="bullet", start="•", leftIndent=14))

story.append(Spacer(1, 4))
story.append(Paragraph(
    "See Methodology below for how \"lead quality\" is defined and handled, and the appendix "
    "for full statistical output.", styles["BodySecondary"]))

story.append(PageBreak())

# =========================================================================
# METHODOLOGY
# =========================================================================
story.append(h1("Methodology Note"))

story.append(Paragraph("Lead-quality definition", styles["H2"]))
story.append(Paragraph(
    "The advertiser's stated baseline quality rate (8.0%) reconciles almost exactly with "
    "<b>Closed</b> leads (became a paying customer) as a share of all leads sold: 245 / 3,021 = "
    "8.11%. We use <b>CallStatus == Closed</b> as the primary lead-quality metric throughout "
    "this report, since it is what the advertiser is actually offering to pay more for.",
    styles["Body"]))
story.append(Paragraph(
    "As a secondary, supporting cut, we also report a broader <b>Good</b> definition (Closed + "
    "EP Sent + EP Received + EP Confirmed, any forward progress toward becoming a customer) "
    "against a <b>Bad</b> definition (Unable to Contact + Contacted-Invalid Profile + "
    "Contacted-Doesn't Qualify). The remaining ~71% of leads have a blank CallStatus and are "
    "treated as <b>Unknown</b> (neither good nor bad), per the data dictionary; these are leads "
    "the advertiser has not yet resolved or reported back on. Where the Good/Bad cut would tell "
    "a materially different story than the Closed-only cut, we flag it explicitly (see Q1).",
    styles["Body"]))

story.append(Paragraph("Data cleaning decisions", styles["H2"]))
story.append(ListFlowable([
    ListItem(Paragraph(
        "<b>WidgetName size normalization:</b> ad sizes 300250 and 302252 are confirmed identical "
        "per the data dictionary; widget names were normalized to compare creative/design variants "
        "independent of size.", styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>Partner field split:</b> the Partner column contains both \"google\" (lowercase) and "
        "\"Google\" (capitalized) as distinct values. Cross-referencing ReferralDomain shows this "
        "is not a casing typo: lowercase \"google\" is almost entirely www.google.com (organic/paid "
        "search), while \"Google\" is almost entirely googleads.g.doubleclick.net (Display/Content "
        "Network). We split these into <b>Google-Search</b> and <b>Google-Display</b> since they "
        "show a large, significant quality gap (see Q2) that would otherwise be hidden by merging them.",
        styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>DebtLevel bucket harmonization:</b> the debt-amount bucketing scheme changed mid-dataset. "
        "April-May used a combined \"7500-15000\" bucket, while June onward split it into "
        "\"7500-10000\" and \"10001-15000\". We re-merged these into the coarser \"7500-15000\" "
        "bucket throughout so DebtLevel is comparable across the full date range.",
        styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>PublisherZoneName / PublisherCampaignName / Call-Center Partner are perfectly "
        "collinear</b> in this dataset; the 271 Call Center leads are exactly the \"Top "
        "Right-300x250\" zone and exactly the \"DebtReductionCallCenter\" publisher campaign, no "
        "more and no less. Similarly, <b>AdvertiserCampaignName is perfectly collinear with the "
        "CreditSolutions widget variant</b>. We report each field's univariate relationship but "
        "collapse the redundant ones in the multivariate model (Q2) to avoid double-counting the "
        "same split three times.", styles["BulletBody"])),
], bulletType="bullet", start="•", leftIndent=14))

story.append(Paragraph("Data quality caveats", styles["H2"]))
story.append(ListFlowable([
    ListItem(Paragraph(
        "<b>CallStatus is missing for 2,140 of 3,021 leads (70.8%).</b> These are treated as "
        "Unknown throughout. This is a large enough share that any rate we report should be read "
        "as \"rate among resolved leads,\" not \"rate among all leads sold\"; we note this "
        "wherever it materially matters. Missingness is not evenly distributed (Call Center leads "
        "are resolved more often, 59% missing vs 72% for web-form leads), so naive comparisons "
        "that ignore Unknown status can be misleading across segments.", styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>AddressScore and PhoneScore are only populated from 2009-06-26 onward</b> (1,393 of "
        "3,021 leads, 46%). Any finding involving these fields is necessarily restricted to that "
        "later window and should not be assumed to hold for the full Apr-Sep period.",
        styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>Small-n segments are flagged, not hidden.</b> Throughout Q2, segment levels with fewer "
        "than 30 leads are marked unreliable and excluded from chi-square tests, but shown in full "
        "tables in the appendix for transparency.", styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>Multiple-comparisons risk:</b> Q2 scans many candidate segments (11 widget variants, "
        "31 states, etc.) for the best/worst performer. With that many comparisons, some "
        "differences will look \"significant\" by chance. We call out this risk specifically for "
        "State, where the overall chi-square is not significant (p=0.54) even though individual "
        "states like OK and HI show high raw rates on modest n.", styles["BulletBody"])),
    ListItem(Paragraph(
        "We tested whether placeholder/refused emails (none@none.com, refused@refused.com, etc., "
        "142 leads) predict worse quality; they do not (9.2% vs 8.1% Closed), so this was ruled "
        "out as a filtering lever.", styles["BulletBody"])),
], bulletType="bullet", start="•", leftIndent=14))

story.append(PageBreak())

# =========================================================================
# Q1
# =========================================================================
story.append(h1("Q1: Is Lead Quality Trending Over Time?"))
story.append(Paragraph(
    "<b>Yes, Closed rate is declining, and the decline is statistically significant.</b> We "
    "tested this two ways: a lead-level logistic regression of Closed on week number (the "
    "primary test, since it uses every individual outcome rather than collapsing to weekly "
    "averages first), and a Mann-Kendall non-parametric trend test on the weekly aggregated rate "
    "series as a distribution-free cross-check.", styles["Body"]))

story.append(chart_image(f"{CHARTS}/q1_trend.png"))
story.append(Paragraph(
    "Weekly Closed rate, Apr-Sep 2009. Point size reflects weekly lead volume. Red line is the "
    "fitted logistic trend.", styles["Caption"]))

story.append(make_table(
    ["Test", "Statistic", "Result", "p-value"],
    [
        ["Logistic regression (Closed ~ week)", "OR = 0.974 / week (95% CI 0.956–0.993)",
         "Odds of closing fall ~2.6%/week; ~48% lower by week 25 vs week 0", "0.0072"],
        ["Mann-Kendall (weekly rate series)", "S = −120, z = −2.48", "Decreasing trend confirmed non-parametrically", "0.0131"],
        ["Secondary check: Good rate ~ week", "OR = 1.002 / week", "No significant trend in the broader Good definition", "0.807"],
    ],
    col_widths=[1.7 * inch, 2.0 * inch, 2.1 * inch, 0.75 * inch],
))
story.append(Spacer(1, 6))

story.append(Paragraph(
    "The nuance worth flagging: <b>the decline only shows up in the Closed rate, not in the "
    "broader Good rate</b> (Closed + EP stages). If the traffic mix or lead quality reaching the "
    "advertiser were simply getting worse, we'd expect both metrics to fall together. Instead, "
    "leads appear to be advancing through the EP pipeline at a roughly stable rate over time, but "
    "converting to Closed less often as the year progresses. That's more consistent with a "
    "downstream sales/closing execution change (call-center staffing, worksheet follow-through, "
    "advertiser capacity) than with declining lead quality at the point of sale. It's worth "
    "investigating operationally alongside the traffic-composition levers in Q3.",
    styles["Body"]))

story.append(Paragraph(
    "Monthly Closed rate: Apr 10.8% → May 6.4% → Jun 10.3% → Jul 6.2% → Aug 9.4% → Sep 4.4%. The "
    "month-to-month swings are large, but the week-level regression and Mann-Kendall test both "
    "confirm a genuine downward drift underneath that noise, not just random variation.",
    styles["BodySecondary"]))

story.append(PageBreak())

# =========================================================================
# Q2
# =========================================================================
story.append(h1("Q2: What Drives Lead Quality?"))
story.append(Paragraph(
    "We tested each candidate segment two ways: a chi-square test of independence across all "
    "reliable (n≥30) levels, and, for the top drivers, a multivariate logistic regression that "
    "controls for the other segments simultaneously (since several are correlated, e.g. Call "
    "Center leads cluster on specific publisher zones by construction).", styles["Body"]))

story.append(Paragraph("Ranked driver summary", styles["H2"]))
story.append(make_table(
    ["Segment", "Chi-square p-value", "Survives multivariate control?", "Verdict"],
    [
        ["Partner / traffic source", "0.0001", "Yes: Google-Display p&lt;0.001", "<b>Strong, actionable driver</b>"],
        ["Debt level", "0.091 (overall); &gt;$100k tier significant", "Yes: p=0.043", "<b>Strong, actionable driver</b>"],
        ["PhoneScore", "0.052 (categorical); continuous term significant", "Yes: p=0.039 (post-Jun subset)", "Supporting signal, smaller effect"],
        ["WidgetName / creative", "0.418", "No", "No reliable effect detected"],
        ["PublisherZone / Campaign (web vs call-center)", "0.411", "Collinear with Partner=Call_Center", "No independent effect beyond Partner"],
        ["AdvertiserCampaignName (branded vs generic)", "0.653", "Collinear with widget", "No effect"],
        ["State", "0.538 (overall)", "Borderline for 1-2 states only", "Not reliable, multiple-comparison risk"],
        ["AddressScore", "0.322", "Not tested (dropped for PhoneScore)", "No clean signal"],
    ],
    col_widths=[1.85 * inch, 1.55 * inch, 1.75 * inch, 1.45 * inch],
    highlight_rows=[0, 1],
))
story.append(Spacer(1, 10))

story.append(KeepTogether([
    Paragraph("Traffic source / Partner", styles["H2"]),
    chart_image(f"{CHARTS}/q2_partner.png"),
    Paragraph(
        "Closed rate by traffic source, n≥30 only. Advertise.com (n=3) excluded as unreliable.",
        styles["Caption"]),
]))
story.append(Paragraph(
    "Google-Display leads close at 4.1% vs 9.9% for Google-Search, a statistically significant "
    "gap (two-proportion z-test: z=4.33, p&lt;0.0001) that holds up after controlling for widget, "
    "state, and debt level in the multivariate model (OR=0.31, 95% CI 0.17–0.58, p&lt;0.001, vs "
    "AdKnowledge as reference). It also holds under the broader Good-rate definition (7.0% for "
    "Google-Display vs 13.8-18.7% for other channels), so this isn't an artifact of the Closed-only "
    "metric. Interestingly, Google-Display's <i>bad</i>-lead rate (15.0%) is not much worse than "
    "other channels (13-24%); its problem is specifically weak downstream conversion, consistent "
    "with lower purchase intent from display/content-network impressions versus active search "
    "intent, not a data-quality or fraud issue.", styles["Body"]))

story.append(KeepTogether([
    Paragraph("Debt level", styles["H2"]),
    chart_image(f"{CHARTS}/q2_debtlevel.png"),
    Paragraph("Closed rate by consumer-reported debt level (buckets harmonized, see Methodology).",
              styles["Caption"]),
]))
story.append(Paragraph(
    "Consumers reporting over $100k in debt close at just 3.7%, the lowest of any debt tier, "
    "and the only tier with a below-baseline rate that's also statistically significant in the "
    "multivariate model (p=0.043) after controlling for widget, partner, and state. This tier "
    "also has the highest bad-lead rate (19.9%), so the pattern is consistent across both "
    "definitions: these are less qualified prospects, plausibly because a debt-settlement program "
    "isn't a realistic fit for extremely high balances, or because these leads skew toward "
    "unemployment/inability-to-pay (a disqualifying reason per the data dictionary).",
    styles["Body"]))

story.append(Paragraph("Other segments tested", styles["H2"]))
story.append(Paragraph(
    "<b>WidgetName / creative design</b> shows no statistically reliable effect (chi-square "
    "p=0.42) despite some spread in raw rates (1DC-BlueMeter 14.1%, n=92 vs 1DC-Head3 5.3%, n=75); "
    "with 11 variants compared, that spread is well within what multiple comparisons on modest "
    "sample sizes would produce by chance. <b>PublisherZoneName/PublisherCampaignName</b> "
    "(page placement, web-form vs call-center) shows no effect once you account for the fact "
    "it's identical to the Call_Center partner split already tested above. <b>AdvertiserCampaignName</b> "
    "(branded vs generic ad) shows no effect (p=0.65) and is collinear with the CreditSolutions "
    "widget variant. <b>State</b> is not significant overall (chi-square p=0.54 across 22 reliable "
    "states); a few states like Oklahoma (18.0%, n=50) and Hawaii (15.6%, n=32) look attractive "
    "individually, but with 22+ states tested this is exactly the kind of pattern that shows up by "
    "chance; we don't recommend acting on state alone. <b>PhoneScore</b> shows a modest, "
    "directionally consistent signal (OR=1.24 per point, p=0.039 in the multivariate model "
    "restricted to the post-June scored subsample), higher phone-match confidence associates "
    "with better quality, but the effect is smaller than traffic source or debt level. "
    "<b>AddressScore</b> shows no clean monotonic relationship (p=0.32) and is not a reliable lever.",
    styles["Body"]))

story.append(PageBreak())

# =========================================================================
# Q3
# =========================================================================
story.append(h1("Q3: Path to +20% Lead Quality (8.0% to 9.6%)"))
story.append(Paragraph(
    "The advertiser's offer requires moving the blended Closed rate from 8.0% to 9.6%, a gap of "
    "1.49 percentage points. The two significant, actionable drivers from Q2, traffic source and "
    "debt level, get there when stacked together, with total sold lead volume held constant.",
    styles["Body"]))

story.append(Spacer(1, 4))
story.append(stat_box_row([
    ("Baseline (actual)", "8.11%", GRAY_BOX_BG, INK),
    ("Projected (combined levers)", "9.75%", CRIMSON, colors.white),
], col_width=3.3 * inch))
story.append(Spacer(1, 12))

story.append(chart_image(f"{CHARTS}/q3_waterfall.png"))
story.append(Paragraph(
    "Scenario sizing: each bar assumes total sold volume is held at 3,021 leads; see notes below "
    "for exact assumptions.", styles["Caption"]))

story.append(make_table(
    ["Lever", "Mechanism", "Projected rate", "Lift", "% of gap closed"],
    [
        ["1. Redirect Google-Display budget to Search", "639 Display leads re-sourced via Search at "
         "Search's observed 9.9% rate, same volume", "9.35%", "+1.24pp", "83%"],
        ["2b. Exclude &gt;$100k-debt leads, backfill volume", "191 high-debt leads replaced with "
         "volume at the 8.41% blended rate of all other tiers", "8.41%", "+0.30pp", "20%"],
        ["3. Combined (1 + 2b)", "Both levers stacked, same total volume", "<b>9.75%</b>",
         "<b>+1.64pp</b>", "<b>110%</b>"],
    ],
    col_widths=[2.0 * inch, 2.5 * inch, 0.85 * inch, 0.7 * inch, 0.85 * inch],
    highlight_rows=[2],
))
story.append(Spacer(1, 8))

story.append(Paragraph("Recommended levers", styles["H2"]))
story.append(ListFlowable([
    ListItem(Paragraph(
        "<b>Reallocate Google ad spend from Display/Content Network toward Search.</b> This is "
        "the single highest-leverage move available; it alone closes 83% of the gap. It requires "
        "no changes to the publisher's widgets, forms, or the advertiser relationship; it's a "
        "media-buying decision within the team's direct control. Practically: audit the current "
        "Google campaign structure for content-network/GDN placements (identifiable by "
        "doubleclick.net referral domains) and shift that budget into search-targeted campaigns, "
        "which already show 2.4x the close rate on comparable volume.", styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>Add a debt-level qualification gate before selling &gt;$100k-debt leads,</b> or "
        "route them to a different buyer/program better suited to very high balances. Combined "
        "with the traffic reallocation, this pushes blended quality past the 9.6% target with room "
        "to spare (9.75% projected, 110% of the required gap). Note this reduces the pool of "
        "leads eligible for this advertiser by about 6%; the backfill assumption in scenario 2b "
        "assumes that volume is replaced with additional traffic at the blended rate of the "
        "remaining pool, a reasonable assumption if publisher volume isn't already capacity-constrained.",
        styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>Investigate the Q1 closing-execution decline as a separate, unsized opportunity.</b> "
        "Since the Good-rate trend is flat while Closed-rate is falling, there may be upside "
        "available purely from improving downstream follow-through (worksheet completion "
        "reminders, call-center capacity, faster confirmation turnaround) that wouldn't require "
        "any traffic changes at all. We can't size this precisely from this dataset since it's a "
        "process question, not a composition question, but it's worth an operational review in "
        "parallel with the two levers above.", styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>PhoneScore-based pre-sale filtering is a smaller, supporting lever</b> worth piloting "
        "once the score is available on more of the volume: leads with PhoneScore 4-5 close at "
        "7.6% vs 5.9% for PhoneScore 2-3 within the post-June scored subsample. The effect is real "
        "(p=0.039 in the multivariate model) but modest relative to the two levers above, and "
        "currently only covers 46% of volume.", styles["BulletBody"])),
], bulletType="bullet", start="•", leftIndent=14))

story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>A caution on precision:</b> these scenarios reallocate historical averages forward: they "
    "assume Google-Search and the non-high-debt pool would maintain their observed rates at "
    "higher volume, which may not hold exactly if diminishing returns or audience saturation "
    "kick in at scale. We'd recommend testing the traffic reallocation on a partial-budget basis "
    "first and re-measuring before committing fully.", styles["BodySecondary"]))

story.append(PageBreak())

# =========================================================================
# CONCLUSION
# =========================================================================
story.append(h1("Conclusion"))
story.append(Paragraph(
    "Putting the three questions together: lead quality is worth watching closely right now. It's "
    "trending down over the six months in this dataset, but the cause looks fixable rather than "
    "structural. Two straightforward changes to where traffic comes from and which leads get sold "
    "can plausibly clear the advertiser's quality target on their own, with no changes needed to "
    "the publisher's widgets, forms, or the advertiser relationship.",
    styles["Body"]))

story.append(callout(
    "<b>In plain terms:</b> buy less Google Display traffic and more Google Search traffic, stop "
    "selling leads from consumers carrying over $100k in debt, and keep an eye on whether the "
    "sales team's closing rate recovers on its own over the next few months. Doing the first two "
    "already clears the advertiser's 9.6% bar on paper; doing all three leaves room to beat it."
))

story.append(Paragraph("What this means in practice", styles["H2"]))
story.append(ListFlowable([
    ListItem(Paragraph(
        "<b>This quarter:</b> shift a meaningful share of Google ad spend from Display/Content "
        "Network to Search, and add a debt-level check before selling leads over $100k. Both are "
        "media-buying and qualification decisions within the team's direct control.",
        styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>Ongoing:</b> track Closed rate and Good rate side by side every month. If Good rate "
        "stays flat while Closed rate keeps falling, that confirms the issue is downstream, in "
        "closing execution, not in the leads themselves, and the fix is operational rather than "
        "traffic-related.", styles["BulletBody"])),
    ListItem(Paragraph(
        "<b>As data accumulates:</b> PhoneScore is a promising secondary filter, but it is only "
        "populated for about half of current volume. Once it covers more of the traffic, revisit "
        "it as a pre-sale quality gate.", styles["BulletBody"])),
], bulletType="bullet", start="•", leftIndent=14))

story.append(Spacer(1, 6))
story.append(Paragraph(
    f"For a closer look at any of these numbers, including a segment-by-segment breakdown you can "
    f"filter yourself, see the interactive companion site at {site_link_markup(underline=True)}.",
    styles["Body"]))

story.append(PageBreak())

# =========================================================================
# APPENDIX
# =========================================================================
story.append(h1("Appendix"))

story.append(Paragraph("A1. Overall quality-definition breakdown", styles["H2"]))
story.append(make_table(
    ["Category", "n", "% of total"],
    [
        ["Closed", "245", "8.11%"],
        ["Good (Closed + EP Sent/Received/Confirmed)", "393", "13.01%"],
        ["Bad (Unable to Contact / Invalid Profile / Doesn't Qualify)", "488", "16.15%"],
        ["Unknown (blank CallStatus)", "2,140", "70.84%"],
        ["Total leads sold", "3,021", "100%"],
    ],
    col_widths=[3.6 * inch, 1.0 * inch, 1.2 * inch],
))

story.append(Paragraph("A2. Multivariate logistic regression: key coefficients", styles["H2"]))
story.append(Paragraph(
    "Model: Closed ~ Widget variant + Partner (traffic source) + State (top states + Other) + "
    "Debt level. n=3,021. Reference categories: widget=1DC (base), partner=AdKnowledge, "
    "state=AL, debt=15001-20000.", styles["BodySecondary"]))
story.append(make_table(
    ["Predictor", "Odds ratio", "95% CI", "p-value"],
    [
        ["Google-Display (vs AdKnowledge)", "0.31", "0.17 – 0.58", "&lt;0.001"],
        ["yahoo (vs AdKnowledge)", "0.60", "0.35 – 1.01", "0.053"],
        ["Google-Search (vs AdKnowledge)", "0.83", "0.50 – 1.37", "0.413"],
        ["Call Center (vs AdKnowledge)", "0.68", "0.35 – 1.35", "0.275"],
        ["Debt &gt;$100k (vs 15001-20000)", "0.42", "0.18 – 0.97", "0.043"],
        ["Debt 70001-90000 (vs 15001-20000)", "1.72", "0.93 – 3.18", "0.085"],
        ["New York state (vs top-state baseline)", "0.45", "0.20 – 1.00", "0.049"],
        ["Widget variants (all)", "0.59 - 1.63", "n/a", "all p &gt; 0.16 (n.s.)"],
    ],
    col_widths=[2.6 * inch, 1.1 * inch, 1.3 * inch, 1.1 * inch],
))
story.append(Paragraph(
    "Robustness check adding PhoneScore (restricted to the 1,393 leads with a score, i.e. "
    "created 2009-06-26 or later): PhoneScore OR=1.24 per point, p=0.039, directionally "
    "consistent with the univariate pattern, controlling for widget/partner/state/debt.",
    styles["BodySecondary"]))

story.append(Paragraph("A3. Full segment tables (Closed rate)", styles["H2"]))
story.append(make_table(
    ["Widget variant", "n", "Closed rate"],
    [
        ["1DC-BlueMeter", "92", "14.1%"], ["1DC-Head2", "89", "12.4%"], ["1DC (base)", "620", "9.2%"],
        ["2DC-CreditSolutions", "75", "8.0%"], ["1DC-CreditSolutions", "1,131", "7.8%"],
        ["1DC-yellowarrow-dark", "135", "7.4%"], ["1DC-white", "436", "7.3%"],
        ["2DC-BlueMeter", "87", "6.9%"], ["1DC-yellowarrow-blue", "232", "6.5%"],
        ["1DC-yellowarrow", "49", "6.1%"], ["1DC-Head3", "75", "5.3%"],
    ],
    col_widths=[2.5 * inch, 1.0 * inch, 1.2 * inch],
))
story.append(Spacer(1, 8))
story.append(make_table(
    ["Debt level", "n", "Closed rate", "Good rate", "Bad rate"],
    [
        ["7500-15000", "1,004", "7.5%", "11.6%", "18.3%"],
        ["15001-20000", "408", "8.6%", "14.0%", "12.0%"],
        ["20001-30000", "456", "8.8%", "15.8%", "15.4%"],
        ["30001-50000", "496", "7.9%", "12.3%", "16.9%"],
        ["50001-70000", "245", "9.0%", "15.5%", "13.9%"],
        ["70001-90000", "131", "13.7%", "19.1%", "12.2%"],
        ["90000-100000", "90", "10.0%", "12.2%", "14.4%"],
        ["More than 100000", "191", "3.7%", "6.8%", "19.9%"],
    ],
    col_widths=[1.9 * inch, 0.7 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch],
    highlight_rows=[7],
))

story.append(Spacer(1, 10))
story.append(Paragraph(
    "Full row-level analysis code (Python/pandas/statsmodels/scipy), all intermediate output "
    "tables, and chart-generation scripts are included alongside this report as supporting/"
    "appendix material.", styles["BodySecondary"]))

def draw_page_furniture(canvas, doc_):
    canvas.saveState()

    # running header on every page after the cover
    if doc_.page > 1:
        canvas.setFont("Helvetica-Bold", 7.8)
        canvas.setFillColor(INK_MUTED)
        canvas.drawString(0.9 * inch, LETTER[1] - 0.62 * inch, "RZR  |  LEAD QUALITY ANALYSIS")
        canvas.drawRightString(LETTER[0] - 0.9 * inch, LETTER[1] - 0.62 * inch, "CASE STUDY SUBMISSION")
        canvas.setStrokeColor(INK)
        canvas.setLineWidth(1.2)
        canvas.line(0.9 * inch, LETTER[1] - 0.72 * inch, LETTER[0] - 0.9 * inch, LETTER[1] - 0.72 * inch)

    # footer on every page, including the cover
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.7)
    canvas.line(0.9 * inch, 0.74 * inch, LETTER[0] - 0.9 * inch, 0.74 * inch)

    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(INK_SECONDARY)
    canvas.drawString(0.9 * inch, 0.58 * inch,
                       f"{AUTHOR_NAME}, Analytics Challenge Case Study Submission for RZR, July 2026")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(INK_MUTED)
    canvas.drawRightString(LETTER[0] - 0.9 * inch, 0.58 * inch, f"Page {doc_.page}")

    link_parts = [
        ("LinkedIn", AUTHOR_LINKEDIN),
        ("Portfolio", AUTHOR_PORTFOLIO),
        ("GitHub", AUTHOR_GITHUB),
    ]
    x = 0.9 * inch
    y2 = 0.44 * inch
    for i, (label, url) in enumerate(link_parts):
        canvas.setFont("Helvetica-Bold", 7.6)
        canvas.setFillColor(ORANGE)
        canvas.drawString(x, y2, label)
        w = canvas.stringWidth(label, "Helvetica-Bold", 7.6)
        canvas.linkURL(url, (x, y2 - 1, x + w, y2 + 8), relative=0)
        x += w
        if i < len(link_parts) - 1:
            canvas.setFont("Helvetica", 7.6)
            canvas.setFillColor(INK_MUTED)
            sep = "   |   "
            canvas.drawString(x, y2, sep)
            x += canvas.stringWidth(sep, "Helvetica", 7.6)
    canvas.restoreState()


doc.build(story, onFirstPage=draw_page_furniture, onLaterPages=draw_page_furniture)
print("PDF built: ../output/RZR_Lead_Quality_Analysis.pdf")
