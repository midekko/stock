# -*- encoding: utf-8 -*-
"""
    project config
"""

import os

basedir = os.path.abspath(os.path.dirname(__file__))  # 设置基础目录


class Config(object):
    # 配置基础类
    FLASK_APP = 'causal'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'TxuvWdN[PYOB2V0yMGn5q4Fk'
    LESS_BIN = '/usr/local/bin/lessc'
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # 取消这个报警信息

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    # 开发类
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:12332100@localhost:3306/core?charset=utf8mb4'
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = ''  # 替换线上的链接
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
