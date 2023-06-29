# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 12:38:11 2023

@author: Sergio Salazar-Galán ssalgal@upo.es / sersaga@upv.es 

"""

import os
import pandas as pd
from pathlib import Path
import datetime

path = r'D:\Pyto_AGUAMET_UPO\EscenariosCC\RRNN\PREC' + '\\'
fileExt = r".dat"
files = [_ for _ in os.listdir(path) if _.endswith(fileExt)]

#extracción de la serie temporal de las estaciones     
for i in range(len(files)):
    stid = Path(files[i]).stem[7:57]
    serie_station = open(path + stid + '.csv', 'w') 
    sr_file = pd.read_csv(path + files[i], skiprows=2, header=None, sep=r"\s+", engine='c')
    for j in range(len(sr_file.index)):
        df_monthj = sr_file.iloc[j,3:].reset_index(drop=True)
        rowfiltered = []
        for k in range(len(df_monthj)):
            if df_monthj.iloc[k] >= 0:
                yearj = sr_file.iloc[j,1]
                monthj = sr_file.iloc[j,2]
                dayk = k+1
                value = df_monthj.iloc[k] / 10
                time_station = datetime.datetime(yearj,monthj,dayk)
                timestr = time_station.strftime("%Y-%m-%d")
                row = (timestr, value)
                rowfiltered.append(row)
        df_serie = pd.DataFrame(rowfiltered).astype(str)
        df_serier = df_serie.set_axis(['Dates' , 'Value'], axis=1)
        df_seriedt = df_serier.set_index(pd.DatetimeIndex(df_serier['Dates']))
        del df_seriedt['Dates']
        df_seriedtfill  = df_seriedt.resample('D').ffill()
        seriestr = ';'.join(df_seriedtfill.loc[:,'Value'])
        serie_station.write(seriestr + ';')
    serie_station.close()
            
#extracción de la serie temporal de las estaciones para cada escenario y puntos de interés    
RCP = 'RCP85' # cambiar ruta para cada RCP (RCP45, RCP60, RCP85)
path = r'D:\Pyto_AGUAMET_UPO\EscenariosCC\RRNN\PREC' + '\\' + RCP + '\\'
fileExt = r".csv"
stations = pd.read_csv(r'D:\Pyto_AGUAMET_UPO\Scripts' + '\\Stations_CC_AEMET.csv', sep =';') # puntos a extraer e imprimir en fichero de evento
stationsid = pd.DataFrame(stations['ID'].unique())


files = [_ for _ in os.listdir(path) if _.endswith(fileExt)]
dffiles = pd.DataFrame(files)
dffilesr = dffiles.set_axis(['Names'], axis=1)

listnames = []
namespid = []
for file in files:
    name_split = file.split('.')
    namespid.append(name_split[0])
    listnames.append(file) 
    rows = list(zip(namespid, listnames))

pdrows = pd.DataFrame(rows)
pdrowsr = pdrows.set_axis(['PID', 'Names'], axis=1)

selectstid = []
for j in range(len(stationsid)):
    stationidi = stationsid.iloc[j,0]
    selectfiles = pdrowsr.loc[(pdrowsr['PID'] == stationidi)]
    selectfilesn = selectfiles.iloc[0,1]
    selectstid.append(selectfilesn)

stationselect = pd.DataFrame(selectstid) #listado de estaciones de interés

#construcción del fichero de evento con las estaciones de interés
serie_rcp = open(path + 'Evento_' + RCP +'_ppt.csv', 'w') 
serie_rcp.write('F 01-01-2006 00:00 ' + '\n')
serie_rcp.write('*' + '\n')
serie_rcp.write('G 34674 1440' + '\n')
serie_rcp.write('*' + '\n')

for j in range(len(stationselect)):
    station = stationselect.iloc[j,0]
    rowst = pd.read_csv(path + station, header=None, sep=';').astype(str)
    name_split = station.split('.')
    stationdesc = stations.loc[(stations['ID'] == name_split[0])]
    namest = stationdesc.iloc[0,0]
    UTMX = stationdesc.iloc[0,1]
    UTMY = stationdesc.iloc[0,2]
    ALT = stationdesc.iloc[0,3]
    seriestr = ' '.join(rowst.iloc[0,:])
    serie_rcp.write('P ' + '"' + str(namest) + '" ' + str(UTMX) + ' ' + str(UTMY) + ' ' + str(ALT) + ' 0 ' + seriestr + '\n')
serie_rcp.close()
                      
            