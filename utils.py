from main import db, psycopg2, convert_searchable_text
def search(input_words):
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "SELECT text, instance, screen_name FROM posts WHERE true"
    args = []
    for arg in input_words:
        if arg.startswith("instance:"):
            sql += " AND instance=%s"
            args.append(arg[9:])
        else:
            sql += " AND searchable_text LIKE %s"
            args.append("%"+convert_searchable_text(arg)+"%")
    sql += "ORDER BY created_at DESC LIMIT 1000"
    cur.execute(sql, args)
    return cur