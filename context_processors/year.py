from datetime import datetime

def get_year(request):
    return {
        'year': datetime.now().year,
        }
