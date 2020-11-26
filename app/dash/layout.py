# -*- coding: utf-8 -*-
# @Author: zhanglei
# @Time: 2020/8/4 16:44
# @File: layout.py

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from datetime import date
from .controls import *
from .utils import *


def get_dash_layout():
    return html.Div(
        [
            dcc.Store(id="aggregate_data", storage_type='session'),
            html.Div(id="output-clientside"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src="",
                                id="plotly-image",
                                style={
                                    "height": "60px",
                                    "width": "auto",
                                    "margin-bottom": "25px",
                                },
                            )
                        ],
                        className="one-third column",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "core的100w期权目标",
                                        style={"margin-bottom": "0px"},
                                    ),
                                ]
                            )
                        ],
                        className="one-half column",
                        id="title",
                    ),
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="name",
                                options=dict_options(NAMES),
                                multi=False,
                                value=list(NAMES.keys())[0],
                                className="dcc_control",
                            ),
                            html.P("支付日期:", className="control_label"),
                            dcc.DatePickerSingle(
                                id='date',
                                min_date_allowed=date(2020, 11, 17),
                                max_date_allowed=date(2030, 12, 31),
                                initial_visible_month=date(2020, 11, 11),
                                date=date.today(),
                                display_format='YYYY-MM-DD',
                            ),
                            html.P("A股/元:", className="control_label"),
                            dcc.Input(
                                id="cn_stock",
                                placeholder="单位/元",
                                className="dcc_control",
                                style={'width': '100%', "display": "block"},
                            ),
                            html.P("港股/港币:", className="control_label"),
                            dcc.Input(
                                id="hk_stock",
                                placeholder="单位/港币",
                                className="dcc_control",
                                style={'width': '100%', "display": "block"},
                            ),
                            html.P("美股/美金:", className="control_label"),
                            dcc.Input(
                                id="us_stock",
                                placeholder="单位/美金",
                                className="dcc_control",
                                style={'width': '100%', "display": "block"},
                            ),
                            html.P("操作:", className="control_label"),
                            dcc.Input(
                                id="op",
                                placeholder="默认输入瞎比操作，牛逼操作#打头",
                                className="dcc_control",
                                style={'width': '100%', "display": "block"},
                            ),
                            html.Button(
                                '更新', id='add', style={"margin-left": '5px', "margin-top": '10px'}
                            ),
                            dcc.Loading(id="loading_run_data", type="default"),
                            dcc.Store(id='df_value', storage_type='memory'),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Store(id='hk', storage_type='memory'),
                                    dcc.Store(id='us', storage_type='memory'),
                                    html.P(id="info"),
                                    dbc.Progress("10000", id='total_progress', value=25, style={"height": "16px"}),
                                ],
                                className="pretty_container",
                            ),
                            html.Div(
                                id="data_table",
                                className="pretty_container",
                            ),
                        ],
                        id="right-column",
                        className="eight columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                dcc.Graph(id="individual-chart", config={"displayModeBar": False}),
                                className="pretty_container",
                            ),
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="choose_name",
                                        options=total_names(NAMES),
                                        multi=False,
                                        value='ALL',
                                        className="dcc_control",
                                    ),
                                    dcc.Graph(id="pie-chart", config={"displayModeBar": False}),
                                ],
                                className="pretty_container",
                            ),
                            html.Div(
                                id="op_table",
                                className="pretty_container",
                            ),
                        ],
                        className="four columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="line-chart")],
                        className="pretty_container eight columns",
                    ),
                ],
                className="row flex-display",
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )
