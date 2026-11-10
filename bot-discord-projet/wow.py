
from random import *


vid = ["https://youtu.be/el4CQj-TCbA",
        "https://youtu.be/a5V6gdu5ih8",
        "https://youtu.be/xg79mkbNaTg",
        "https://youtu.be/PvWLbK_mNw0",
        "https://youtu.be/rxGuNJ-nEYg",
        "https://youtu.be/hn_1Rr5Rzf8",
        "https://youtu.be/bk7McNUjWgw",
        "https://youtu.be/WCcLMNcWZOc",
        "https://youtu.be/7wKu13wmHog",
        "https://youtu.be/1-q_8TKNG9w",
        "https://youtu.be/py0wRutmMF4"
        ]
used = []
def choix()->str:
    """Renvoie une vidéo incroyable"""
    choix = choice(vid)
    used.append(choix)
    vid.remove(choix)
    if len(vid) == 0:
        vid.extend(used)
        used.clear()
    return choix
