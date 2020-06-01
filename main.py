from flask import Flask, request, make_response, redirect, render_template, session, url_for, flash
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap

from app.forms import loginForm, upload_Form

import unittest
import os

from flask_bootstrap import Bootstrap

import pandas as pd

from app import plots

DATABASE = '/path/to/database.db'

# App init

app = Flask(__name__)
bootstrap = Bootstrap(app)

useres  = ['Ingenieria', 'Francisco']
password = 'Oficina1308'
folder_name = 'files_folder'
folder_path = os.path.join(os.getcwd(), folder_name)

# Testing

@app.cli.command()
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(tests)


# Error Handler

# @app.errorhandler(404)
# def not_found(error):
#     return render_template('404.html', error=error)

# Routes

@app.route('/')
def index():
    user_ip = request.remote_addr
    response = make_response(redirect('/hello'))
    # response.set_cookie('user_id',user_ip)
    session['user_ip'] = user_ip


    return response


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    user_ip = session.get('user_ip')
    login_form = loginForm()
    username = session.get('username')

    context = {

        'login_form': login_form,
        'username': username,
    }

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        #session['username'] = username

        if username in useres:
            #password_db = user_document.to_dict().get('password')
            if password == password:

                for file in os.listdir(folder_path):
                    os.remove(os.path.join(folder_path, file))
                flash('Bienvenido de nuevo')
                return redirect(url_for('upload'))
            else:
                flash('Contraseña incorrecta !!')
        else:
            flash('Usuario incorrecto !!')

        return redirect(url_for('index'))

    return render_template('hello.html', **context)

# Route to upload the file

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    upload_form = upload_Form()

    context = {
        'user_ip': session.get('user_ip'),
        'upload_form': upload_form,
        'username': session.get('username'),
    }

    if upload_form.validate_on_submit():
        file1 = upload_form.file1.data
        file2 = upload_form.file2.data
        file3 = upload_form.file3.data
        file4 = upload_form.file4.data
        file5 = upload_form.file5.data

        form_files = [file1, file2, file3, file4, file5]

        excel_files = []
        for file in form_files:
            if file.filename != '':
                file = pd.read_excel(file)
                excel_files.append(file)

        data = pd.concat(excel_files)

        data.to_csv(os.path.join(folder_name, 'unvalidated.csv'),index=False)

        #
        # print(file.filename=='')
        # if file.filename == '':
        #     print(file)
        #     file = pd.read_excel(file)

        # file.to_csv(os.path.join(folder_name, 'unvalidated.csv'),index=False)

        #Toca meterlo a la base de datos
        #session['file'] = file.to_json()

        flash('CARGA EXITOSA !!!!')

        return redirect(url_for('validation'))

    return render_template('upload.html', **context)

# Route of data validation

@app.route('/validation',methods=['GET', 'POST'])
def validation():
    #df = pd.read_json(session['file'])
    df = pd.read_csv(os.path.join(folder_path, 'unvalidated.csv'))
    print(df.head())
    header = df.head()
    #session['header'] = header.to_json()
    tables = [header.to_html(classes='table', header="true",)]

    class validate_Form(FlaskForm):
        #choices=[('', ''),('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')]
        choices=[(i,i) for i in df.columns]
        choices.insert(0,('',''))
        fecha = SelectField(u'Fecha', choices=choices, validators=[DataRequired()])
        sku = SelectField(u'SKU', choices=choices, validators=[DataRequired()])
        cliente = SelectField(u'Cliente', choices=choices, validators=[DataRequired()])
        cliente_padre = SelectField(u'Cliente Padre  (En caso de que no exista dejar en blanco)', choices=choices)
        cantidad = SelectField(u'Cantidad', choices=choices, validators=[DataRequired()])
        categoria = SelectField(u'Categoría', choices=choices, validators=[DataRequired()])
        pedido = SelectField(u'Pedido', choices=choices, validators=[DataRequired()])
        resultados = SubmitField(u'Ir a Resultados')

    validate_form = validate_Form()

    context = {
        'tables': tables,
        'validate_form': validate_form,
    }

    if validate_form.validate_on_submit():
        fecha, sku, cliente = validate_form.fecha.data, validate_form.sku.data, validate_form.cliente.data
        cantidad, categoria, pedido = validate_form.cantidad.data, validate_form.categoria.data, validate_form.pedido.data
        cliente_padre = validate_form.cliente_padre.data

        if cliente_padre =='':
            columns_names = {sku: 'SKU', fecha: 'Fecha', pedido: 'Pedido', cliente: 'Cliente', cantidad: 'Cantidad',
                             categoria: 'Categoria'}
            df.rename(columns=columns_names, inplace=True)
            df['Cliente_padre'] = df['Cliente']
        else:
            columns_names = {sku: 'SKU', fecha: 'Fecha', pedido: 'Pedido',cliente: 'Cliente', cantidad: 'Cantidad', categoria: 'Categoria', cliente_padre: 'Cliente_padre'}
            df.rename(columns=columns_names, inplace=True)

        df = df[['Fecha','Pedido','Cliente','SKU','Cantidad','Categoria','Cliente_padre']]

        saved_files = os.listdir(folder_path)

        cont = 0
        for file in saved_files:
            if 'checked' in file:
                cont += 1

        df.to_csv(os.path.join(folder_name, str('checked_')+'.csv'), index=False)


        return redirect(url_for('results'))


    return render_template('validation.html', **context)

# Dashboar


@app.route('/results', methods=['GET', 'POST'])
def results():
    saved_files = os.listdir(folder_path)
    data = pd.DataFrame()

    for file in saved_files:
        if 'checked' in file:
            temp = pd.read_csv(os.path.join(folder_path, file),parse_dates=['Fecha'])
            data = pd.concat([data, temp],ignore_index=True)

    data.reset_index(drop=True, inplace=True)
    #print(data['Fecha'])
    #print(type(data['Fecha'][0]))
    #data = pd.read_json(session['file'])

    unidades_plot, unidades_tabla, unidades_df, _ = plots.unidades_dia(data)
    lineas_plot, lineas_tabla, lineas_df, _ = plots.lineas_dia(data)
    sku_plot, sku_tabla, sku_df, _ = plots.sku_dia(data)
    clientes_plot, clientes_tabla, clientes_df, _ = plots.clientes_dia(data)
    pedidos_plot, pedidos_tabla, pedidos_df, _ = plots.pedidos_dia(data)
    dia_semana = plots.dia_semana(data)

    tabla_resumen = pd.concat([lineas_df, sku_df, clientes_df, pedidos_df], ignore_index=True)
    tabla_resumen.index = ['Lineas','SKU','Clientes','Pedidos']
    tabla_resumen = tabla_resumen.to_html(classes='table', header="true",)

    metodologia = plots.metodologia(lineas_df['Percentil 90'][0], sku_df['Percentil 90'][0])
    resumen_clientes = plots.resumen_clientes(data)

    media_unidades = unidades_df.loc['-','Media']
    media_lineas = lineas_df.loc['-', 'Media']
    media_sku = sku_df.loc['-', 'Media']
    media_clientes = clientes_df.loc['-', 'Media']

    context = {
        'dia_semana': dia_semana,
        'unidades_plot': unidades_plot,
        'unidades_tabla': unidades_tabla,
        'lineas_plot': lineas_plot,
        'lineas_tabla': lineas_tabla,
        'sku_plot': sku_plot,
        'sku_tabla': sku_tabla,
        'clientes_plot': clientes_plot,
        'clientes_tabla':  clientes_tabla,
        'pedidos_plot': pedidos_plot,
        'pedidos_tabla': pedidos_tabla,
        'tabla_resumen': tabla_resumen,
        'metodologia_sugerida': metodologia,
        'resumen_clientes': resumen_clientes,
        'media_unidades': media_unidades,
        'media_lineas': media_lineas,
        'media_sku': media_sku,
        'media_clientes': media_clientes,
    }



    plot = plots.create_plot()
    return render_template('results.html', **context)

@app.route('/graficos', methods=['GET', 'POST'])
def graficos():
    saved_files = os.listdir(folder_path)
    data = pd.DataFrame()

    for file in saved_files:
        if 'checked' in file:
            temp = pd.read_csv(os.path.join(folder_path, file),parse_dates=['Fecha'])
            data = pd.concat([data, temp],ignore_index=True)

    data.reset_index(drop=True, inplace=True)
    #print(data['Fecha'])
    #print(type(data['Fecha'][0]))
    #data = pd.read_json(session['file'])

    unidades_plot, unidades_tabla, unidades_df, _ = plots.unidades_dia(data)
    lineas_plot, lineas_tabla, lineas_df, _ = plots.lineas_dia(data)
    sku_plot, sku_tabla, sku_df, _ = plots.sku_dia(data)
    clientes_plot, clientes_tabla, clientes_df, _ = plots.clientes_dia(data)
    pedidos_plot, pedidos_tabla, pedidos_df, _ = plots.pedidos_dia(data)

    tabla_resumen = pd.concat([lineas_df, sku_df, clientes_df, pedidos_df], ignore_index=True)
    tabla_resumen.index = ['Lineas','SKU','Clientes','Pedidos']
    tabla_resumen = tabla_resumen.to_html(classes='table', header="true",)

    metodologia = plots.metodologia(lineas_df['Percentil 90'][0], sku_df['Percentil 90'][0])
    resumen_clientes = plots.resumen_clientes(data)

    media_unidades = unidades_df.loc['-','Media']
    media_lineas = lineas_df.loc['-', 'Media']
    media_sku = sku_df.loc['-', 'Media']
    media_clientes = clientes_df.loc['-', 'Media']

    context = {
        'unidades_plot': unidades_plot,
        'unidades_tabla': unidades_tabla,
        'lineas_plot': lineas_plot,
        'lineas_tabla': lineas_tabla,
        'sku_plot': sku_plot,
        'sku_tabla': sku_tabla,
        'clientes_plot': clientes_plot,
        'clientes_tabla':  clientes_tabla,
        'pedidos_plot': pedidos_plot,
        'pedidos_tabla': pedidos_tabla,
        'tabla_resumen': tabla_resumen,
        'metodologia_sugerida': metodologia,
        'resumen_clientes': resumen_clientes,
        'media_unidades': media_unidades,
        'media_lineas': media_lineas,
        'media_sku': media_sku,
        'media_clientes': media_clientes,
    }



    plot = plots.create_plot()
    return render_template('graficos.html', **context)

# Run app___

if __name__ == '__main__':
    #app.config['ENV'] = 'production'
    app.secret_key = 'super secret key'
    app.run(debug=False)
