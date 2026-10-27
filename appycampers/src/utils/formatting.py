def format_camp_date(value):
    if not value:
        return ""
    return f"{value.strftime('%b')} {value.day}, {value.year}"
