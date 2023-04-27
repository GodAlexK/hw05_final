from datetime import datetime


real = datetime.today()


def year(request):
    return {
        'year': real.year
    }
