# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 13:54:22 2022

@author: Sergio Salazar-Galán - IIAMA-UPV sersaga@upv.es / LHA ssalgal@upo.es

"""

from datetime import datetime, timedelta 
import numpy as np
import pandas as pd
import math

RCP = 'RCP60' # Cambiar para cada RCP
path_csv= r"D:\Pyto_AGUAMET_UPO\EscenariosCC\RRNN\ET0" + '\\' + RCP + '\\'
Tmin_file = path_csv + "Evento_" + RCP + "_tmin.csv"
Tmax_file = path_csv + "Evento_" + RCP + "_tmax.csv"

coord   = pd.read_csv(r'D:\Pyto_AGUAMET_UPO\Scripts' + '\\Puntos_AEMET_CC_RRNN.csv', sep =';') 
lat_rad = (coord.iloc[:,2])*math.pi/180 # Convertir grados decimales en radianes para las estaciones
Gsc = 0.082 #Gsc constante solar = 0,082 MJ m-2 min-1

pd_tminraw=pd.read_csv(Tmin_file, sep=';', header=None, decimal = '.', index_col=False)
pd_tmaxraw=pd.read_csv(Tmax_file, sep=';', header=None, decimal = '.',index_col=False)
pd_tmin = pd_tminraw.interpolate(method='nearest').iloc[:,0:34675]
pd_tmax= pd_tmaxraw.interpolate(method='nearest').iloc[:,0:34675]
df_tmed = (pd_tmax+pd_tmin)/2
df_tdif = pd_tmax-pd_tmin
number_i = len(df_tdif)
number_j = len(df_tdif.columns)

pd_fechas= pd.date_range(start='2006-1-1', end='2100-12-31', freq='d')
pd_fechas = pd_fechas[(pd_fechas.month != 2) | (pd_fechas.day != 29)] #•Eliminar 29 de febrero en años bisiestos

J_dias = [] # lista de almacenamiento de los días julianos
for j in range (number_j):
    DAY = timedelta(1)
    J_est = pd_fechas[j]
    dia_jul = J_est.strftime("%j") # Obtiene el día juliano del año de 1 a 365 
    J_dias.append(dia_jul)
df_J_dias = pd.DataFrame(J_dias).astype(int)

Dr_list = [] #Lista del calculo de la distancia relativa inversa Tierra-Sol
Ds_list = [] #Lista del calculo de la declinación solar 


for j in range (number_j):
    dr = 1 + (0.033*math.cos((2*math.pi/365)*df_J_dias.iloc[j]))
    Dr_list.append(dr)
    ds = 0.409*math.sin(((2*math.pi/365)*df_J_dias.iloc[j])-1.39)
    Ds_list.append(ds)
df_Dr_list = pd.DataFrame(Dr_list).T  
df_Ds_list = pd.DataFrame(Ds_list).T   

ws_mat = np.empty((number_i,number_j))#matriz para el ángulo de radiación a la puesta del sol [rad]
for i in range (number_i):
    for j in range(number_j):
        ws = math.acos((-1*math.tan(lat_rad.iloc[i]))*math.tan(df_Ds_list.iloc[0,j]))
        ws_mat[i,j] = round(ws,5)

Ra_mat = np.empty((number_i,number_j))#matriz para la radiación extraterrestre, Ra, para cada día del año y diversas latitudes (estaciones) [mm/dia]
for i in range (number_i):
    term_i = round(lat_rad.iloc[i],5)
    for j in range(number_j):
        ws_term = float(ws_mat[i,j])
        Ds_term = float(df_Ds_list.iloc[0,j])
        Dr_term = float(df_Dr_list.iloc[0,j])
        Ra_term = float(0.408*((24*60/math.pi)*Gsc*(Dr_term)*((ws_term*math.sin(term_i)*math.sin(Ds_term))+((math.cos(term_i))*(math.cos(Ds_term))*(math.sin(ws_term))))))
        Ra_mat[i,j] = round(Ra_term,5)
df_Ra = pd.DataFrame(Ra_mat)

       
ETO_mat = np.empty((number_i,number_j))#matriz de ETO para cada día del año y diversas latitudes (estaciones) [mm/dia]
for i in range (number_i):
    for j in range(number_j):
        Primer_term = float(df_tmed.iloc[i,j]) + 17.8
        if float(df_tdif.iloc[i,j]) <= 0:
            Segundo_term == 0
        else:
            Segundo_term = float(df_tdif.iloc[i,j])
        Tercer_term = float(df_Ra.iloc[i,j])
        ETO = 0.0023*(Primer_term)*(math.sqrt(Segundo_term))*(Tercer_term)
        ETO_mat[i,j] = round(ETO, 2)

df_ETO = pd.DataFrame(ETO_mat)
df_ETO.to_csv(path_csv +"ETO_" + RCP + ".csv", sep=";", decimal = '.')

##construcción del fichero de evento con las estaciones de interés para cada escenario   
path = r'D:\Pyto_AGUAMET_UPO\EscenariosCC\RRNN\ET0' + '\\' + RCP + '\\'
stations = pd.read_csv(r'D:\Pyto_AGUAMET_UPO\Scripts' + '\\Stations_CC_AEMET.csv', sep =';') # puntos a extraer e imprimir en fichero de evento
seriest = pd.read_csv(path_csv +"ETO_" + RCP + ".csv", sep=";", decimal = '.', engine="python", header=0, index_col=0).astype(str)

serie_rcp = open(path + 'Evento_' + RCP +'_eto.csv', 'w') 

for j in range(len(stations)):
    station = stations.iloc[j,:]
    namest = station.iloc[0]
    UTMX = station.iloc[1]
    UTMY = station.iloc[2]
    ALT = station.iloc[3]
    rowst = seriest.iloc[j,:].astype(str)
    seriestr = ' '.join(rowst.iloc[:])
    serie_rcp.write('E ' + '"' + str(namest) + '" ' + str(UTMX) + ' ' + str(UTMY) + ' ' + str(ALT) + ' 0 ' + seriestr + '\n')
serie_rcp.close()   