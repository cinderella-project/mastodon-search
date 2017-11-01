from main import get_ltl_api, db, psycopg2, new_toot
import sys
import time

host = sys.argv[1]

max_id_cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
max_id_cur.execute("SELECT instance_id FROM posts WHERE instance=%s ORDER BY instance_id ASC", [host])
db.commit()
max_id = (max_id_cur.fetchone() or {}).get("instance_id")

if max_id is None:
    exit(1)
while True:
    limit = 40
    t = get_ltl_api(host, {
        "max_id": max_id,
        "limit": limit,
    })
    for toot in t:
        new_toot(toot, host)
        db.commit()
    print(len(t))
    if len(t) < limit:
        break
    max_id = t[-1]["id"]
    time.sleep(limit*1.5)