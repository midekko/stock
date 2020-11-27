# flake8: noqa

# In[]:
# Controls for webapp

NAMES = {
    "栋哥": "栋哥",
    "P总": "P总",
    "贤哥": "贤哥",
    "表哥": "表哥",
    "萌萌": "萌萌",
    "渔歌": "渔歌",
}

COLORS = ["green", "blue", "orange", "red", "cyan", "gray"]

EN_NAMES = {
    "dong": "栋哥",
    "ppl": "P总",
    "xian": "贤哥",
    "lei": "表哥",
    "meng": "萌萌",
    "yu": "渔歌",
}

VALID_USERNAME_PASSWORD_PAIRS = dict([(k, 'core') for k in EN_NAMES.keys()])
