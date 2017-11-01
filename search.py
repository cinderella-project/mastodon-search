import sys
import utils
cur = utils.search(sys.argv[1:])
for toot in cur:
    print(toot["screen_name"]+"@"+toot["instance"],toot["text"])