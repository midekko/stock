from datetime import date
from datetime import datetime

import numpy as np
import akshare as ak
import copy
import dash
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from .controls import *
import plotly.express as px

from app import db
from app.models.stock import Stock
from .layout import get_dash_layout


layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    # legend=dict(font=dict(size=10), orientation="h"),
)


def create_dash(server):
    app = dash.Dash(
        server=server,
        meta_tags=[{"name": "viewport", "content": "width=device-width"}],
       # routes_pathname_prefix='/stock/'
    )

    # Create app layout
    app.layout = get_dash_layout()

    @app.callback([Output('date', 'date'), Output('date', 'max_date_allowed')],
                  Input('name', 'value'))
    def check_date(name):
        return [date.today(), date.today()]

    @app.callback([Output('cn_stock', 'value'), Output('hk_stock', 'value'), Output('us_stock', 'value')],
                  [Input('name', 'value'), Input('date', 'date')])
    def check_stock(name, date_value):
        if date_value is not None:
            date_object = date.fromisoformat(date_value)
            thedate = date_object.strftime('%Y-%m-%d')
            stock = Stock.query.filter(Stock.case_name == "core", Stock.user_name == name,
                                       Stock.thedate == thedate).first()
            if stock is not None:
                return stock.cn_stock, stock.hk_stock, stock.us_stock
            else:
                return 0, 0, 0
        else:
            raise PreventUpdate

    @app.callback([Output('df_value', 'data'), Output("loading_run_data", "children")],
                  [Input('add', 'n_clicks')],
                  [State('name', 'value'), State('date', 'date'),
                   State('cn_stock', 'value'), State('hk_stock', 'value'), State('us_stock', 'value')])
    def insert_update(click, name, date_value, cn_stock, hk_stock, us_stock):
        if date_value is not None:
            date_object = date.fromisoformat(date_value)
            thedate = date_object.strftime('%Y-%m-%d')
            stock = Stock.query.filter(Stock.case_name == "core", Stock.user_name == name,
                                       Stock.thedate == thedate).first()
            if click is not None:
                if stock is None:
                    stock = Stock("core", name, thedate, cn_stock, hk_stock, us_stock)
                    stock.save()
                else:
                    stock.cn_stock = xint(cn_stock)
                    stock.hk_stock = xint(hk_stock)
                    stock.us_stock = xint(us_stock)
                    stock.updated = datetime.now()
                    stock.update()

            df = pd.read_sql(Stock.query.filter(Stock.case_name == "core")
                             .order_by(Stock.thedate, Stock.user_name).statement, db.session.bind) \
                .drop(columns=['case_name', 'created', 'updated'])
            return df.to_dict('records'), ''
        else:
            raise PreventUpdate


    @app.callback(
        [Output("data_table", "children"), Output("hk", "data"), Output("us", "data"), Output("total_progress", "children"),
         Output("total_progress", "value"), Output("info", "children"),
         Output("pie-chart", "figure"), Output("individual-chart", "figure"), Output("line-chart", "figure")],
        [Input('add', 'n_clicks'), Input('df_value', 'data')],
    )
    def fill_data_tab(click, data):
        macro_china_rmb_df = ak.macro_china_rmb()
        arr = macro_china_rmb_df[['美元/人民币_中间价', '港元/人民币_中间价']][-1:].to_numpy()
        us = arr[0][0]
        hk = arr[0][1]

        df = pd.DataFrame.from_dict(data)
        cn_total = df['cn_stock'].sum()
        hk_total = df['hk_stock'].sum() * hk
        us_total = df['us_stock'].sum() * us
        total = cn_total + hk_total + us_total
        df['total'] = round(df['cn_stock'] + df['hk_stock'] * hk + df['us_stock'] * us, 2)
        info = "1/港元 = " + str(hk) + " /元, 1/美元 = " + str(us) + " /元" + ", 总盈利: " + str(round(total, 2)) + \
               ",  100w完成度: " + str(round(total / 10000, 2)) + "%"
        dis, dis_r = total, round(total / 10000, 2)
        if total < 0:
            dis, dis_r = 0, 0

            # 饼图
        pie_df = pd.DataFrame([['A股', cn_total], ['港股', hk_total], ['美股', us_total]], columns=['stock', 'total'])
        layout_pie = copy.deepcopy(layout)
        pie_data = [
            dict(
                type="pie",
                labels=pie_df['stock'].to_numpy(),
                values=pie_df['total'].to_numpy(),
            ),
        ]
        layout_pie["height"] = '200'
        pai_fig = dict(data=pie_data, layout=layout_pie)

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
        layout_bar["height"] = '200'
        bar_fig = dict(data=bar_data, layout=layout_bar)

        d1 = df[['thedate', 'cn_stock', 'hk_stock', 'us_stock', 'total', 'user_name']]
        d2 = d1.groupby(["thedate"])['cn_stock', 'hk_stock', 'us_stock', 'total'].sum().reset_index()
        d2['user_name'] = 'ALL'
        new_df = pd.concat([d1, d2])
        # new_df['days'] = (pd.to_datetime(new_df['thedate']).dt.date - date(2020, 11, 12)).apply(lambda x: x.days)

        new_df = new_df.groupby(['user_name', "thedate"]).agg({'cn_stock': np.sum, 'hk_stock': np.sum,
                                                               'us_stock': np.sum, 'total': np.sum})
        cum_cols = ['cn_stock', 'hk_stock', 'us_stock', 'total']
        cumsums = new_df.groupby(level="user_name")[cum_cols].transform(lambda x: round(x.cumsum(), 2))
        new_df.loc[:, cum_cols] = cumsums
        new_df = new_df.reset_index()
        # new_df.sort_values(['thedate', 'user_name'], inplace=True, ascending=[True, True])
        new_df['ratio'] = round(new_df['total'] / 10000, 2)

        line_fig = px.line(new_df, x='thedate', y='total', color="user_name", line_group="user_name", height=400)
        line_fig.update_xaxes(
            tickformat="%Y-%m-%d",
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1个月", step="month", stepmode="backward"),
                    dict(count=6, label="6个月", step="month", stepmode="backward"),
                    dict(count=1, label="今年", step="year", stepmode="todate"),
                    dict(count=1, label="近1年", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
        )
        line_fig.update_layout(paper_bgcolor="#F9F9F9")

        join_df = pd.merge(pd.concat([d1, d2]), new_df, on=['thedate', 'user_name'])
        join_df.sort_values(['thedate', 'user_name'], inplace=True, ascending=[False, True])
        join_df['today']=join_df['total_x'].round(decimals=2)
    
        tables = [
            dash_table.DataTable(

                columns=[{"name": '日期', "id": 'thedate'}, {"name": '名称', "id": 'user_name'},
                         {"name": 'A股/元', "id": 'cn_stock_x'}, {"name": '港股/港币', "id": 'hk_stock_x'},
                         {"name": '美股/美金', "id": 'us_stock_x'}, {"name": '当日合计/元', "id": 'today'},
                         {"name": '累积合计/元', "id": 'total_y'}, {"name": '进度/%', "id": 'ratio'}],
                data=join_df.to_dict('records'),
                page_action='none',
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    # {
                    #     'if': {'row_index': 'odd'},
                    #     'backgroundColor': 'rgb(248, 248, 248)'
                    # },
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
                style_table={'height': '350px', 'overflowY': 'auto'}
            ),
        ]

        return tables, hk, us, dis, dis_r, info, pai_fig, bar_fig, line_fig

    return app.server


def xstr(s):
    return '' if s is None else str(s)


def xint(s):
    return 0 if not s else int(s)
