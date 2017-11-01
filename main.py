import json
import re
import requests
import psycopg2
import psycopg2.extras
import threading
import datetime
import dateutil.parser
import traceback
import html
import unicodedata
import time
import sys

USER_AGENT="searchdon_crawler/0.1 (+https://mstdn.maud.io/@rinsuki)"

SEARCHABLE_TEXT_VERSION=9

html_re = re.compile('<(.+?)>')

def convert_searchable_text(text):
    # remove html tag
    text = html_re.sub("", text)
    # remove html escape
    text = html.unescape(text)
    # unicode normalize
    text = unicodedata.normalize("NFKD", text)
    # delete 濁音と半濁音
    text = text.replace("\u309A", "").replace("\u3099", "")
    # lowercase
    text = text.lower()
    return text

db=psycopg2.connect("host=localhost port=5432 dbname=mastodon_search user=postgres")

# print(db)

def get_ltl_api(host, params={}):
    params["local"] = "true"
    url="https://{0}/api/v1/timelines/public".format(host)
    cur = db.cursor()
    cur.execute("INSERT INTO request_logs (host, url, params, requested_at) VALUES (%s, %s, %s, %s)", [
        host,
        url,
        json.dumps(params),
        datetime.datetime.now()
    ])
    t = requests.get(url,params=params, headers={
        "User-Agent": USER_AGENT
    }).json()
    return t

def new_toot(toot, host):
    try:
        cur = db.cursor()
        cur.execute("INSERT INTO posts (id, json, text, searchable_text, searchable_text_version, instance, screen_name, instance_id, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", [
            host+":"+str(toot["account"]["id"])+":"+str(toot["id"]),
            json.dumps(toot),
            toot.get("content", ""),
            convert_searchable_text(toot.get("content", "")),
            SEARCHABLE_TEXT_VERSION,
            host,
            toot["account"]["username"],
            toot["id"],
            dateutil.parser.parse(toot["created_at"])
        ])
        db.commit()
        print(toot)
    except psycopg2.IntegrityError:
        pass
    except psycopg2.InternalError:
        pass
    except:
        traceback.print_exc()
        pass
def logger(host):
    while True:
        latest_id_cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        latest_id_cur.execute("SELECT instance_id FROM posts WHERE instance=%s ORDER BY instance_id DESC", [host])
        latest_id = (latest_id_cur.fetchone() or {}).get("instance_id")
        if latest_id == None:
            latest_id = get_ltl_api(host, {
                "limit": 10
            })[-1]["id"]
        print(latest_id)
        max_id=None
        while True:
            limit=40
            t = get_ltl_api(host, {
                "since_id": latest_id,
                "max_id": max_id,
                "limit": limit
            })
            if len(t) == 0:
                break
            for toot in t:
                new_toot(toot, host)
            if len(t) < limit:
                break
            max_id = t[-1]["id"]
            if latest_id == max_id:
                break
            print(len(t), latest_id)
            time.sleep(3)
        time.sleep(60)
if __name__ == "__main__":
    logger(sys.argv[1])