# -*- coding: utf-8 -*-
# @Author: zhanglei
# @Time: 2020/6/29 20:41
# @File: wsgi.py

from app import create_app

app = create_app('development')

if __name__ == "__main__":
    app.run(port=8050)
