from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔎 Search", callback_data="menu:search"),
             InlineKeyboardButton("🎯 Filters", callback_data="menu:filters")],
            [InlineKeyboardButton("↕️ Sort", callback_data="menu:sort"),
             InlineKeyboardButton("⭐ Saved Jobs", callback_data="menu:saved")],
            [InlineKeyboardButton("📋 Show Results", callback_data="menu:results")],
            [InlineKeyboardButton("🤖 Find a Job That Fits Me", callback_data="menu:similar")],
            [InlineKeyboardButton("🗑 Clear All Filters", callback_data="menu:clear")],
        ]
    )


def filters_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💼 Job Type", callback_data="menu:jobtype"),
             InlineKeyboardButton("📍 Location", callback_data="filter:ask:location")],
            [InlineKeyboardButton("💰 Min Salary", callback_data="filter:ask:min_salary"),
             InlineKeyboardButton("💰 Max Salary", callback_data="filter:ask:max_salary")],
            [InlineKeyboardButton("🕒 Date Posted", callback_data="menu:posted"),
             InlineKeyboardButton("🎓 Experience", callback_data="menu:experience")],
            [InlineKeyboardButton("🏠 Work Type", callback_data="menu:remote"),
             InlineKeyboardButton("🔥 Actively Hiring?", callback_data="menu:hiring")],
            [InlineKeyboardButton("⬅️ Back", callback_data="menu:main")],
        ]
    )


def jobtype_menu_keyboard() -> InlineKeyboardMarkup:
    options = [
        ("Full-time", "Full-time"),
        ("Part-time", "Part-time"),
        ("Contract", "Contract"),
        ("Internship", "Internship"),
        ("Freelance", "Freelance"),
    ]
    rows = [[InlineKeyboardButton(label, callback_data=f"filter:job_type:{value}")] for label, value in options]
    rows.append([InlineKeyboardButton("Clear This Filter", callback_data="filter:job_type:")])
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="menu:filters")])
    return InlineKeyboardMarkup(rows)


def posted_menu_keyboard() -> InlineKeyboardMarkup:
    options = [
        ("Today", "today"),
        ("Last 3 Days", "last_3_days"),
        ("Last Week", "last_week"),
        ("Last Month", "last_month"),
    ]
    rows = [[InlineKeyboardButton(label, callback_data=f"filter:posted:{value}")] for label, value in options]
    rows.append([InlineKeyboardButton("Clear This Filter", callback_data="filter:posted:")])
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="menu:filters")])
    return InlineKeyboardMarkup(rows)


def experience_menu_keyboard() -> InlineKeyboardMarkup:
    options = [("Entry", "entry"), ("Mid", "mid"), ("Senior", "senior"), ("Staff", "staff")]
    rows = [[InlineKeyboardButton(label, callback_data=f"filter:experience_level:{value}")] for label, value in options]
    rows.append([InlineKeyboardButton("Clear This Filter", callback_data="filter:experience_level:")])
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="menu:filters")])
    return InlineKeyboardMarkup(rows)


def remote_menu_keyboard() -> InlineKeyboardMarkup:
    options = [
        ("Remote Only", "remote_only"),
        ("Onsite Only", "onsite_only"),
        ("Both", "remote_and_onsite"),
    ]
    rows = [[InlineKeyboardButton(label, callback_data=f"filter:remote:{value}")] for label, value in options]
    rows.append([InlineKeyboardButton("Clear This Filter", callback_data="filter:remote:")])
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="menu:filters")])
    return InlineKeyboardMarkup(rows)


def hiring_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Yes, Actively Hiring", callback_data="filter:actively_hiring:true")],
            [InlineKeyboardButton("Doesn't Matter", callback_data="filter:actively_hiring:")],
            [InlineKeyboardButton("⬅️ Back", callback_data="menu:filters")],
        ]
    )


def sort_menu_keyboard() -> InlineKeyboardMarkup:
    options = [
        ("🆕 Newest First", "newest"), ("📅 Oldest First", "oldest"),
        ("💰 Salary: High to Low", "salary_high"), ("💰 Salary: Low to High", "salary_low"),
        ("🔤 Company: A-Z", "company_asc"), ("🔤 Company: Z-A", "company_desc"),
        ("🎯 Best Match", "relevance"),
    ]
    rows = [[InlineKeyboardButton(label, callback_data=f"sort:{value}")] for label, value in options]
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def job_save_keyboard(rowid: int, job_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔗 View Job",
                    url=job_link
                ),
                InlineKeyboardButton(
                    "⭐ Save",
                    callback_data=f"save:{rowid}"
                )
            ]
])

def job_saved_keyboard(rowid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "✅ Saved",
                callback_data=f"saved:{rowid}"
            )
        ]]
    )


def load_more_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬇️ Load More Jobs", callback_data="results:more")],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data="menu:main")],
        ]
    )


def format_job(job: dict) -> str:
    salary = ""
    if job.get("min_salary") and job.get("max_salary"):
        salary = f"\n💰 {job['min_salary']:.0f} - {job['max_salary']:.0f} {job.get('currency') or ''}"
    return (
        f"*{job['title']}*\n"
        f"🏢 {job['company']}\n"
        f"📍 {job.get('location') or 'Not specified'}"
        f"{salary}\n"
        f"🕒 {job.get('posted') or 'Not specified'}" 

    )


def format_similar_job(job: dict) -> str:
    salary = ""
    if job.get("min_salary") and job.get("max_salary"):
        salary = f"\n💰 {job['min_salary']:.0f} - {job['max_salary']:.0f} {job.get('currency') or ''}"
    return (
        f"🎯 Match: *{job['match_percentage']}%*\n"
        f"*{job['title']}*\n"
        f"🏢 {job['company']}\n"
        f"📍 {job.get('location') or 'Not specified'}\n"
        f"{salary}"


    )


def notifications_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔔 Enable Notifications",
                    callback_data="notifications:on"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔕 No, thanks",
                    callback_data="notifications:off"
                )
            ],
        ]
    )


