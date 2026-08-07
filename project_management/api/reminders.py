import frappe
from frappe.utils import add_days, getdate, today

BOT_NAME = "Project Manager Bot"


def send_overdue_task_reminders():
    """Daily scheduled job.

    Sends automated reminder alerts to the assignee (via a Raven bot DM) for
    tasks that are "not on track", i.e. not Completed AND either overdue or
    due within the configured reminder window. Only projects that have
    reminders enabled are considered.
    """

    bot = _get_bot()
    if not bot:
        frappe.log_error(
            "Raven Bot '{}' was not found or has no Raven User.".format(BOT_NAME),
            "Project Management Reminders",
        )
        return

    for task, project in _get_targets():

        assignee = _resolve_assignee(task, project)
        if not assignee:
            continue

        if not _should_remind(task, project):
            continue

        try:
            bot.send_direct_message(
                user_id=assignee,
                text=_build_message(task, project),
                link_doctype="Project Task",
                link_document=task["name"],
            )
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                "Failed to send reminder for task {}".format(task["name"]),
            )
            continue

        frappe.db.set_value(
            "Project Task",
            task["name"],
            "last_reminder_on",
            today(),
        )

    frappe.db.commit()


def _get_bot():
    """Return (or create) the Raven bot used to send reminders."""

    if not frappe.db.exists("DocType", "Raven Bot"):
        return None

    existing = frappe.db.get_value("Raven Bot", {"bot_name": BOT_NAME}, "name")
    if existing:
        return frappe.get_doc("Raven Bot", existing)

    try:
        bot = frappe.new_doc("Raven Bot")
        bot.bot_name = BOT_NAME
        bot.is_ai_bot = 0
        bot.is_standard = 0
        # on_update auto-creates the linked Raven User for the bot
        bot.insert(ignore_permissions=True)
        return frappe.get_doc("Raven Bot", bot.name)

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Failed to create Raven Bot {}".format(BOT_NAME),
        )
        return None


def _get_targets():
    """Return [(task_dict, project_dict)] for projects with reminders enabled."""

    projects = frappe.get_all(
        "Project Info",
        filters={"enable_task_reminders": 1},
        fields=[
            "name",
            "project_name",
            "project_manager",
            "reminder_days_before_due",
            "reminder_days_after_overdue",
        ],
    )

    if not projects:
        return []

    project_by_name = {p.name: p for p in projects}

    tasks = frappe.get_all(
        "Project Task",
        filters={
            "status": ["!=", "Completed"],
            "project": ["in", list(project_by_name.keys())],
            "due_date": ["is", "set"],
        },
        fields=[
            "name",
            "title",
            "project",
            "assigned_to",
            "due_date",
            "last_reminder_on",
        ],
    )

    return [(task, project_by_name[task.project]) for task in tasks]


def _resolve_assignee(task, project):
    """Use the task assignee, falling back to the project manager.

    The assignee must exist both as a Frappe User and a Raven User so the
    bot can DM them.
    """

    for candidate in (task.get("assigned_to"), project.get("project_manager")):
        if candidate and frappe.db.exists("User", candidate):
            if frappe.db.exists("Raven User", {"user": candidate}):
                return candidate

    return None


def _should_remind(task, project):
    """Decide whether to send a reminder for this task today.

    A task is "not on track" and worth reminding when:
      - its due date is within `reminder_days_before_due` from today, or
      - it is past due and we are on/after the configured re-nudge day
        (`reminder_days_after_overdue` after the last reminder).
    We never send more than one reminder for a task per day.
    """

    due_date = getdate(task.get("due_date"))
    if not due_date:
        return False

    now = getdate(today())

    last_reminder_on = task.get("last_reminder_on")
    if last_reminder_on and getdate(last_reminder_on) == now:
        return False

    days_before = int(project.get("reminder_days_before_due") or 3)
    days_after_overdue = int(project.get("reminder_days_after_overdue") or 1)

    last_sent = getdate(last_reminder_on) if last_reminder_on else None

    # Not yet on track and the reminder window has started
    if add_days(now, days_before) < due_date:
        return False

    if now <= due_date:
        # Upcoming: remind on entering the window, then again only every
        # `days_before` days so we don't spam daily.
        if not last_sent:
            return True
        return now >= add_days(last_sent, days_before)

    # Overdue: re-nudge every `days_after_overdue` days.
    if not last_sent:
        return True
    return now >= add_days(last_sent, days_after_overdue)


def _build_message(task, project):
    """Build the reminder text for a task."""

    due_date = getdate(task["due_date"])
    overdue = getdate(today()) > due_date
    status_word = "OVERDUE" if overdue else "DUE SOON"

    return (
        "<p>⏰ <b>{status}</b></p>"
        "<p>This is an automated reminder that your task is {tone}. "
        "Please update the status or reach out if you are blocked.</p>"
        "<p>Task: <b>{title}</b><br>"
        "Project: <b>{project}</b><br>"
        "Due date: <b>{due_date}</b></p>"
    ).format(
        status=status_word,
        tone="overdue" if overdue else "due soon",
        title=frappe.utils.cstr(task["title"]),
        project=frappe.utils.cstr(project["project_name"]),
        due_date=frappe.utils.cstr(task["due_date"]),
    )
