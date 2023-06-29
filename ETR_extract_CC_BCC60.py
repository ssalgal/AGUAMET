# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 04:51:22 2023

@author: Sergio Salazar-Galán - LHA ssalgal@upo.es

"""
import os
import pandas as pd
from pathlib import Path
from rasterstats import zonal_stats
import csv
import glob


#### obtención de la evapotranspiración real por provincia y año

wpprint = r'D:\Pyto_AGUAMET_UPO\Modelo\CC_BCC_60' + '\\_ASCII\\'
wpout= r'D:\Pyto_AGUAMET_UPO\Modelo\CC_BCC_60\Resultados' + '\\' 
wp_mask = r'D:\Pyto_AGUAMET_UPO\Modelo\CC_BCC_60' + '\\Mask\\'

etr_files = glob.glob(wpprint + 'Y1*.asc')

fileExt = r".shp"
m_files = [_ for _ in os.listdir(wp_mask) if _.endswith(fileExt)]
cant = len(m_files)

mv = 0

for m_file in m_files:
    Val_med = []
    F_value = []
    
    for etr_file in etr_files:

    
        zs = zonal_stats(wp_mask + m_file, etr_file, stats=['mean'])
        mean_df = pd.DataFrame.from_dict(zs)
        mv = mean_df.mean(skipna=True)
        
        yeari = Path(etr_file).stem[3:7]
        Name_file = Path(m_file).stem
    
        header = ['YEAR', 'ETR']
    
        if mv is None:
            mv_aj = 0
        else:
            mv_aj = mv
    
        Val_med.append(str(mv_aj.iloc[0]))
        F_value.append(str(yeari)) 
        rows = zip(F_value, Val_med)
      
        with open(wpout + 'ETR_' + Path(m_file).stem + '.csv','w', newline='') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONE)
            writer.writerow(header)
            writer.writerows(rows)
        f.close()