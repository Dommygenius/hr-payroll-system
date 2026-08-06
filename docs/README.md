# HRMS Pro — Design Documentation Index

| Document | Format | Description |
|----------|--------|-------------|
| [HRMS-System-Design-Documentation.md](./HRMS-System-Design-Documentation.md) | Markdown | Full technical docs with Mermaid flowcharts & ER diagrams |
| [HRMS-System-Design.pptx](./HRMS-System-Design.pptx) | PowerPoint | Presentation slides for stakeholders |

## Regenerate PowerPoint

```powershell
venv\Scripts\python docs/generate_presentation.py
```

## View Mermaid Diagrams

Open `HRMS-System-Design-Documentation.md` in:
- **VS Code / Cursor** with Mermaid preview extension
- **GitHub** (renders Mermaid natively)
- **https://mermaid.live** — paste diagram blocks for export to PNG/SVG

## Contents Overview

### Flowcharts (in both docs)
- System architecture
- Authentication & security flow
- Recruitment & onboarding
- Leave management (multi-level approval)
- Payroll processing (with AI anomaly detection)
- Time & attendance (biometric, QR, GPS)
- Performance review cycle
- Disciplinary process

### Database Design
- Company-centric multi-tenant ER model
- 58+ entity tables across 17 Django apps
- Relationship summary with FK details
- Module-grouped ER diagrams (Core, Auth, Employee, Payroll, Leave, etc.)
