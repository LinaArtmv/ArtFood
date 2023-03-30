from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    dt = datetime.today()
    return {
        'year': dt.year
    }
