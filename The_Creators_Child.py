import praw
import pdb
import re
import os
import config
import time
from REACTIONS import REACTANTS, REACTIONS

_cycle = 'alchemy1'
_resources = set()

if not os.path.isfile("cycle.txt"):
    _cycle = 'alchemy1'
else:
    with open("cycle.txt", "r") as f:
       _cycle = f.read()

if not os.path.isfile("resources.txt"):
    _resources = {'matter', 'life', 'intelligence'}
else:
    with open("resources.txt", "r") as f:
       resources = f.read()
       resources = resources.split("\n")
       resources = list(filter(None, resources))
       _resources = set()
       for i in resources:
           _resources |= {i}

reddit = praw.Reddit('bot1')

if not os.path.isfile("posts_seen.txt"):
    posts_seen = []
else:
    with open("posts_seen.txt", "r") as f:
       posts_seen = f.read()
       posts_seen = posts_seen.split("\n")
       posts_seen = list(filter(None, posts_seen))

subreddit = reddit.subreddit(config.sub)

def sortScore(val):
    return val.score
    
def parseComment(comment):
    step1 = re.search(r'!([a-z]*)(( ?\+ ?)([a-z]*))+!', comment.body, re.I)
    if step1:
        step2 = step1.group()[1:-1]
        step3 = re.split(r' ?\+ ?', step2, 0, re.I)
        return step3
    else:
        return

def updateAlchemy():
    global _resources
    posts = filter(lambda x: x.author.id == '97b31x8' or x.author.id == '3hpqioem', subreddit.new(limit=config.activity))
    post = []
    for submission in posts:
        if submission.id not in posts_seen:
            post = post + [submission]
    if post is not []:
        post = post[0]
    else:
        return
    post.comments.replace_more(limit=None)
    top5 = post.comments.list()
    top5 = list(filter(parseComment, top5))
    top5.sort(key=sortScore, reverse=True)
    top5 = top5[0:5]
    react5 = post.selftext
    for piece in top5:
        react = parseComment(piece)
        react.sort()
        exp = ""
        for n in react:
            if n in _resources:
                exp += n
            else:
                exp += '!ERROR!'
        if exp in REACTIONS:
            react5 += '\n\nCongratulations, u/' + piece.author.name + '! You have created ' + REACTIONS[exp] + '.'
            _resources |= {REACTIONS[exp]}            
        else:
            react5 += '\n\nu/' + piece.author.name + "'s reaction was a failure."
    react5 += '\n\n*See comments for more details.*'
    post.edit(react5)
def updateBasic():
    pass

def switch():
    p = subreddit.submit('Switch cycles?', selftext='', send_replies=False)
    p.reply('Yes')
    p.reply('No')
    p.mod.lock()

def update(cycle):
    if swap:
        if _cycle == 'alchemy2':
            cycle = 'basic'
        elif _cycle == 'basic':
            cycle = 'alchemy1'
    else:
        if _cycle == 'alchemy2':
            cycle = 'alchemy1'
        elif _cycle == 'alchemy1':
            cycle = 'alchemy2'
    
    if cycle == 'alchemy2':
        updateAlchemy()
        switch()
    elif cycle == 'alchemy1':
        st = ''
        for i in _resources:
            st += i + '\n\n'
        post(cycle, st)
    elif cycle == 'basic':
        updateBasic()
        switch()
    return cycle

def post(cycle, selfText):
    if cycle == 'basic':
        cycstr = 'Resources for generation on'
    elif cycle == 'alchemy1':
        cycstr = 'Resources for alchemy on'
    else:
        return
    t = time.strftime(cycstr + ' %a, %d %b 20%y', time.localtime())
    st = selfText
    fid = None
    subreddit.submit(t, selftext=st, flair_id=fid, send_replies=False)

def readPost(post, cycle):
    if (post.author.id == '97b31x8' or post.author.id == '3hpqioem') and re.fullmatch("next", submission.title, re.IGNORECASE):
        posts_seen.append(post.id)
        foo = update(cycle)
        return foo
    else:
        return cycle


swap = False

if _cycle == 'alchemy2' or _cycle == 'basic':
    for i in subreddit.new(limit=config.activity):
        if i.id not in posts_seen and i.title == 'Switch cycles?':
            posts_seen.append(i.id)
            i.comment_sort = 'top'
            for c in i.comments:
                if c.body == 'Yes':
                    swap = True
                break

if config.mode == 'debug':
    for submission in subreddit.new(limit=config.activity):
        if submission.id not in posts_seen:
            c = readPost(submission, _cycle)
            _cycle = c
else:
    _cycle = update(_cycle)

with open("posts_seen.txt", "w") as f:
    for post_id in posts_seen:
        f.write(post_id + "\n")

with open("cycle.txt", "w") as f:
    f.write(_cycle)

with open("resources.txt", "w") as f:
    for resource in _resources:
        f.write(resource + "\n")
