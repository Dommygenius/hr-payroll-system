"""Capture live UI screenshots for the HRMS presentation."""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8000'
TENANT = f'{BASE}/t/acme-corp'
OUT = Path(r'd:\Projects Running\HR & Payroll System\docs\presentation_shots')
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [
    ('01_landing', f'{BASE}/', False),
    ('02_login', f'{TENANT}/accounts/login/', False),
    ('03_dashboard', f'{TENANT}/dashboard/', True),
    ('04_employees', f'{TENANT}/module/employees/list/', True),
    ('05_recruitment', f'{TENANT}/module/recruitment/jobs/', True),
    ('06_leave', f'{TENANT}/module/leave/requests/', True),
    ('07_attendance', f'{TENANT}/module/attendance/', True),
    ('08_payroll', f'{TENANT}/module/payroll/runs/', True),
    ('09_performance', f'{TENANT}/module/performance/', True),
    ('10_ai', f'{TENANT}/module/ai/', True),
    ('11_reports', f'{TENANT}/module/reports/', True),
    ('12_settings', f'{TENANT}/module/settings/', True),
    ('13_roles', f'{TENANT}/module/settings/roles/', True),
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            device_scale_factor=1.25,
        )
        page = context.new_page()

        # Login once
        page.goto(f'{TENANT}/accounts/login/', wait_until='networkidle', timeout=60000)
        page.fill('input[name="username"]', 'admin@acme.com')
        page.fill('input[name="password"]', 'Admin@123456')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        print('Logged in:', page.url)

        for name, url, _needs_auth in PAGES:
            try:
                page.goto(url, wait_until='networkidle', timeout=45000)
                page.wait_for_timeout(800)
                # Hide flash messages if any clutter
                path = OUT / f'{name}.png'
                page.screenshot(path=str(path), full_page=False)
                print('OK', name, '->', path.name, 'status ok')
            except Exception as e:
                print('FAIL', name, e)

        browser.close()
    print('Done. Shots in', OUT)


if __name__ == '__main__':
    main()
