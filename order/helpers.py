from django.db import connection
from django.db.models import Max
from .models import Order

def next_order_number_sqlite():
    table = Order._meta.db_table
    try:
        with connection.cursor() as cursor:
            # utiliser %s pour les paramètres (Django s'occupe du backend)
            cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = %s", [table])
            row = cursor.fetchone()
    except Exception:
        row = None

    if row and row[0] is not None:
        return row[0] + 1
    # fallback si sqlite_sequence absent
    max_id = Order.objects.aggregate(max_id=Max('id'))['max_id'] or 0
    return max_id + 1