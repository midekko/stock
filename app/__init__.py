# -*- encoding: utf-8 -*-
"""
    程序主目录
"""

from flask import Flask
from flask_assets import Environment
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()


def create_app(config_name, extra_config_settings=None):
    app = Flask('core')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    if extra_config_settings is not None:
        app.config.update(extra_config_settings)

    assets = Environment()
    assets.init_app(app)

    with app.app_context():
        # init app
        db.init_app(app)
        db.create_all()

        # from .views import register_blueprints
        # register_blueprints(app)

        # Import parts of our core Flask app

        # Import Dash application

        from .dash.dashboard import create_dash
        app = create_dash(app)

        # Compile static assets
        from .assets import compile_static_assets
        compile_static_assets(assets, config_name)

        return app
