import copy
import random
from datetime import date, datetime, timedelta

import akshare as ak
import dash
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import db
from app.models.position import Position
from app.models.stock import Stock
from .controls import *
from .layout import get_dash_layout
from .utils import get_daily_fund, get_daily_stock, xfloat, xint, xstr

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    # legend=dict(font=dict(size=10), orientation="h"),
)

colour = ["red","blue","green","yellow","purple","orange","white","black" ]

def create_dash(server):
    app = dash.Dash(
        server=server,
        meta_tags=[{"name": "viewport", "content": "width=device-width"}],
        # routes_pathname_prefix='/stock/'
    )

    # auth = dash_auth.BasicAuth(
    #     app,
    #     VALID_USERNAME_PASSWORD_PAIRS
    # )

    # Create app layout
    app.layout = get_dash_layout()

    @app.callback([Output('date', 'date'), Output('date', 'max_date_allowed'),
                   Output('name', 'value')],
                  Input('title', 'children'))
    def check_date(name):
        username = 'dong'  # request.authorization['username']
        now = datetime.now()
        if now.hour < 11:
            return date.today() + timedelta(-1), date.today(), EN_NAMES[username]
        return date.today(), date.today(), EN_NAMES[username]

    @app.callback([Output('cn_stock', 'value'), Output('hk_stock', 'value'),
                   Output('us_stock', 'value'), Output('fund_stock', 'value'),
                   Output('op', 'value')],
                  [Input('name', 'value'), Input('date', 'date'),
                   Input('cn_s', 'data'), Input('hk_s', 'data'),
                   Input('us_s', 'data'), Input('fund_s', 'data')])
    def check_stock(name, date_value, cn_s, hk_s, us_s, fund_s):
        if date_value is not None:
            date_object = date.fromisoformat(date_value)
            thedate = date_object.strftime('%Y-%m-%d')
            stock = Stock.query.filter(Stock.case_name == "core", Stock.user_name == name,
                                       Stock.thedate == thedate).first()
            cn = stock.cn_stock if stock and xfloat(stock.cn_stock) != 0 else xfloat(cn_s)
            hk = stock.hk_stock if stock and xfloat(stock.hk_stock) != 0 else xfloat(hk_s)
            us = stock.us_stock if stock and xfloat(stock.us_stock) != 0 else xfloat(us_s)
            fund = stock.fund_stock if stock and xfloat(stock.fund_stock) != 0 else xfloat(fund_s)
            op = xstr(stock.op) if stock else ''

            return cn, hk, us, fund, op
        else:
            raise PreventUpdate

    @app.callback([Output('df_value', 'data'), Output("loading_run_data", "children")],
                  [Input('add', 'n_clicks')],
                  [State('name', 'value'), State('date', 'date'),
                   State('cn_stock', 'value'), State('hk_stock', 'value'),
                   State('us_stock', 'value'), State('fund_stock', 'value'),
                   State('op', 'value')])
    def insert_update(click, name, date_value, cn_stock, hk_stock, us_stock, fund_stock, op):
        if date_value is not None:
            date_object = date.fromisoformat(date_value)
            thedate = date_object.strftime('%Y-%m-%d')
            stock = Stock.query.filter(Stock.case_name == "core", Stock.user_name == name,
                                       Stock.thedate == thedate).first()
            if click is not None:
                if stock is None:
                    stock = Stock("core", name, thedate, cn_stock, hk_stock, us_stock, fund_stock, op)
                    stock.save()
                else:
                    stock.cn_stock = xfloat(cn_stock)
                    stock.hk_stock = xfloat(hk_stock)
                    stock.us_stock = xfloat(us_stock)
                    stock.fund_stock = xfloat(fund_stock)
                    stock.op = op
                    stock.updated = datetime.now()
                    stock.update()

            df = pd.read_sql(Stock.query.filter(Stock.case_name == "core")
                             .order_by(Stock.thedate, Stock.user_name).statement, db.session.bind) \
                .drop(columns=['case_name', 'created', 'updated'])
            return df.to_dict('records'), ''
        else:
            raise PreventUpdate

    @app.callback(
        [Output("data_table", "children"), Output("hk", "data"), Output("us", "data"),
         Output("total_progress", "children"),
         Output("total_progress", "value"), Output("info", "children"),
         Output("individual-chart", "figure"), Output('new_df', 'data')],
        [Input('add', 'n_clicks'), Input('df_value', 'data')],
    )
    def fill_data_tab(click, data):
        macro_china_rmb_df = ak.macro_china_rmb()
        arr = macro_china_rmb_df[['美元/人民币_中间价', '港元/人民币_中间价']][-1:].to_numpy()
        us = arr[0][0]
        hk = arr[0][1]

        origin = pd.DataFrame.from_dict(data)
        df = origin.drop(columns=['op'])
        cn_total = df['cn_stock'].sum()
        hk_total = df['hk_stock'].sum() * hk
        us_total = df['us_stock'].sum() * us
        fund_total = df['fund_stock'].sum()
        total = cn_total + hk_total + us_total + fund_total
        df['total'] = round(df['cn_stock'] + df['hk_stock'] * hk + df['us_stock'] * us + df['fund_stock'], 2)
        info = "1/港元 = " + str(hk) + " /元, 1/美元 = " + str(us) + " /元" + ", 总盈利: " + str(round(total, 2)) + \
               ",  100w完成度: " + str(round(total / 10000, 2)) + "%"
        dis, dis_r = total, round(total / 10000, 2)
        if total < 0:
            dis, dis_r = 0, 0

        # 柱状图
        bar_df = df.groupby(["user_name"])['total'].sum().reset_index()
        bar_df.sort_values('total', inplace=True, ascending=[True])
        layout_bar = copy.deepcopy(layout)
        radio_colors = {cat: color for cat, color in zip(NAMES.keys(), COLORS)}

        bar_data = [
            {
                "type": "bar",
                "x": bar_df['total'].values,
                "y": bar_df['user_name'].values,
                "orientation": "h",
                "showlegend": False,
                "marker": {
                    "color": [radio_colors[cat] for cat in bar_df['user_name'].values]
                },
            },
        ]
        layout_bar["height"] = '230'
        bar_fig = dict(data=bar_data, layout=layout_bar)

        d1 = df[['thedate', 'cn_stock', 'hk_stock', 'us_stock', 'fund_stock', 'total', 'user_name']]
        d2 = d1.groupby(["thedate"])['cn_stock', 'hk_stock', 'us_stock', 'fund_stock', 'total'].sum().reset_index()
        d2['user_name'] = 'ALL'
        new_df = pd.concat([d1, d2])
        # new_df['days'] = (pd.to_datetime(new_df['thedate']).dt.date - date(2020, 11, 12)).apply(lambda x: x.days)

        new_df = new_df.groupby(['user_name', "thedate"]).agg({'cn_stock': np.sum, 'hk_stock': np.sum,
                                                               'us_stock': np.sum, 'fund_stock': np.sum,
                                                               'total': np.sum})
        cum_cols = ['cn_stock', 'hk_stock', 'us_stock', 'fund_stock', 'total']
        cumsums = new_df.groupby(level="user_name")[cum_cols].transform(lambda x: round(x.cumsum(), 2))
        new_df.loc[:, cum_cols] = cumsums
        new_df = new_df.reset_index()
        # new_df.sort_values(['thedate', 'user_name'], inplace=True, ascending=[True, True])
        new_df['ratio'] = round(new_df['total'] / 10000, 2)

        join_df = pd.merge(pd.concat([d1, d2]), new_df, on=['thedate', 'user_name'])
        join_df.sort_values(['thedate', 'user_name'], inplace=True, ascending=[False, True])
        join_df['today'] = join_df['total_x'].round(decimals=2)

        tables = [
            dash_table.DataTable(

                columns=[{"name": '日期', "id": 'thedate'}, {"name": '名称', "id": 'user_name'},
                         {"name": 'A股/元', "id": 'cn_stock_x'}, {"name": '港股/港币', "id": 'hk_stock_x'},
                         {"name": '美股/美金', "id": 'us_stock_x'}, {"name": '基金/元', "id": 'fund_stock_x'},
                         {"name": '当日合计/元', "id": 'today'},
                         {"name": '累积合计/元', "id": 'total_y'}, {"name": '进度/%', "id": 'ratio'}],
                data=join_df.to_dict('records'),
                page_action='none',
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{{user_name}} = {}'.format('ALL'),
                        },
                        'backgroundColor': '#4d80e6',
                        'color': 'white'
                    },
                ],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_table={'height': '380px', 'overflowY': 'auto'}
            ),
        ]

        return tables, hk, us, dis, dis_r, info, bar_fig, new_df.to_dict('records')

    @app.callback(
        [Output("line-chart", "figure")],
        [Input('add', 'n_clicks'), Input('choose_stock', 'value'),
         Input('new_df', 'data'), Input("hk", "data"), Input("us", "data")],
    )
    def fill_line_chart(click, stock, data, hk, us):
        new_df = pd.DataFrame.from_dict(data)
        if stock == 'cn':
            new_df['cum'] = new_df['cn_stock']
        elif stock == 'hk':
            new_df['cum'] = new_df['hk_stock'] * hk
        elif stock == 'us':
            new_df['cum'] = new_df['us_stock'] * us
        elif stock == 'fund':
            new_df['cum'] = new_df['fund_stock']
        else:
            new_df['cum'] = new_df['total']

        line_fig = px.line(new_df, x='thedate', y='cum', color="user_name", line_group="user_name", height=380)
        line_fig.update_xaxes(
            tickformat="%m-%d",
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1个月", step="month", stepmode="backward"),
                    dict(count=6, label="6个月", step="month", stepmode="backward"),
                    dict(count=1, label="今年", step="year", stepmode="todate"),
                    dict(count=1, label="近1年", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        line_fig.update_layout(
            showlegend=True,
            # plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            autosize=True,
            margin=dict(t=10, l=10, b=10, r=10),
            legend=dict(orientation="h", title=''),
            xaxis_title='',
            yaxis_title=''
        )

        return [line_fig]

    @app.callback(
        [Output("pie-chart", "figure"), Output("op_table", "children")],
        [Input('add', 'n_clicks'), Input('choose_name', 'value'),
         Input('df_value', 'data'), Input("hk", "data"), Input("us", "data")],
    )
    def fill_data_tab_dynamic(click, name, data, hk, us):
        origin = pd.DataFrame.from_dict(data)
        if name == 'ALL':
            df = origin.drop(columns=['op'])
            ops = origin[(origin['op'].notnull()) & (origin['op'] != '')]
        else:
            df = origin[origin['user_name'] == name].drop(columns=['op'])
            ops = origin[(origin['op'].notnull()) & (origin['op'] != '') & (origin['user_name'] == name)]

        cn_total = df['cn_stock'].sum()
        hk_total = df['hk_stock'].sum() * hk
        us_total = df['us_stock'].sum() * us
        fund_total = df['fund_stock'].sum() * us

        # 饼图
        pie_df = pd.DataFrame([['美股', us_total], ['港股', hk_total], ['A股', cn_total], ['基金', fund_total]], columns=['stock', 'total'])
        layout_pie = copy.deepcopy(layout)
        pie_data = [
            {
                "type": "bar",
                "x": pie_df['total'].values,
                "y": pie_df['stock'].values,
                "orientation": "h",
                "showlegend": False,
                "marker": {
                    "color": ['green', 'cyan', 'red', 'orange']
                },
            },
        ]
        layout_pie["height"] = '150'
        pai_fig = dict(data=pie_data, layout=layout_pie)

        ops['niubility'] = ops['op'].apply(lambda x: '↗️' if x.startswith('#') else '↘️')
        ops['o'] = ops['op'].apply(lambda x: x[1:] if x.startswith('#') else x)
        ops.sort_values(['thedate'], inplace=True, ascending=[True])

        tables = [
            dash_table.DataTable(

                columns=[{"name": '日期', "id": 'thedate'}, {"name": '类型', "id": 'niubility'},
                         {"name": '操作', "id": 'o'}],
                data=ops.to_dict('records'),
                page_action='none',
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{{user_name}} = {}'.format('ALL'),
                        },
                        'backgroundColor': '#4d80e6',
                        'color': 'white'
                    },
                ],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_table={'height': '230px', 'overflowY': 'auto'}
            ),
        ]

        return pai_fig, tables

    @app.callback([Output('hold_value', 'data'), Output("loading_hold_data", "children")],
                  [Input('hold_add', 'n_clicks'), Input('hold_del', 'n_clicks')],
                  [State('name', 'value'), State('hold_category', 'value'),
                   State('hold_code', 'value'), State('hold_num', 'value'),
                   State('hold_price', 'value')])
    def insert_stock(add, delete, name, category, code, num, price):
        ctx = dash.callback_context
        button = ctx.triggered[0]['prop_id'].split('.')[0]

        if add is not None and button == 'hold_add' and code:
            code = code.upper()
            position = Position.query.filter(Position.case_name == "core", Position.user_name == name,
                                             Position.hold_code == code).first()
            if position is None:
                position = Position("core", name, category, code, xfloat(num), xfloat(price))
                position.save()
            else:
                position.hold_category = category
                position.hold_num = xfloat(num)
                position.hold_price = xfloat(price)
                position.updated = datetime.now()
                position.update()
        elif delete is not None and button == 'hold_del' and code:
            code = code.upper()
            position = Position.query.filter(Position.case_name == "core", Position.user_name == name,
                                             Position.hold_code == code).first()
            if position is not None:
                position.delete()

        df = pd.read_sql(Position.query.filter(Position.case_name == "core")
                         .order_by(Position.user_name).statement, db.session.bind) \
            .drop(columns=['case_name', 'created', 'updated'])
        return df.to_dict('records'), ''

    @app.callback(
        [Output("hold_table", "children"), Output("hold_info", "children"), Output('daily-chart', 'figure'),
         Output("fund_s", "data"), Output("cn_s", "data"), Output("hk_s", "data"), Output("us_s", "data")],
        [Input('hold_add', 'n_clicks'), Input('hold_del', 'n_clicks'), Input('name', 'value'),
         Input('hold_value', 'data'), Input("hk", "data"), Input("us", "data")],
    )
    def fill_hold_table(add, delete, name, data, hk, us):
        origin = pd.DataFrame.from_dict(data)
        df = origin[origin['user_name'] == name].drop(columns=['user_name'])
        if len(df) == 0:
            return None, name + ", 输入一下你的持仓情况", None, 0, 0, 0, 0

        df[['name', 'y', 't', 'ratio', 'category']] = \
            df[["hold_category", "hold_code"]].apply(lambda x: pd.Series(get_daily_fund(x['hold_code'])
               if x['hold_category'] == 'fund' else get_daily_stock(x['hold_code'])), axis=1)

        df['today_gain'] = df[["category", "t", "y", "hold_num"]].apply(
            lambda x: round((x['t'] - x['y']) * x['hold_num'], 2)
            if x['category'] == 'cn' else (round((x['t'] - x['y']) * x['hold_num'], 2)) if x['category'] == 'us'
            else round((x['t'] - x['y']) * x['hold_num'], 2), axis=1)
        df['total_gain'] = df[["category", "t", "hold_price", "hold_num"]].apply(
            lambda x: round((x['t'] - x['hold_price']) * x['hold_num'], 2)
            if x['category'] == 'cn' else (round((x['t'] - x['hold_price']) * x['hold_num'] * us, 2)) if x['category'] == 'us'
            else round((x['t'] - x['hold_price']) * x['hold_num'] * hk, 2), axis=1)
        df['total_ratio'] = df[["t", "hold_price"]].apply(lambda x: round(((x['t'] / x['hold_price']) - 1) * 100, 2), axis=1)

        tables = [
            dash_table.DataTable(
                columns=[{"name": '代码', "id": 'hold_code'}, {"name": '名称', "id": 'name'},
                         {"name": '当前价', "id": 't'}, {"name": '日收益率/%', "id": 'ratio'},
                         {"name": '日收益', "id": 'today_gain'},
                         {"name": '总收益率/%', "id": 'total_ratio'}, {"name": '累积收益/元', "id": 'total_gain'},
                         {"name": '数量', "id": 'hold_num'}, {"name": '持仓成本', "id": 'hold_price'},],
                data=df.sort_values(['hold_category', 'hold_code'], ascending=[True, True]).to_dict('records'),
                page_action='none',
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{ratio} > 0',
                            'column_id': 'ratio'
                        },
                        'color': 'red',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': '{ratio} < 0',
                            'column_id': 'ratio'
                        },
                        'color': 'green',
                        'fontWeight': 'bold'
                    },
                ],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_table={'height': '320px', 'overflowY': 'auto'},
                # style_data={
                #     'whiteSpace': 'normal',
                #     'height': 'auto',
                #     'lineHeight': '20px'
                # },
            ),
        ]

        now = datetime.now()
        d = date.today() if now.hour < 11 else date.today() + timedelta(-1)
        today_gain = df.groupby(["category"])['today_gain'].sum().to_dict()
        [fund_s, cn_s, hk_s, us_s] = [today_gain.get(k, 0) for k in ('fund', 'cn', 'hk', 'us')]
        info = name + ", " + str(d) + "盈利统计: 基金 = " + str(fund_s) + ", A股 = " + str(cn_s) \
               + ", 港股 = " + str(hk_s) + ", 美股 = " + str(us_s)

        # 累积盈利图
        bar_df = copy.deepcopy(df)
        bar_df.sort_values('total_gain', inplace=True, ascending=[True])
        layout_bar = copy.deepcopy(layout)

        bar_data = [
            {
                "type": "bar",
                "x": bar_df['total_gain'].values,
                "y": bar_df['name'].values,
                "orientation": "h",
                "showlegend": False,
                "marker": {
                    "color": [random.choice(colour) for i in range(len(bar_df))]
                },
            },
        ]
        layout_bar["height"] = '230'
        layout_bar['margin'] = dict(l=150, r=30, b=20, t=40)
        bar_fig = dict(data=bar_data, layout=layout_bar)

        return tables, info, bar_fig, fund_s, cn_s, hk_s, us_s

    return app.server

