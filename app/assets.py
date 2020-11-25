# -*- coding: utf-8 -*-
# @Author: zhanglei
# @Time: 2020/6/30 13:32
# @File: assets.py

from flask_assets import Bundle


def compile_static_assets(assets, config_name):
    """
    Compile stylesheets if in development mode.
    :param assets: Flask-Assets Environment
    :type assets: Environment
    """
    assets.auto_build = True
    assets.debug = False
    style_bundle = Bundle(
        'src/less/*.less',
        filters='less,cssmin',
        output='dist/css/style.min.css',
        extra={'rel': 'stylesheet/less'}
    )
    js_bundle = Bundle(
        'src/js/*.js',
        filters='jsmin',
        output='dist/js/main.min.js'
    )
    assets.register('main_styles', style_bundle)
    assets.register('main_js', js_bundle)

    # if config_name == 'development':
    #     style_bundle.build()
    #     js_bundle.build()

    return assets
