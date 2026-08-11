"""Generate HRMS Pro presentation with live UI screenshots."""
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

FOREST = RGBColor(0x1B, 0x4D, 0x3E)
TEAL = RGBColor(0x2A, 0x6F, 0x5F)
ACCENT = RGBColor(0xC4, 0xA3, 0x5A)
LIGHT = RGBColor(0xF3, 0xF6, 0xF4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x1A, 0x1F, 0x1E)
MUTED = RGBColor(0x5A, 0x66, 0x62)
SHOTS = Path(r'd:\Projects Running\HR & Payroll System\docs\presentation_shots')


def set_run(run, size=18, bold=False, color=DARK, font='Calibri'):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_bg(slide, color=LIGHT):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    sp_tree = slide.shapes._spTree
    sp = shape._element
    sp_tree.remove(sp)
    sp_tree.insert(2, sp)


def add_bar(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_text(slide, left, top, width, height, text, size=18, bold=False, color=DARK, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color)
    return box


def add_bullets(slide, left, top, width, height, items, size=16, color=DARK, spacing=8):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(spacing)
        run = p.add_run()
        run.text = '•  ' + item
        set_run(run, size=size, color=color)
    return box


def add_card(slide, left, top, width, height, title, lines):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = RGBColor(0xD5, 0xE0, 0xDB)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.1), height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()
    add_text(slide, left + Inches(0.25), top + Inches(0.15), width - Inches(0.35), Inches(0.35),
             title, size=15, bold=True, color=FOREST)
    add_bullets(slide, left + Inches(0.2), top + Inches(0.5), width - Inches(0.35), height - Inches(0.6),
                lines, size=12, color=MUTED, spacing=5)


def section_header(slide, title, subtitle=''):
    add_bg(slide, LIGHT)
    add_bar(slide, 0, 0, prs.slide_width, Inches(0.07), FOREST)
    add_bar(slide, 0, Inches(7.43), prs.slide_width, Inches(0.07), FOREST)
    add_text(slide, Inches(0.55), Inches(0.22), Inches(12), Inches(0.45), title, size=28, bold=True, color=FOREST)
    if subtitle:
        add_text(slide, Inches(0.55), Inches(0.68), Inches(12), Inches(0.32), subtitle, size=14, color=MUTED)
    add_bar(slide, Inches(0.55), Inches(1.05), Inches(1.0), Inches(0.05), ACCENT)


def add_shot(slide, filename, left, top, width, height=None):
    """Embed screenshot preserving aspect ratio (width-driven unless height given)."""
    path = SHOTS / filename
    if not path.exists():
        return None
    # Native shots are 1440x900
    if height is None:
        height = width * 900 / 1440
    frame = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left - Inches(0.04),
        top - Inches(0.04),
        width + Inches(0.08),
        height + Inches(0.08),
    )
    frame.fill.solid()
    frame.fill.fore_color.rgb = WHITE
    frame.line.color.rgb = RGBColor(0xC8, 0xD5, 0xCF)
    return slide.shapes.add_picture(str(path), left, top, width=width, height=height)


def feature_slide(title, subtitle, bullets, shot_file, caption='Live product screenshot'):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    section_header(slide, title, subtitle)
    # Left text panel
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.45), Inches(1.3), Inches(4.3), Inches(5.7))
    panel.fill.solid()
    panel.fill.fore_color.rgb = WHITE
    panel.line.color.rgb = RGBColor(0xD5, 0xE0, 0xDB)
    add_text(slide, Inches(0.7), Inches(1.5), Inches(3.9), Inches(0.35), 'What you can do', size=14, bold=True, color=TEAL)
    add_bullets(slide, Inches(0.65), Inches(1.95), Inches(3.9), Inches(4.6), bullets, size=15, spacing=10)
    # Screenshot on right
    add_shot(slide, shot_file, Inches(5.0), Inches(1.35), Inches(7.85))
    add_text(slide, Inches(5.0), Inches(6.4), Inches(7.85), Inches(0.3), caption, size=11, color=MUTED, align=PP_ALIGN.CENTER)
    return slide


# ===== 1 Title =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, FOREST)
add_bar(slide, 0, Inches(5.85), prs.slide_width, Inches(1.65), TEAL)
add_text(slide, Inches(0.8), Inches(1.6), Inches(11), Inches(0.4), 'HRMS PRO', size=18, bold=True, color=ACCENT)
add_text(slide, Inches(0.8), Inches(2.1), Inches(11.5), Inches(1.1),
         'Human Resource & Payroll System', size=36, bold=True, color=WHITE)
add_text(slide, Inches(0.8), Inches(3.3), Inches(11), Inches(0.5),
         'Feature tour with real product screenshots', size=20, color=RGBColor(0xC8, 0xD9, 0xD3))
add_text(slide, Inches(0.8), Inches(6.2), Inches(11), Inches(0.4),
         'Dashboard  ·  People  ·  Payroll  ·  Leave  ·  AI  ·  Security', size=15, color=WHITE)
add_text(slide, Inches(0.8), Inches(6.65), Inches(11), Inches(0.3),
         'Live UI from Acme Corporation demo tenant  |  2026', size=13, color=RGBColor(0xB0, 0xC8, 0xC0))

# ===== 2 Agenda =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
section_header(slide, 'Agenda', 'A visual walkthrough of the full platform')
add_bullets(slide, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.5), [
    '1. Login & tenant portal look',
    '2. Main dashboard overview',
    '3. Employees & recruitment',
    '4. Leave, attendance & payroll',
    '5. Performance, AI & reports',
    '6. Settings, roles & security',
    '7. Why it matters',
], size=20, spacing=16)

# ===== 3 Login look =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
section_header(slide, 'Tenant Login Experience', 'Each company gets its own branded portal')
add_shot(slide, '02_login.png', Inches(0.7), Inches(1.3), Inches(8.2))
add_card(slide, Inches(9.2), Inches(1.5), Inches(3.6), Inches(4.8), 'Key points', [
    'Split-screen branded login',
    'URL: /t/company-slug/',
    'Email or phone sign-in',
    'Tenant data stays isolated',
    'Optional OAuth providers',
    'MFA-ready security',
])

# ===== 4 Dashboard hero =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
section_header(slide, 'Main Dashboard', 'Your daily command center')
# Full-width dashboard shot (fit height under footer)
add_shot(slide, '03_dashboard.png', Inches(1.5), Inches(1.2), Inches(10.3))
add_text(
    slide, Inches(0.7), Inches(6.85), Inches(12), Inches(0.3),
    'Live Acme Corporation dashboard — stats, shortcuts, announcements',
    size=12, color=MUTED, align=PP_ALIGN.CENTER,
)

# ===== 5 Dashboard explained =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
section_header(slide, 'Dashboard — What Leaders See', 'Stats, shortcuts, and activity in one place')
cards = [
    ('Quick actions', ['Add employee', 'Leave queue', 'Analytics']),
    ('Live metrics', ['Headcount', 'Present / on leave', 'Open jobs & payroll']),
    ('Navigation', ['Core HR, Finance, Growth', 'Workplace & Insights', 'Settings at bottom']),
    ('Activity feed', ['Announcements', 'Recent updates', 'Pending approvals']),
]
for i, (t, lines) in enumerate(cards):
    r, c = divmod(i, 2)
    add_card(slide, Inches(0.6) + Inches(c * 6.3), Inches(1.4) + Inches(r * 2.8),
             Inches(6.0), Inches(2.55), t, lines)

# ===== Feature slides with screenshots =====
feature_slide(
    'Employees',
    'Central people directory',
    [
        'Search and filter staff',
        'View full employee details',
        'Link dept, role & manager',
        'Employment status tracking',
        'Soft-delete keeps history',
        'Feeds leave & payroll',
    ],
    '04_employees.png',
)

feature_slide(
    'Recruitment & Onboarding',
    'Jobs → applicants → interviews',
    [
        'Post open roles',
        'Track applicants per job',
        'AI resume scoring',
        'Schedule interviews',
        'Rate candidates',
        'Hire into employee records',
    ],
    '05_recruitment.png',
)

feature_slide(
    'Leave Management',
    'Apply, approve, track balances',
    [
        'Employee leave requests',
        'Balance checks built-in',
        'Approve / reject with notes',
        'Multi-level approvals',
        'Calendar visibility',
        'AI leave summaries',
    ],
    '06_leave.png',
)

feature_slide(
    'Time & Attendance',
    'Presence, lateness, overtime',
    [
        'Daily attendance records',
        'Portal clock-in / out',
        'Late & overtime tracking',
        'Exceptions & shifts',
        'Biometric / GPS ready',
        'Syncs into payroll',
    ],
    '07_attendance.png',
)

feature_slide(
    'Payroll & Compliance',
    'Runs, payslips, and loans',
    [
        'Create payroll runs',
        'Gross → net calculation',
        'Employee payslips',
        'AI anomaly flags',
        'Staff loan deductions',
        'Review & approve flow',
    ],
    '08_payroll.png',
)

feature_slide(
    'Performance Management',
    'Goals, tasks, and reviews',
    [
        'Assign goals & tasks',
        'Due dates and points',
        'Track progress %',
        'Manager review cycles',
        'Ratings & feedback',
        'Coach teams clearly',
    ],
    '09_performance.png',
)

feature_slide(
    'AI Assistant',
    'Smart help for HR & managers',
    [
        'Resume screening scores',
        'Payroll anomaly detection',
        'Attendance checks',
        'Summarize pending leave',
        'Draft approve/reject notes',
        'Company-scoped chat only',
    ],
    '10_ai.png',
)

feature_slide(
    'Reports & Insights',
    'See the big picture fast',
    [
        'Workforce analytics',
        'Leave & payroll reports',
        'Operational visibility',
        'Export-ready views',
        'Support leadership decisions',
    ],
    '11_reports.png',
)

feature_slide(
    'System Settings',
    'Users, org structure, preferences',
    [
        'Manage users & roles',
        'Branches & departments',
        'Job designations',
        'Company profile',
        'Operational preferences',
    ],
    '12_settings.png',
)

feature_slide(
    'Role Catalog (Super Admin)',
    'Enable or remove roles per tenant',
    [
        'Turn roles on/off by need',
        'Super Admin + Employee required',
        'Promote / demote users safely',
        'Blocks removing last Super Admin',
        'Fits each company’s structure',
    ],
    '13_roles.png',
)

# Relations / Casuals / Surveys (text cards — no dedicated shot needed)
slide = prs.slides.add_slide(prs.slide_layouts[6])
section_header(slide, 'Also Included', 'Relations, disciplinary, casuals & surveys')
add_card(slide, Inches(0.55), Inches(1.4), Inches(4.0), Inches(5.4), 'Relations & Awards', [
    'Recognize good work',
    'Track relations cases',
    'Linked to employee history',
])
add_card(slide, Inches(4.7), Inches(1.4), Inches(4.0), Inches(5.4), 'Disciplinary', [
    'Log incidents',
    'Investigations & hearings',
    'Warnings to dismissal',
    'Fair, auditable process',
])
add_card(slide, Inches(8.85), Inches(1.4), Inches(4.0), Inches(5.4), 'Casuals & Surveys', [
    'Temporary worker management',
    'Supervisor oversight',
    'Anonymous staff surveys',
    'Sentiment over time',
])

# Security
slide = prs.slides.add_slide(prs.slide_layouts[6])
section_header(slide, 'Security & Multi-Tenant', 'Enterprise protection built in')
add_bullets(slide, Inches(0.8), Inches(1.4), Inches(11.5), Inches(5.5), [
    'Secure login (email / phone) with optional MFA',
    'Account lockout after failed attempts',
    'Role-Based Access Control for every module',
    'Strict tenant isolation — companies never share data',
    'Audit logs for important actions',
    'REST API + OAuth for modern integrations',
], size=20, spacing=14)

# Benefits
slide = prs.slides.add_slide(prs.slide_layouts[6])
section_header(slide, 'Why HRMS Pro?', 'Clear value for the business')
benefits = [
    ('One system', ['Replace scattered Excel tools']),
    ('Faster HR', ['Hire, leave & payroll quicker']),
    ('Fewer errors', ['Balances + AI checks']),
    ('Strong control', ['Roles, tenants, audit']),
    ('Scalable SaaS', ['One company or many']),
    ('Modern UI', ['Clean dashboard people use']),
]
for i, (t, d) in enumerate(benefits):
    r, c = divmod(i, 3)
    add_card(slide, Inches(0.55) + Inches(c * 4.2), Inches(1.4) + Inches(r * 2.7),
             Inches(4.0), Inches(2.45), t, d)

# Closing
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, FOREST)
add_bar(slide, 0, Inches(5.85), prs.slide_width, Inches(1.65), TEAL)
add_text(slide, Inches(0.8), Inches(2.2), Inches(11.5), Inches(0.9),
         'Thank You', size=44, bold=True, color=WHITE)
add_text(slide, Inches(0.8), Inches(3.3), Inches(11.5), Inches(0.6),
         'Questions? We can open a live demo next.', size=22, color=RGBColor(0xC8, 0xD9, 0xD3))
add_text(slide, Inches(0.8), Inches(6.25), Inches(11.5), Inches(0.4),
         'HRMS Pro  ·  Screenshots from live Acme Corporation tenant', size=15, color=WHITE)

out = Path(r'd:\Projects Running\HR & Payroll System\docs\HRMS-Pro-Features-Presentation-v2.pptx')
prs.save(str(out))
# Also try overwriting original if unlocked
legacy = Path(r'd:\Projects Running\HR & Payroll System\docs\HRMS-Pro-Features-Presentation.pptx')
try:
    prs.save(str(legacy))
    print('Also updated:', legacy.name)
except PermissionError:
    print('Original PPTX is open — saved as v2 only. Close PowerPoint and re-run to replace.')
print('Saved:', out)
print('Slides:', len(prs.slides))
print('Size KB:', round(out.stat().st_size / 1024))
