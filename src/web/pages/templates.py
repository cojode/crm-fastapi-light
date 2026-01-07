from fastapi.templating import Jinja2Templates

from src.settings import settings

templates = Jinja2Templates(directory=settings.jinja2_templates_path)


def datetimeformat(value, format="%H:%M %d.%m.%Y"):
    if value is None:
        return ""
    return value.strftime(format)


templates.env.filters["datetimeformat"] = datetimeformat
