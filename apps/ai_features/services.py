"""AI service layer for HRMS intelligent features."""
import logging
import re

from django.conf import settings

from apps.ai_features.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

HR_SYSTEM_PROMPT = (
    'You are HRMS Pro Assistant, a friendly HR and payroll expert for employees and managers. '
    'Give clear, practical answers in plain language. Use short paragraphs or numbered steps when helpful. '
    'Cover leave, payslips, attendance, payroll, recruitment, performance, policies, and using the HRMS system. '
    'When the user asks follow-up questions like "yes" or "help me more", use the conversation history for context. '
    'If company-specific data is provided below, use it. Otherwise say you do not have that detail and suggest contacting HR. '
    'For managers and HR with a pending leave queue: summarize requests clearly (who, type, dates, days, reason), '
    'highlight short or missing descriptions, and draft approve/reject notes when asked. '
    'Never silently approve or reject leave yourself — provide drafts and guide them to Leave → Requests to act. '
    'When drafting rejection notes, be professional and specific to the employee reason when available.'
)


class ResumeScreeningService:
    """Screen and score resumes against job requirements."""

    @staticmethod
    def screen_resume(applicant_id: str, company=None) -> dict:
        from apps.recruitment.models import Applicant

        qs = Applicant.objects.all()
        if company is not None:
            qs = qs.filter(company=company)
        try:
            applicant = qs.get(pk=applicant_id)
        except Applicant.DoesNotExist:
            return {'error': 'Applicant not found'}

        score = 0.65
        keywords = ['python', 'django', 'management', 'leadership', 'experience']
        cover_lower = (applicant.cover_letter or '').lower()
        matched = [kw for kw in keywords if kw in cover_lower]
        score += len(matched) * 0.05
        score = min(score, 1.0)

        applicant.ai_score = round(score, 2)
        applicant.save(update_fields=['ai_score'])

        return {
            'applicant_id': str(applicant.id),
            'score': applicant.ai_score,
            'matched_keywords': matched,
            'recommendation': 'interview' if score >= 0.6 else 'reject',
        }


class PayrollAnomalyService:
    """Detect anomalies in payroll data."""

    @staticmethod
    def detect_anomalies(payroll_run_id: str, company=None) -> list:
        from apps.payroll.models import Payslip, PayrollRun

        run_qs = PayrollRun.objects.all()
        if company is not None:
            run_qs = run_qs.filter(company=company)
        if not run_qs.filter(pk=payroll_run_id).exists():
            return {'error': 'Payroll run not found'}

        anomalies = []
        payslips = Payslip.objects.filter(payroll_run_id=payroll_run_id)
        if company is not None:
            payslips = payslips.filter(company=company)

        if not payslips.exists():
            return anomalies

        avg_net = sum(p.net_pay for p in payslips) / payslips.count()

        for payslip in payslips:
            if payslip.net_pay > avg_net * 2:
                payslip.is_anomaly = True
                payslip.anomaly_reason = 'Net pay exceeds 200% of average'
                payslip.save(update_fields=['is_anomaly', 'anomaly_reason'])
                anomalies.append({
                    'payslip_id': str(payslip.id),
                    'employee': str(payslip.employee),
                    'reason': payslip.anomaly_reason,
                })

        return anomalies


class AttritionPredictionService:
    """Predict employee attrition risk."""

    @staticmethod
    def predict(employee_id: str, company=None) -> dict:
        from apps.employees.models import Employee

        qs = Employee.objects.all()
        if company is not None:
            qs = qs.filter(company=company)
        try:
            employee = qs.get(pk=employee_id)
        except Employee.DoesNotExist:
            return {'error': 'Employee not found'}

        risk_score = 0.3
        factors = []

        if employee.employment_status == 'probation':
            risk_score += 0.15
            factors.append('Currently on probation')

        warning_count = employee.warnings.filter(is_active=True).count()
        if warning_count > 0:
            risk_score += warning_count * 0.1
            factors.append(f'{warning_count} active warning(s)')

        risk_score = min(risk_score, 1.0)
        risk_level = 'high' if risk_score >= 0.7 else 'medium' if risk_score >= 0.4 else 'low'

        return {
            'employee_id': str(employee.id),
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'factors': factors,
        }


class AttendanceAnomalyService:
    """Detect attendance pattern anomalies."""

    @staticmethod
    def detect(employee_id: str, days: int = 30, company=None) -> list:
        from datetime import timedelta

        from django.utils import timezone

        from apps.attendance.models import AttendanceRecord
        from apps.employees.models import Employee

        emp_qs = Employee.objects.all()
        if company is not None:
            emp_qs = emp_qs.filter(company=company)
        if not emp_qs.filter(pk=employee_id).exists():
            return {'error': 'Employee not found'}

        start_date = timezone.now().date() - timedelta(days=days)
        records = AttendanceRecord.objects.filter(
            employee_id=employee_id, date__gte=start_date
        )
        if company is not None:
            records = records.filter(company=company)

        anomalies = []
        late_count = records.filter(status='late').count()
        if late_count >= 5:
            anomalies.append({
                'type': 'frequent_late',
                'count': late_count,
                'message': f'Employee was late {late_count} times in {days} days',
            })

        return anomalies


class HRChatbotService:
    """HR chatbot: Google Gemini when available, smart contextual assistant otherwise."""

    @classmethod
    def respond(cls, message: str, history: list | None = None, user=None) -> dict:
        history = history or []
        context = cls._user_context(user)
        system_prompt = cls._build_system_prompt(context)

        client = GeminiClient()
        gemini = client.generate(message, history=history, system_prompt=system_prompt)
        if gemini.get('ok'):
            return {
                'text': gemini['text'],
                'source': 'gemini',
                'model': gemini.get('model', ''),
            }

        fallback = cls._smart_reply(message, history, user, context)
        return {
            'text': fallback,
            'source': 'assistant',
            'gemini_error': gemini.get('error'),
        }

    @classmethod
    def ai_status(cls) -> dict:
        client = GeminiClient()
        if not client.configured:
            return {
                'mode': 'assistant',
                'label': 'Smart Assistant',
                'online': False,
                'note': 'Add GEMINI_API_KEY in .env to enable Gemini AI',
            }

        result = client.generate('Reply OK', max_tokens=8)
        if result.get('ok'):
            model = result.get('model', getattr(settings, 'GEMINI_MODEL', ''))
            return {
                'mode': 'gemini',
                'label': 'Gemini AI',
                'online': True,
                'model': model,
            }

        error = result.get('error', 'Unavailable')
        return {
            'mode': 'assistant',
            'label': 'Smart Assistant',
            'online': False,
            'note': f'Gemini unavailable ({error[:80]}) — using built-in HR assistant',
        }

    @classmethod
    def _build_system_prompt(cls, context: dict) -> str:
        lines = [HR_SYSTEM_PROMPT]
        if not context:
            return lines[0]

        lines.append('\n\nEmployee context (use when relevant):')
        if context.get('employee_name'):
            lines.append(f"- Name: {context['employee_name']}")
        if context.get('department'):
            lines.append(f"- Department: {context['department']}")
        if context.get('company_name'):
            lines.append(f"- Company: {context['company_name']}")
        if context.get('role'):
            lines.append(f"- Role: {context['role']}")

        balances = context.get('leave_balances') or []
        if balances:
            bal_text = ', '.join(f"{b['type']}: {b['days']} days" for b in balances[:5])
            lines.append(f'- Leave balances: {bal_text}')

        pending = context.get('pending_leave')
        if pending:
            lines.append(f'- Own open leave requests: {pending}')

        recent = context.get('recent_attendance')
        if recent:
            lines.append(
                f"- Last 7 days attendance: {recent['present']} present, {recent['late']} late"
            )

        approvals = context.get('pending_approvals') or []
        if context.get('can_manage_leave'):
            lines.append('\nLeave approval duties (manager/HR):')
            lines.append(f"- Pending approvals in queue: {context.get('pending_approvals_count', 0)}")
            if approvals:
                lines.append('- Queue details:')
                for item in approvals[:8]:
                    reason = item.get('reason') or 'No description'
                    lines.append(
                        f"  • {item['employee']} | {item['leave_type']} | "
                        f"{item['start_date']} → {item['end_date']} ({item['days']} days) | "
                        f"Reason: {reason}"
                    )
            lines.append(
                '- When asked to summarize or draft approve/reject notes, use this queue. '
                'Remind the user to complete Approve/Reject under Leave → Requests.'
            )

        lines.append(
            '\nHRMS navigation: Leave Management, Payroll > Payslips, Attendance > Clock In, '
            'Performance > Work Tasks, Settings > Users & Roles.'
        )
        return '\n'.join(lines)

    @classmethod
    def _smart_reply(cls, message: str, history: list, user, context: dict | None = None) -> str:
        if context is None:
            context = cls._user_context(user)
        text = message.strip().lower()
        last_assistant = cls._last_assistant_text(history)
        intent = cls._detect_intent(text, last_assistant)

        if intent == 'greeting':
            name = context.get('first_name', 'there')
            extra = ''
            if context.get('can_manage_leave'):
                count = context.get('pending_approvals_count', 0)
                extra = (
                    f" As a manager/HR, I can also summarize **{count}** pending leave "
                    f"approval(s) and draft approve/reject notes.\n\n"
                )
            return (
                f"Hello {name}! I'm your HR assistant. I can help with leave requests, "
                f"payslips, attendance, payroll, performance reviews, and HR policies.\n\n"
                f"{extra}"
                f"What would you like help with today?"
            )

        if intent == 'help':
            help_lines = [
                "Here's what I can help you with:\n",
                "1. **Leave** — apply, check balance, track approvals",
                "2. **Payslips** — download and understand your pay",
                "3. **Attendance** — clock-in, view records, late exceptions",
                "4. **Payroll** — salary, deductions, and pay dates",
                "5. **Performance** — goals, tasks, and reviews",
                "6. **Account** — password and profile settings",
            ]
            if context.get('can_manage_leave'):
                help_lines.extend([
                    "",
                    "**Manager / HR leave duties:**",
                    "• Summarize pending leave approvals",
                    "• Draft approval notes",
                    "• Draft rejection notes with a clear reason",
                    "",
                    "Try: *Summarize pending leave* or *Draft a rejection note*",
                ])
            else:
                help_lines.append(
                    "\nTry asking: *How do I apply for annual leave?* or *Where is my payslip?*"
                )
            return '\n'.join(help_lines)

        if intent == 'leave_approvals':
            return cls._leave_approvals_reply(context)

        if intent == 'draft_approve':
            return cls._draft_leave_decision(context, decision='approve')

        if intent == 'draft_reject':
            return cls._draft_leave_decision(context, decision='reject')

        if intent in ('leave', 'leave_followup'):
            return cls._leave_reply(context, last_assistant, intent == 'leave_followup')

        if intent == 'payslip':
            return (
                "Your payslips are in **Payroll → Payslips** (or your profile under Payroll).\n\n"
                "Steps:\n"
                "1. Open the **Payroll** module from the sidebar\n"
                "2. Select **Payslips**\n"
                "3. Choose the pay period and click **Download PDF**\n\n"
                + cls._employee_line(context)
            )

        if intent == 'attendance':
            return (
                "For attendance:\n\n"
                "1. **Clock in/out** — go to **Attendance → Clock In** (GPS enabled if your branch requires it)\n"
                "2. **View history** — **Attendance → Records** shows daily status\n"
                "3. **Late or missed punch** — contact HR or raise an attendance exception\n\n"
                + cls._attendance_summary(context)
            )

        if intent == 'password':
            return (
                "To change your password:\n\n"
                "1. Click your profile (top right) → **Profile**\n"
                "2. Choose **Change Password**\n"
                "3. Enter current password and your new password twice\n\n"
                "Forgotten password? Use **Forgot password** on the login page or contact HR admin."
            )

        if intent == 'payroll':
            return (
                "Payroll in HRMS covers salary structures, allowances, deductions, tax, and payslip runs.\n\n"
                "Employees: view payslips under **Payroll → Payslips**.\n"
                "HR/Payroll officers: process runs under **Payroll → Payroll Runs**.\n\n"
                + cls._employee_line(context)
            )

        if intent == 'performance':
            return (
                "Performance management includes goals, KPIs, work tasks, and review cycles.\n\n"
                "1. **Tasks** — **Performance → Work Tasks** for assigned items and subtasks\n"
                "2. **Reviews** — **Performance → Reviews** for appraisal cycles\n"
                "3. **Monthly scores** — tracked automatically from task completion\n\n"
                "Ask your manager if you don't see expected goals yet."
            )

        if intent == 'thanks':
            return "You're welcome! Let me know if you need anything else."

        if last_assistant and cls._is_short_followup(text):
            return cls._followup_from_context(text, last_assistant, context)

        return (
            "I'm not sure I understood that. I can help with:\n\n"
            "• Leave and time off\n"
            "• Pending leave approvals (managers/HR)\n"
            "• Draft approve/reject notes\n"
            "• Payslips and payroll\n"
            "• Attendance and clock-in\n"
            "• Performance and tasks\n"
            "• Password and profile\n\n"
            "Please rephrase your question, or type **help** to see all topics."
        )

    @staticmethod
    def _detect_intent(text: str, last_assistant: str) -> str:
        if re.search(r'\b(hi|hello|hey|good morning|good afternoon)\b', text):
            return 'greeting'
        if re.search(r'\b(help me|help|what can you do|assist me)\b', text):
            return 'help'
        if re.search(r'\b(thanks|thank you|cheers)\b', text):
            return 'thanks'
        if re.search(r'\b(password|reset password|change password|forgot password)\b', text):
            return 'password'
        if re.search(r'\b(payslip|pay slip|salary slip|my pay|wage)\b', text):
            return 'payslip'
        if re.search(r'\b(clock.?in|clock.?out|attendance|late|check.?in|check.?out)\b', text):
            return 'attendance'
        if re.search(r'\b(payroll|deduction|tax|pension|net pay)\b', text):
            return 'payroll'
        if re.search(r'\b(performance|review|kpi|goal|task)\b', text):
            return 'performance'
        if re.search(
            r'\b(draft\s+(an?\s+)?(approval|approve)|approve\s+note|approval\s+note|'
            r'write\s+(an?\s+)?approv)',
            text,
        ):
            return 'draft_approve'
        if re.search(
            r'\b(draft\s+(an?\s+)?(rejection|reject)|reject\s+note|rejection\s+note|'
            r'write\s+(an?\s+)?reject)',
            text,
        ):
            return 'draft_reject'
        if re.search(
            r'\b(pending\s+leave|leave\s+approv|approval\s+queue|awaiting\s+approval|'
            r'summariz(e|e)\s+(pending\s+)?leave|leave\s+queue|who\s+is\s+on\s+leave|'
            r'leave\s+request(s)?\s+(to\s+)?(review|approv))',
            text,
        ):
            return 'leave_approvals'
        if re.search(r'\b(leave|vacation|time off|annual|sick day|holiday)\b', text):
            return 'leave'
        if last_assistant and 'leave' in last_assistant.lower():
            if re.search(r'\b(yes|ok|okay|sure|please|apply|how)\b', text):
                return 'leave_followup'
        return 'unknown'

    @staticmethod
    def _is_short_followup(text: str) -> bool:
        return len(text.split()) <= 4 or text in {'yes', 'ok', 'okay', 'sure', 'please', 'help me'}

    @classmethod
    def _followup_from_context(cls, text: str, last_assistant: str, context: dict) -> str:
        last_lower = last_assistant.lower()
        if 'approv' in last_lower or 'pending leave' in last_lower:
            if 'reject' in text:
                return cls._draft_leave_decision(context, decision='reject')
            if 'approv' in text:
                return cls._draft_leave_decision(context, decision='approve')
            return cls._leave_approvals_reply(context)
        if 'leave' in last_lower:
            return cls._leave_reply(context, last_assistant, followup=True)
        if 'payslip' in last_lower or 'payroll' in last_lower:
            return (
                "Your payslips are in **Payroll → Payslips** (or your profile under Payroll).\n\n"
                "Steps:\n"
                "1. Open the **Payroll** module from the sidebar\n"
                "2. Select **Payslips**\n"
                "3. Choose the pay period and click **Download PDF**\n\n"
                + cls._employee_line(context)
            )
        if 'attendance' in last_lower or 'clock' in last_lower:
            return (
                "To clock in now, go to **Attendance → Clock In** in the sidebar.\n"
                "Make sure location access is enabled if your branch uses GPS check-in."
            )
        return (
            "Happy to help further. Try asking:\n"
            "• *Summarize pending leave*\n"
            "• *Draft an approval note*\n"
            "• *How do I apply for leave?*\n"
            "• *Where is my payslip?*"
        )

    @classmethod
    def _leave_reply(cls, context: dict, last_assistant: str, followup: bool = False) -> str:
        lines = [
            "**How to apply for leave:**",
            "1. Open **Leave Management** from the sidebar",
            "2. Click **New Leave Request** (or use the form in Leave Requests)",
            "3. Select leave type (annual, sick, unpaid, etc.)",
            "4. Pick start and end dates and add a **description/reason** (shown during approval)",
            "5. Submit — your manager will receive it for approval",
        ]

        balances = context.get('leave_balances') or []
        if balances:
            lines.append("\n**Your leave balances:**")
            for item in balances[:5]:
                lines.append(f"• {item['type']}: {item['days']} days remaining")

        pending = context.get('pending_leave', 0)
        if pending:
            lines.append(f"\nYou have **{pending}** leave request(s) awaiting approval.")

        if context.get('can_manage_leave'):
            count = context.get('pending_approvals_count', 0)
            lines.append(
                f"\nAs an approver, you currently have **{count}** pending leave request(s) to review. "
                "Ask me to *summarize pending leave* or *draft an approval note*."
            )

        if followup and last_assistant:
            lines.insert(0, "Sure — here are the detailed steps:\n")

        lines.append("\nNeed a specific leave type explained? Ask e.g. *Can I take sick leave?*")
        return '\n'.join(lines)

    @classmethod
    def _leave_approvals_reply(cls, context: dict) -> str:
        if not context.get('can_manage_leave'):
            return (
                "Leave approval summaries are for managers and HR. "
                "You can still ask about **your own leave** balance or how to apply.\n\n"
                "Your open requests: **"
                f"{context.get('pending_leave', 0)}**."
            )

        approvals = context.get('pending_approvals') or []
        count = context.get('pending_approvals_count', 0)
        if not approvals:
            return (
                "There are **no pending leave requests** waiting for approval right now.\n\n"
                "Check again later under **Leave → Requests**, or ask me to help once new requests arrive."
            )

        lines = [
            f"**Pending leave approvals ({count}):**\n",
        ]
        for idx, item in enumerate(approvals[:8], start=1):
            reason = (item.get('reason') or '').strip() or '_No description provided_'
            lines.append(
                f"**{idx}. {item['employee']}** — {item['leave_type']}\n"
                f"   • Period: {item['start_date']} → {item['end_date']} ({item['days']} days)\n"
                f"   • Description: {reason}"
            )

        missing = sum(1 for i in approvals if not (i.get('reason') or '').strip())
        if missing:
            lines.append(
                f"\n⚠ **{missing}** request(s) have no description — ask the employee for more detail before approving."
            )

        lines.append(
            "\nI can **draft an approval note** or **draft a rejection note** for the first request "
            "(or name the employee). Then open **Leave → Requests → Edit** to Approve / Reject."
        )
        return '\n'.join(lines)

    @classmethod
    def _draft_leave_decision(cls, context: dict, decision: str = 'approve') -> str:
        if not context.get('can_manage_leave'):
            return (
                "Drafting approve/reject notes is available to managers and HR approvers. "
                "Employees: track your request status under **Leave → Requests**."
            )

        approvals = context.get('pending_approvals') or []
        if not approvals:
            return (
                "No pending leave requests to draft notes for. "
                "When requests arrive, ask me again or open **Leave → Requests**."
            )

        item = approvals[0]
        reason = (item.get('reason') or '').strip()
        employee = item['employee']
        leave_type = item['leave_type']
        period = f"{item['start_date']} → {item['end_date']}"
        days = item['days']

        if decision == 'approve':
            if reason:
                note = (
                    f"Approved. {leave_type} for {employee} ({period}, {days} days) "
                    f"is cleared based on the submitted description: \"{reason[:180]}\"."
                )
            else:
                note = (
                    f"Approved. {leave_type} for {employee} ({period}, {days} days) "
                    f"is cleared. Please ensure coverage is arranged with the team."
                )
            title = 'Draft approval note'
            tip = 'Paste into **Approval notes** if needed, set status to **Approved**, or click **Approve**.'
        else:
            if reason:
                note = (
                    f"Unable to approve this {leave_type} request for {period} at this time. "
                    f"We reviewed your reason (\"{reason[:140]}\") and need adjusted dates or "
                    f"additional documentation. Please revise and resubmit, or speak with your manager."
                )
            else:
                note = (
                    f"Unable to approve this {leave_type} request for {period}: "
                    f"no description was provided. Please resubmit with a clear reason and preferred dates."
                )
            title = 'Draft rejection note'
            tip = 'Paste into **Approval notes / Rejection reason**, then click **Reject** on the leave edit form.'

        return (
            f"**{title}** for **{employee}** ({leave_type}, {days} days):\n\n"
            f"> {note}\n\n"
            f"**Request description:** {reason or '_None_'}\n\n"
            f"{tip}\n"
            f"Open: **Leave → Requests → Edit**."
        )

    @staticmethod
    def _last_assistant_text(history: list) -> str:
        for item in reversed(history):
            if item.get('role') == 'assistant':
                return item.get('content', '')
        return ''

    @staticmethod
    def _employee_line(context: dict) -> str:
        if context.get('employee_name'):
            return f"Logged in as **{context['employee_name']}** ({context.get('department', 'Employee')})."
        return ''

    @staticmethod
    def _attendance_summary(context: dict) -> str:
        recent = context.get('recent_attendance')
        if not recent:
            return ''
        return f"Recent attendance: **{recent['present']} present**, **{recent['late']} late** (last 7 days)."

    @staticmethod
    def _user_context(user) -> dict:
        """Build AI context strictly scoped to the user's company (never another tenant)."""
        if not user or not getattr(user, 'is_authenticated', False):
            return {}

        from apps.accounts.permissions import can_manage_leave

        company = getattr(user, 'company', None)
        context = {
            'first_name': getattr(user, 'first_name', None) or user.get_username().split('@')[0],
            'role': getattr(user, 'role', '') or 'employee',
            'can_manage_leave': bool(can_manage_leave(user)),
            'pending_approvals': [],
            'pending_approvals_count': 0,
        }
        if company:
            context['company_name'] = company.name
            context['company_slug'] = company.slug

        try:
            from datetime import timedelta

            from django.utils import timezone

            from apps.attendance.models import AttendanceRecord
            from apps.employees.models import Employee
            from apps.leave.models import LeaveBalance, LeaveRequest

            # Always prefer the OneToOne link, then email — but ALWAYS filter by company
            employee_qs = Employee.objects.select_related('department', 'company')
            if company:
                employee_qs = employee_qs.filter(company=company)

            employee = employee_qs.filter(user=user).first()
            if not employee and company:
                employee = employee_qs.filter(email=user.email, company=company).first()

            if employee and company and employee.company_id != company.id:
                employee = None

            if employee:
                context['employee_name'] = employee.full_name
                context['department'] = getattr(employee.department, 'name', 'Employee')

                balances = LeaveBalance.objects.filter(
                    employee=employee,
                    company=employee.company,
                ).select_related('leave_type')[:5]
                context['leave_balances'] = [
                    {
                        'type': b.leave_type.name,
                        'days': float(b.available),
                    }
                    for b in balances
                ]

                context['pending_leave'] = LeaveRequest.objects.filter(
                    employee=employee,
                    company=employee.company,
                    status__in=('pending', 'submitted', 'approved'),
                ).exclude(status='completed').count()

                week_ago = timezone.now().date() - timedelta(days=7)
                records = AttendanceRecord.objects.filter(
                    employee=employee,
                    company=employee.company,
                    date__gte=week_ago,
                )
                context['recent_attendance'] = {
                    'present': records.filter(status='present').count(),
                    'late': records.filter(status='late').count(),
                }

            # Manager / HR leave approval queue (company-scoped)
            if context['can_manage_leave'] and company:
                pending_qs = (
                    LeaveRequest.objects.filter(
                        company=company,
                        status=LeaveRequest.Status.PENDING,
                    )
                    .select_related('employee', 'leave_type')
                    .order_by('start_date', 'created_at')
                )
                context['pending_approvals_count'] = pending_qs.count()
                context['pending_approvals'] = [
                    {
                        'id': str(req.id),
                        'employee': str(req.employee),
                        'leave_type': str(req.leave_type),
                        'start_date': str(req.start_date),
                        'end_date': str(req.end_date),
                        'days': float(req.days_requested),
                        'reason': (req.reason or '')[:240],
                        'status': req.status,
                    }
                    for req in pending_qs[:8]
                ]
        except Exception as exc:
            logger.debug('Chatbot user context lookup failed: %s', exc)

        return context
