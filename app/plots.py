import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json
import os

from collections import defaultdict

def create_plot():
    """

    :return:
    """
    N = 40
    x = np.linspace(0, 1, N)
    y = np.random.randn(N)
    df = pd.DataFrame({'x': x, 'y': y})  # creating a sample dataframe

    data = [
        go.Bar(
            x=df['x'],  # assign x as the dataframe column 'x'
            y=df['y']
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def generate_files(temp):
    # General el JSON del grafico

    data = [
        go.Scatter(
            x=temp.iloc[:, 0],  # assign x as the dataframe column 'x'
            y=temp.iloc[:, 1],
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    # generar JSON para la tabla

    estadisticas = {
        'Máximo': int(temp.iloc[:, 1].max()),
        'Media': int(temp.iloc[:, 1].mean()),
        'Desviación Std': int(temp.iloc[:, 1].std()),
        'Percentil 90': int(temp.iloc[:, 1].quantile(0.9)),
    }

    table_html_pd = pd.DataFrame(estadisticas, index=['-'])
    table_html = table_html_pd.to_html(classes='table', header="true")

    return graphJSON, table_html, table_html_pd


def unidades_dia(data):
    temp = pd.DataFrame(data.groupby('Fecha')['Cantidad'].sum()).reset_index()

    return *generate_files(temp),temp


def lineas_dia(data):
    temp = pd.DataFrame(data.groupby('Fecha')['Cantidad'].count()).reset_index()

    return *generate_files(temp),temp


def sku_dia(data):
    temp = pd.DataFrame(data.groupby('Fecha')['SKU'].nunique()).reset_index()

    return *generate_files(temp),temp


def clientes_dia(data):
    temp = pd.DataFrame(data.groupby('Fecha')['Cliente'].nunique()).reset_index()

    return *generate_files(temp),temp


def pedidos_dia(data):
    temp = pd.DataFrame(data.groupby('Fecha')['Pedido'].nunique()).reset_index()

    return *generate_files(temp),temp


def metodologia(lineas, referencias):
    if referencias < 2000 and lineas <= 20000:
        metodologia = 'Pick to parts'
    elif lineas < 1000:
        metodologia = 'Parts to pick'
    elif lineas <= 20000:
        metodologia = 'Pick to sort'
    else:
        metodologia = 'Pick to box'

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[2000, 2000, ],
        y=[0, 20000, ],
        fill="tozerox",
        mode='none',
        name='Pick to parts'

    ))

    fig.add_trace(go.Scatter(
        x=[2000, 1000000, ],
        y=[1000, 1000, ],
        fill="tozeroy",
        mode='none',
        name='Parts to pick'
    ))

    fig.add_trace(go.Scatter(
        x=[2000, 1000000, ],
        y=[20000, 20000, ],
        fill="tonexty",
        mode='none',
        name='Pick to sort'
    ))

    fig.add_trace(go.Scatter(
        x=[0, 1000000, ],
        y=[100000, 100000, ],
        fill="tonexty",
        mode='none',
        name='Pick to box',

    ))
    fig.add_trace(go.Scatter(
        y=[lineas],
        x=[referencias],
        name='CEDI',
        mode='markers',
        marker_color='rgba(0, 0, 0, 1)',
        marker_size=15,
        text=str(metodologia)
    ))

    fig.update_layout(xaxis_type="log",
                      yaxis_type="log",
                      title="Metodología Picking",
                      xaxis_title="Número de referencias",
                      yaxis_title="Número de líneas por día",
                      width=1300, height=600, )
    # fig.show()

    fig.write_html(file=os.path.join(os.getcwd(), 'app', 'templates', 'metodologia.html'), full_html=False)

    return metodologia

def resumen_clientes(data):
    clientes_padre = data['Cliente_padre'].unique()

    data.set_index('Fecha',inplace=True,drop=False,)
    data.index = pd.to_datetime(data.index)
    data.index.rename('_Fecha',inplace=True)

    results = defaultdict(list)

    for i in clientes_padre:
        temp = data[data['Cliente_padre'] == i]


        results['Cliente'].append(i)

        results['Unidades acumuladas'].append(temp['Cantidad'].sum())
        results['Clientes totales'].append(temp['Cliente'].nunique())


        clientes = temp.groupby('Fecha')['Cliente'].nunique()
        results['Clientes dia maximo'].append(clientes.max())
        results['Clientes dia Per90'].append(int(clientes.quantile(0.9)))

        unidades = temp.groupby('Fecha')['Cantidad'].sum()
        results['Unidades dia max'].append(unidades.max())
        results['Unidades dia Per90'].append(int(unidades.quantile(0.9)))

        temp = temp['Fecha']
        temp = temp.resample('W').nunique()

        results['Frecuencia días (despachos semana) Per90'].append(round(temp.quantile(0.9),1))
        results['Frecuencia días (despachos semana) Per80'].append(round(temp.quantile(0.8),1))
        results['Frecuencia días (despachos semana) Promedio'].append(round(temp.mean(),1))

        df = pd.DataFrame(results)
        df.sort_values(by=['Unidades acumuladas'], inplace=True, ascending=False)
        df.reset_index(drop=True,inplace=True)

    return df.head(30).to_html(classes='table', header="true")


def dia_semana(data):
    temp = pd.DataFrame(data.groupby('Fecha')['Cantidad'].sum()).reset_index()
    result = pd.DataFrame(temp.groupby(temp['Fecha'].dt.day_name('spanish'))['Cantidad'].mean()).loc[['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']]

    data = [
        go.Bar(
            x=result.index,  # assign x as the dataframe column 'x'
            y=result['Cantidad'],

        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON