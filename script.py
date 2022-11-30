#!/usr/bin/env python
# coding: utf-8

# In[136]:


# Carga de librerias basicas
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta, datetime

#Carga de librerias de Dash para correr Dashboard
import dash_bootstrap_components as dbc
from dash import Dash, dash_table, dcc, html, Input, Output, State
from jupyter_dash import JupyterDash


# In[137]:


# Carga de bases de datos de Whirlpool
df = pd.read_excel(r'C:\Users\hecto\OneDrive\Desktop\WORKFILE_Supsa_Energy_Audit_Information_Actualizada.xlsx')
#Cambio de nombre para evitar espacios
df = df.set_axis(['ID','Production_Line','Platform','Familia','Test_Date','Refrigerant','Model_Number','Serial_Number','Sensores','Posicion','Target','Energy_Consumed(kWh/yr)','Porc_Below_Rating_Point','RC_Temp_Average_P1','RC1_Temp_P1','RC2_Temp_P1','RC3_Temp_P1','FC_Temp_Average_P1','FC1_Temp_P1','FC2_Temp_P1','FC3_Temp_P1','Energy_Usage(kWh/day)_P1','Porc_Run_Time_P1','Avg_Ambient_Temp_P1','Temp_Setting_P2','RC_Temp_Average_P2','RC1_Temp_P2','RC2_Temp_P2','RC3_Temp_P2','FC_Temp_Average_P2','FC1_Temp_P2','FC2_Temp_P2','FC3_Temp_P2','Energy_Usage(kWh/day)_P2','Porc_Run_Time_P2','Avg_Ambient_Temp_P2','Ability','Compressor','Supplier','E-star/Std.'], axis=1)
# Cambio de % a valor sin el % para evitar temas en análisis
df['Porc_Below_Rating_Point'] = df['Porc_Below_Rating_Point'].replace("%","")
df['Porc_Below_Rating_Point'] = pd.to_numeric(df['Porc_Below_Rating_Point'])*100
del df['Temp_Setting_P2']
#df['Test_Date'] = df['Test_Date'].dt.strftime("%d/%m/%Y") no usar... dejar para fut ref
df.head()


# In[138]:


app = JupyterDash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Tablero Descriptivo"
server = app.server

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "23rem",
    "padding": "1rem 1rem",
    "background-color": "#1a1919",
}

CONTENT_STYLE = {
    "margin-left": "23rem",
#    "margin-right": "",
     "width": "90rem"
}

sidebar = html.Div(
    [
        html.H2("Tablero Descriptivo", style={'color': '#f4b610', "font-weight": "bold", "font-size": "36px"}),
        html.Hr(style={'color': 'white'}),
        html.H4("Fecha Inicial -> Fecha Final", style={"color": "white", "font-weight": "bold"}),
        dcc.DatePickerRange(id='dates-picker', display_format='DD/MM/YYYY', 
                min_date_allowed=df['Test_Date'].min(), max_date_allowed=df['Test_Date'].max(),
                initial_visible_month=df['Test_Date'].min(), 
                #final_visible_month=df['Test_Date'].max(),
                start_date=df['Test_Date'].min(), end_date=df['Test_Date'].max(), 
                with_portal=True, number_of_months_shown=4,
                style={"background": "white", "color": "black"}),
        html.Br(),
        html.Br(),
        html.H4("Posición",  style={"color": "white", "font-weight": "bold"}),
        dcc.Checklist(options=[1,2], value=[1,2], style={"color": "white","font-size": "20px"}, inline=True, id="pos_checklist", labelStyle={'background':'#1a1919','padding':'0rem 1rem','border-radius':'0.3rem'}),
        html.Br(),
        html.H4("Familia", style={"color": "white", "font-weight": "bold"}),
        dcc.Dropdown(sorted(np.append('Todas',df['Familia'].unique())),'Todas', id="fam_dropdown"),
        html.Br(),
        html.H4("Refrigerante", style={"color": "white", "font-weight": "bold"}),
        dcc.Checklist(options=sorted(df['Refrigerant'].unique()), value=df['Refrigerant'].unique(), style={"color": "white","font-size": "20px"}, inline=True, id="ref_checklist", labelStyle={'background':'#1a1919','padding':'0rem 1rem','border-radius':'0.3rem'}),
        html.Br(),
        html.H4("Lineas de Producción", style={"color": "white", "font-weight": "bold"}),
        dcc.Checklist(options=sorted(df['Production_Line'].unique()), value=df['Production_Line'].unique(), style={"color": "white","font-size": "20px"}, inline=True, id="lineaprod_checklist", labelStyle={'background':'#1a1919','padding':'0rem 1rem','border-radius':'0.3rem'}),
        html.Br(),
        html.H4("Plataforma", style={"color": "white", "font-weight": "bold"}),
        dcc.Dropdown(sorted(np.append('Todas',df['Platform'].unique())), 'Todas', id="plat_dropdown"),
        html.Br(),
        html.H4("Proveedor", style={"color": "white", "font-weight": "bold"}),
        dcc.Dropdown(sorted(np.append('Todas',df['Supplier'].unique())), 'Todas', id="prov_dropdown"),
        #html.Br(),
        #html.Button('Resetear Filtros', id='reset_filters_button', style={"background": "#8a0404", "color": "white","font-size": "16px","width":"21rem"}),
    ],
    style=SIDEBAR_STYLE,id='sidebar',
)
content = html.Div([
    
    html.Div(dbc.Row([
    dbc.Col([dbc.Row(html.H4("Energia Cons. Promedio (kWh/dia)", style={"color": "#1a1919", "font-weight": "bold", "textAlign": "center", "font-size": "18px"})), 
             dbc.Row(html.H2(id="energy_cons_txt", style={"color": "#1a1919", "textAlign": "center", "font-size": "16px"}))],
            width=2),
    dbc.Col([dbc.Row(html.H4("% Below Rating Point Promedio", style={"color": "#1a1919", "font-weight": "bold", "textAlign": "center", "font-size": "18px"})), 
             dbc.Row(html.H2(id="below_rp_txt", style={"color": "#1a1919", "textAlign": "center", "font-size": "16px"}))],
            width=2),
    dbc.Col([dbc.Row(html.H4("Nombre de Familia mas repetida", style={"color": "#1a1919", "font-weight": "bold", "textAlign": "center", "font-size": "18px"})), 
             dbc.Row(html.H2(id="mode_fam_txt", style={"color": "#1a1919", "textAlign": "center", "font-size": "16px"}))],
            width=2),
    dbc.Col([dbc.Row(html.H4("Linea de Producción mas repetida", style={"color": "#1a1919", "font-weight": "bold", "textAlign": "center", "font-size": "18px"})), 
             dbc.Row(html.H2(id="mode_linprod_txt", style={"color": "#1a1919","textAlign": "center", "font-size": "16px"}))],
            width=2),
    dbc.Col([dbc.Row(html.H4("Nombre de Plataforma mas repetida", style={"color": "#1a1919", "font-weight": "bold", "textAlign": "center", "font-size": "18px"})), 
             dbc.Row(html.H2(id="mode_platform_txt", style={"color": "#1a1919","textAlign": "center", "font-size": "16px"}))],
            width=3),
    dbc.Col([dbc.Row(html.H4("Cálculo de CPK", style={"color": "#1a1919", "font-weight": "bold", "textAlign": "center", "font-size": "18px"})), 
             dbc.Row(html.H2(id="cpk_txt", style={"color": "#1a1919","textAlign": "center", "font-size": "16px"}))],
            width=1)
    ]), 
    style={"background-color": "#f4b610","margin-left": "23rem", 'verticalAlign': 'middle'}
    ),
    
    html.Div([
        dbc.Row([
            dbc.Col(html.Div(id="rc_graph", children=[]), width=6),
            dbc.Col(html.Div(id='fc_graph', children=[]), width=6)
        ],
        style={"margin-left": "23rem"}
        ),
        dbc.Row([
            dbc.Col([
                    html.H4("Top 5 - Below Rating Point", style={"color": "#1a1919", "font-weight": "bold", "textAlign": "center", "font-size": "18px"}),
                    html.Div(id="tbl_top5_brp"),
                    html.Br(),
                    html.H4("Bottom 5 - Below Rating Point", style={"color": "#1a1919", "font-weight": "bold", "textAlign": "center", "font-size": "18px"}),
                    html.Div(id="tbl_bot5_brp")
                    ], width=4),
            dbc.Col([
                    html.Div(id="bar-and-line-energy-graph")
                    ], width=8),
        ],
        style={"margin-left": "23rem"}
        )
    ])
])

app.layout = html.Div(
    [
        sidebar,
        content
    ]
)


# In[139]:


df_sorted = df.sort_values(by='Test_Date')

@app.callback(
    Output("rc_graph", "children"),
    [Input("pos_checklist", component_property="value"), Input("fam_dropdown", component_property="value"),
    Input("ref_checklist", component_property="value"), Input("lineaprod_checklist", component_property="value"),
    Input("plat_dropdown", component_property="value"), Input("prov_dropdown", component_property="value"),
    Input('dates-picker', 'start_date'), Input('dates-picker', 'end_date')
    ]
)

def update_rc_fig(posicion,familia,refrigerante,linea_prod,plataforma,proveedor,f_inicio,f_final):
    df_sorted = df.sort_values(by='Test_Date')
    #Filter para posicion
    if isinstance(posicion, list):
        if len(posicion)==1 and posicion[0]== 1:
            rc_y = ['RC1_Temp_P1','RC2_Temp_P1','RC3_Temp_P1']
        elif len(posicion)==1 and posicion[0]== 2:
            rc_y = ['RC1_Temp_P2','RC2_Temp_P2','RC3_Temp_P2']
        else:
            rc_y = ['RC1_Temp_P1','RC2_Temp_P1','RC3_Temp_P1','RC1_Temp_P2','RC2_Temp_P2','RC3_Temp_P2']
    #Filter para familias
    if familia == "Todas":
        temp=df_sorted
    else:
        temp = df_sorted[df_sorted['Familia'] == familia]
    
    #Filter para refrigerantes
    if len(refrigerante)==1:
        temp = temp[temp['Refrigerant'] == refrigerante[0]]
    else:
        pass
    
    #Filter para lineas de producc
    if isinstance(linea_prod, list):
        if len(linea_prod) == 1:
            temp = temp[temp['Production_Line'] == linea_prod[0]]
        elif len(linea_prod) == 2:
            temp = temp[(temp['Production_Line'] == linea_prod[0])
                              | (temp['Production_Line'] == linea_prod[1])]
    else:
        pass
    
    #Filtro para plataforma
    if plataforma == "Todas":
        temp=temp
    else:
        temp = temp[temp['Platform'] == plataforma]
    
    #Filtro para proveedor
    if proveedor == "Todas":
        temp=temp
    else:
        temp = temp[temp['Supplier'] == proveedor]
    
    #Filtro fecha inicial y final
    temp = temp[(temp['Test_Date'] >= f_inicio) & (temp['Test_Date'] <= f_final)]
    
    #Inicio de creacion de gráficas y datos duros
    fig = px.line(data_frame=temp, x="Test_Date", y=rc_y)
    fig.update_layout(
    xaxis_title="Fecha de Prueba",
    yaxis_title="Temperatura de RC (°F)",
    legend=dict(
        title="Leyenda",
        orientation="h",
        yanchor="top",
        y=1.15,
        xanchor="left",
        x=0
))
    return [dcc.Graph(id='linegraph',figure=fig)]


# In[140]:


@app.callback(
    Output("fc_graph", "children"),
    [Input("pos_checklist", component_property="value"), Input("fam_dropdown", component_property="value"),
    Input("ref_checklist", component_property="value"), Input("lineaprod_checklist", component_property="value"),
    Input("plat_dropdown", component_property="value"), Input("prov_dropdown", component_property="value"),
    Input('dates-picker', 'start_date'), Input('dates-picker', 'end_date')
    ]
)

def update_fc_fig(posicion,familia,refrigerante,linea_prod,plataforma,proveedor,f_inicio,f_final):
    df_sorted = df.sort_values(by='Test_Date')
    #Filter para posicion
    if isinstance(posicion, list):
        if len(posicion)==1 and posicion[0]== 1:
            fc_y = ['FC1_Temp_P1','FC2_Temp_P1','FC3_Temp_P1']
        elif len(posicion)==1 and posicion[0]== 2:
            fc_y = ['FC1_Temp_P2','FC2_Temp_P2','FC3_Temp_P2']
        else:
            fc_y = ['FC1_Temp_P1','FC2_Temp_P1','FC3_Temp_P1','FC1_Temp_P2','FC2_Temp_P2','FC3_Temp_P2']
    #Filter para familias
    if familia == "Todas":
        temp=df_sorted
    else:
        temp = df_sorted[df_sorted['Familia'] == familia]
    
    #Filter para refrigerantes
    if len(refrigerante)==1:
        temp = temp[temp['Refrigerant'] == refrigerante[0]]
    else:
        pass
    
    #Filter para lineas de producc
    if isinstance(linea_prod, list):
        if len(linea_prod) == 1:
            temp = temp[temp['Production_Line'] == linea_prod[0]]
        elif len(linea_prod) == 2:
            temp = temp[(temp['Production_Line'] == linea_prod[0])
                              | (temp['Production_Line'] == linea_prod[1])]
    else:
        pass
    
    #Filtro para plataforma
    if plataforma == "Todas":
        temp=temp
    else:
        temp = temp[temp['Platform'] == plataforma]
    
    #Filtro para proveedor
    if proveedor == "Todas":
        temp=temp
    else:
        temp = temp[temp['Supplier'] == proveedor]
    
    #Filtro fecha inicial y final
    temp = temp[(temp['Test_Date'] >= f_inicio) & (temp['Test_Date'] <= f_final)]
    
    #Inicio de creacion de gráficas y datos duros
    fig = px.line(data_frame=temp, x="Test_Date", y=fc_y)

    fig.update_layout(
    xaxis_title="Fecha de Prueba",
    yaxis_title="Temperatura de FC (°F)",
    legend=dict(
        title="Leyenda",
        orientation="h",
        yanchor="top",
        y=1.15,
        xanchor="left",
        x=0
))
    return [dcc.Graph(id='linegraph',figure=fig)]

# @app.callback(
#     [Output("pos_checklist", component_property="value"), Output("fam_dropdown", component_property="value"),
#     Output("ref_checklist", component_property="value"), Output("lineaprod_checklist", component_property="value"),
#     Output("plat_dropdown", component_property="value"), Output("prov_dropdown", component_property="value")]
#     [Input("reset_filters_button", "n_clicks")]
# )

# def reset_button(reset_click):
#     if reset_click > 0:
#         reset_click = 0
#         return [1,2], 'Todas', ['R134','R600'], [2,3,4], 'Todas', 'Todas'


# In[141]:


@app.callback(
    [Output("energy_cons_txt", "children"), Output("below_rp_txt", "children"),
    Output("mode_fam_txt", "children"), Output("mode_linprod_txt", "children"),
    Output("mode_platform_txt", "children"), Output("cpk_txt", "children")],
    [Input("pos_checklist", component_property="value"), Input("fam_dropdown", component_property="value"),
    Input("ref_checklist", component_property="value"), Input("lineaprod_checklist", component_property="value"),
    Input("plat_dropdown", component_property="value"), Input("prov_dropdown", component_property="value"),
    Input('dates-picker', 'start_date'), Input('dates-picker', 'end_date')
    ]
)

def update_txt_numbers(posicion,familia,refrigerante,linea_prod,plataforma,proveedor,f_inicio,f_final):
    df_sorted = df.sort_values(by='Test_Date')
    #Filter para posicion
    if isinstance(posicion, list):
        if len(posicion)==1 and posicion[0]== 1:
            rc_y = ['RC1_Temp_P1','RC2_Temp_P1','RC3_Temp_P1']
        elif len(posicion)==1 and posicion[0]== 2:
            rc_y = ['RC1_Temp_P2','RC2_Temp_P2','RC3_Temp_P2']
        else:
            rc_y = ['RC1_Temp_P1','RC2_Temp_P1','RC3_Temp_P1','RC1_Temp_P2','RC2_Temp_P2','RC3_Temp_P2']
    #Filter para familias
    if familia == "Todas":
        temp=df_sorted
    else:
        temp = df_sorted[df_sorted['Familia'] == familia]
    
    #Filter para refrigerantes
    if len(refrigerante)==1:
        temp = temp[temp['Refrigerant'] == refrigerante[0]]
    else:
        pass
    
    #Filter para lineas de producc
    if isinstance(linea_prod, list):
        if len(linea_prod) == 1:
            temp = temp[temp['Production_Line'] == linea_prod[0]]
        elif len(linea_prod) == 2:
            temp = temp[(temp['Production_Line'] == linea_prod[0])
                              | (temp['Production_Line'] == linea_prod[1])]
    else:
        pass
    
    #Filtro para plataforma
    if plataforma == "Todas":
        temp=temp
    else:
        temp = temp[temp['Platform'] == plataforma]
    
    #Filtro para proveedor
    if proveedor == "Todas":
        temp=temp
    else:
        temp = temp[temp['Supplier'] == proveedor]
    
    #Filtro fecha inicial y final
    temp = temp[(temp['Test_Date'] >= f_inicio) & (temp['Test_Date'] <= f_final)]
    
    avg_energycons = round(temp['Energy_Consumed(kWh/yr)'].mean(),3)
    avg_brp = round(temp['Porc_Below_Rating_Point'].mean(),3)
    mode_fam = temp['Familia'].mode()
    mode_prodline = temp['Production_Line'].mode()
    mode_platform = temp['Platform'].mode()
    cpk_df = temp[['Target','Energy_Consumed(kWh/yr)']].copy().reset_index()
    cpk_df['Difference'] = cpk_df['Energy_Consumed(kWh/yr)'].diff().abs()
    usl = cpk_df['Target'].iat[-1]*1.03
    n_cpk = cpk_df['Energy_Consumed(kWh/yr)'].count()
    X = cpk_df['Energy_Consumed(kWh/yr)'].mean()
    R = cpk_df['Difference'].mean()
    stddev_dif = (cpk_df['Difference'].mean())/1.128
    cpk = round((usl-X)/(3*stddev_dif),2)
    
    return avg_energycons, avg_brp, mode_fam, mode_prodline, mode_platform, cpk


# In[142]:


@app.callback(
    [Output("tbl_top5_brp", "children"), Output("tbl_bot5_brp", "children")],
    [Input("pos_checklist", component_property="value"), Input("fam_dropdown", component_property="value"),
    Input("ref_checklist", component_property="value"), Input("lineaprod_checklist", component_property="value"),
    Input("plat_dropdown", component_property="value"), Input("prov_dropdown", component_property="value"),
    Input('dates-picker', 'start_date'), Input('dates-picker', 'end_date')]
)

def update_tbls(posicion,familia,refrigerante,linea_prod,plataforma,proveedor,f_inicio,f_final):
    df_sorted = df.sort_values(by='Test_Date')
    #Filter para posicion
    if isinstance(posicion, list):
        if len(posicion)==1 and posicion[0]== 1:
            rc_y = ['RC1_Temp_P1','RC2_Temp_P1','RC3_Temp_P1']
        elif len(posicion)==1 and posicion[0]== 2:
            rc_y = ['RC1_Temp_P2','RC2_Temp_P2','RC3_Temp_P2']
        else:
            rc_y = ['RC1_Temp_P1','RC2_Temp_P1','RC3_Temp_P1','RC1_Temp_P2','RC2_Temp_P2','RC3_Temp_P2']
    #Filter para familias
    if familia == "Todas":
        temp=df_sorted
    else:
        temp = df_sorted[df_sorted['Familia'] == familia]
    
    #Filter para refrigerantes
    if len(refrigerante)==1:
        temp = temp[temp['Refrigerant'] == refrigerante[0]]
    else:
        pass
    
    #Filter para lineas de producc
    if isinstance(linea_prod, list):
        if len(linea_prod) == 1:
            temp = temp[temp['Production_Line'] == linea_prod[0]]
        elif len(linea_prod) == 2:
            temp = temp[(temp['Production_Line'] == linea_prod[0])
                              | (temp['Production_Line'] == linea_prod[1])]
    else:
        pass
    
    #Filtro para plataforma
    if plataforma == "Todas":
        temp=temp
    else:
        temp = temp[temp['Platform'] == plataforma]
    
    #Filtro para proveedor
    if proveedor == "Todas":
        temp=temp
    else:
        temp = temp[temp['Supplier'] == proveedor]
    
    #Filtro fecha inicial y final
    temp = temp[(temp['Test_Date'] >= f_inicio) & (temp['Test_Date'] <= f_final)]
    
    #Inicio de creacion de gráficas y datos duros
    tbl_df = temp[['Model_Number','Serial_Number','Porc_Below_Rating_Point']].copy()
    tbl_df['Porc_Below_Rating_Point'] = round(tbl_df['Porc_Below_Rating_Point'], 3)
    top5_df1 = tbl_df[['Model_Number','Serial_Number','Porc_Below_Rating_Point']].copy().sort_values(by='Porc_Below_Rating_Point',ascending=False).head()
    bot5_df1 = tbl_df[['Model_Number','Serial_Number','Porc_Below_Rating_Point']].copy().sort_values(by='Porc_Below_Rating_Point',ascending=True).head()
    
    top5_df = dash_table.DataTable(top5_df1.to_dict('records'), columns=[{"name": i, "id": i} for i in top5_df1.columns])
    bot5_df = dash_table.DataTable(bot5_df1.to_dict('records'), columns=[{"name": i, "id": i} for i in bot5_df1.columns])
    return top5_df, bot5_df


# In[143]:


@app.callback(
    Output("bar-and-line-energy-graph", "children"),
    [Input("pos_checklist", component_property="value"), Input("fam_dropdown", component_property="value"),
    Input("ref_checklist", component_property="value"), Input("lineaprod_checklist", component_property="value"),
    Input("plat_dropdown", component_property="value"), Input("prov_dropdown", component_property="value"),
    Input('dates-picker', 'start_date'), Input('dates-picker', 'end_date')
    ]
)

def update_energy_graph(posicion,familia,refrigerante,linea_prod,plataforma,proveedor,f_inicio,f_final):
    df_sorted = df.sort_values(by='Test_Date')
    #Filter para posicion
    if isinstance(posicion, list):
        if len(posicion)==1 and posicion[0]== 1:
            rc_y = ['RC1_Temp_P1','RC2_Temp_P1','RC3_Temp_P1']
        elif len(posicion)==1 and posicion[0]== 2:
            rc_y = ['RC1_Temp_P2','RC2_Temp_P2','RC3_Temp_P2']
        else:
            rc_y = ['RC1_Temp_P1','RC2_Temp_P1','RC3_Temp_P1','RC1_Temp_P2','RC2_Temp_P2','RC3_Temp_P2']
    #Filter para familias
    if familia == "Todas":
        temp=df_sorted
    else:
        temp = df_sorted[df_sorted['Familia'] == familia]
    
    #Filter para refrigerantes
    if len(refrigerante)==1:
        temp = temp[temp['Refrigerant'] == refrigerante[0]]
    else:
        pass
    
    #Filter para lineas de producc
    if isinstance(linea_prod, list):
        if len(linea_prod) == 1:
            temp = temp[temp['Production_Line'] == linea_prod[0]]
        elif len(linea_prod) == 2:
            temp = temp[(temp['Production_Line'] == linea_prod[0])
                              | (temp['Production_Line'] == linea_prod[1])]
    else:
        pass
    
    #Filtro para plataforma
    if plataforma == "Todas":
        temp=temp
    else:
        temp = temp[temp['Platform'] == plataforma]
    
    #Filtro para proveedor
    if proveedor == "Todas":
        temp=temp
    else:
        temp = temp[temp['Supplier'] == proveedor]
    
    #Filtro fecha inicial y final
    temp = temp[(temp['Test_Date'] >= f_inicio) & (temp['Test_Date'] <= f_final)]
    
    temp2 = temp.groupby('Familia')[['Energy_Consumed(kWh/yr)','Target']].median().reset_index()
    #Inicio de creacion de gráficas y datos duros
    fig = px.bar(temp2, x="Familia", y='Energy_Consumed(kWh/yr)',text_auto=True)
    fig.update_traces(marker_color='#f4b610')
    fig.add_scatter(x=temp2["Familia"], y=temp2["Target"], name="Target", text=temp2['Target'], textposition="top center")
    fig.update_layout(
    title='Mediana del Consumo (kWh/año) y Target por Familia',
    xaxis_title="Familia",
    yaxis_title="Energía Consumida (kWh/yr)",
    legend=dict(
        title="Leyenda",
        yanchor="top",
        y=1,
        xanchor="right",
        x=1
))
    return [dcc.Graph(id='bar-and-line-graph',figure=fig)]


# In[144]:


if __name__=='__main__':
	app.run_server(debug=True, port=2929)
