from main import *

cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur2 = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute("SELECT text, id FROM posts WHERE searchable_text_version!=%s", [SEARCHABLE_TEXT_VERSION])

for toot in cur:
    print(toot)
    cur2.execute("UPDATE posts SET searchable_text=%s, searchable_text_version=%s where id=%s",[
        convert_searchable_text(toot["text"]),
        SEARCHABLE_TEXT_VERSION,
        toot["id"]
    ])
db.commit()