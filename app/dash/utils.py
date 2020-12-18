# -*- coding: utf-8 -*-
# @Author: zhanglei
# @Time: 2020/8/4 16:46
# @File: utils.py

import requests
import json


def dict_options(dict):
    return [
        {"label": str(dict[k]), "value": str(k)}
        for k in dict
    ]


def total_names(dict):
    d = dict_options(dict)
    d.append({"label": "ALL", "value": "ALL"})
    return d


def dict_options_s(dict):
    return [
        {"label": str(k), "value": str(k)}
        for k in dict
    ]


def dict_options_l(list):
    return [
        {"label": str(k[0]), "value": str(k[0])}
        for k in list
    ]


def get_daily_fund(code):
    fund_daily_req = requests.get('http://fundgz.1234567.com.cn/js/' + code + '.js')
    fund_daily = json.loads(fund_daily_req.text.lstrip('jsonpgz(').strip(');'))
    name = fund_daily['name']  # 基金名称
    y = fund_daily['dwjz']  # 昨日净值2.0321
    t = fund_daily['gsz']  # 今日净值2.0412
    ratio = fund_daily['gszzl']  # 增长比例0.45

    return name, float(y), float(t), ratio, 'fund'


def get_daily_stock(code):
    if not code.isnumeric():
        stock_daily_req = requests.get('http://hq.sinajs.cn/list=gb_' + code.lower())
        res = stock_daily_req.text.split('"')[1].split(',')
        name, y, t, category = res[0], res[26], res[1], 'us'
    elif len(code) <= 5:
        stock_daily_req = requests.get('http://hq.sinajs.cn/list=hk' + code)
        res = stock_daily_req.text.split('"')[1].split(',')
        name, y, t, category = res[1], res[3], res[4], 'hk'
    elif code.startswith('6'):
        stock_daily_req = requests.get('http://hq.sinajs.cn/list=sh' + code)
        res = stock_daily_req.text.split('"')[1].split(',')
        name, y, t, category = res[0], res[2], res[3], 'cn'
    else:
        stock_daily_req = requests.get('http://hq.sinajs.cn/list=sz' + code)
        res = stock_daily_req.text.split('"')[1].split(',')
        name, y, t, category = res[0], res[2], res[3], 'cn'

    ratio = round((float(t) / float(y) - 1) * 100, 2)
    return name, float(y), float(t), ratio, category


def xstr(s):
    return '' if s is None else str(s)


def xint(s):
    return 0 if not s else int(s)


def xfloat(s):
    return 0 if not s else float(s)