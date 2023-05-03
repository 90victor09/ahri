
def is_table_exists(conn, tablename):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM information_schema.tables WHERE table_name=%s", (tablename,))
        return bool(cursor.rowcount)
