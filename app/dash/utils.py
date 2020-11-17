# -*- coding: utf-8 -*-
# @Author: zhanglei
# @Time: 2020/8/4 16:46
# @File: utils.py


def dict_options(dict):
    return [
        {"label": str(dict[k]), "value": str(k)}
        for k in dict
    ]


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
