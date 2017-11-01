import main
import threading

hosts = [
    "mstdn.jp",
    "friends.nico",
    "pawoo.net",
    "mstdn.maud.io",
    "imastodon.net"
]

for host in hosts:
    threading.Thread(target=main.logger, args=[host]).start()