# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 06:20:12 2015

@author: paulinkenbrandt
"""
import snake
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.ticker as tick
from matplotlib.backends.backend_pdf import PdfPages
import os

Drive = 'E:'

folder = Drive + '\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\2015\\2015 q2'
wellinfofile = Drive + '\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\well table 2015-03-23.csv'


wellinfo = pd.read_csv(Drive + '\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\well table 2015-03-23.csv',header=0,index_col=0)
wellinfo["G_Elev_m"] = wellinfo["GroundElevation"]/3.2808
wellinfo["Well"] = wellinfo['Well'].apply(lambda x: str(x).lower().strip())
wellinfo['WellID'] = wellinfo.index.values


#### Manual Water Levels

manualwls = Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\All tape measurements.csv"
manual = pd.read_csv(manualwls, skiprows=0, parse_dates=0, 
                     index_col="DateTime", engine="python")


#### Barometric Pressure Data

#### Compilation of Barometric Pressure Data

pw03baro_append = Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\2015\\2015 q2\\pw03 barologger 06-24-2015.xle"
pw10baro_append = Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\2015\\2015 q2\\pw10 barologger 06-25-2015.xle"
pw19baro_append = Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\2015\\2015 q2\\pw19 barologger 06-26-2015.xle"


pw03baro = Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\pw03baro.csv"
pw10baro = Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\pw10baro.csv"
pw19baro = Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\pw19baro.csv"


snake.appendomatic(pw03baro_append,pw03baro)
snake.appendomatic(pw10baro_append,pw10baro)
snake.appendomatic(pw19baro_append,pw19baro)

# duplicated to update changes made by appendomatic
pw03baro = pd.read_csv(Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\pw03baro.csv",index_col='DateTime',parse_dates=True)
pw10baro = pd.read_csv(Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\pw10baro.csv",index_col='DateTime',parse_dates=True)
pw19baro = pd.read_csv(Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\pw19baro.csv",index_col='DateTime',parse_dates=True)

pw03baro['pw03'] = pw03baro['Level']
pw03baro = snake.hourly_resample(pw03baro['pw03'].to_frame())
pw10baro['pw10'] = pw10baro['Level']
pw10baro = snake.hourly_resample(pw10baro['pw10'].to_frame())
pw19baro['pw19'] = pw19baro['Level']
pw19baro = snake.hourly_resample(pw19baro['pw19'].to_frame())


baro = pd.merge(pw03baro, pw10baro, how="outer", left_index=True, right_index=True)
baro = pd.merge(baro, pw19baro, how="outer", left_index=True, right_index=True)
baro.dropna(axis=0, inplace=True)
baro['integr'] = 0 #for vented transducers
#baro[baro.index.to_datetime()==pd.datetime(2015,3,4,10)]


baro[['pw03','pw10','pw19']].plot()


wellinfo = snake.barodistance(wellinfo)
wellinfo = snake.make_files_table(folder, wellinfo)
#wellinfo.to_csv(folder+"wellinfo2")

infile = Drive + "\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\2015\\2015 q2\\"
pathlist = os.path.splitext(infile)[0].split('\\')
baro.to_csv(pathlist[0] + '\\' + pathlist[1] + '\\' + pathlist[2] + '\\' + pathlist[3] + '\\' + pathlist[4] + '\\' + 'baro' + '.csv')

### Water Level Tranducer Data

#### Import Data

##### Import All Files

pdf_pages = PdfPages(folder+'wells.pdf')
for i in wellinfo.loc[:,'full_file_name']:
    g = snake.imp_new_well(folder+'\\'+i, wellinfo, manual, baro)
    glist = g.columns.tolist()
    for j in range(len(glist)):
        if 'pw' in glist[j]:
            h = glist[j]
    y1 = g['WaterElevation'].values
    y2 = g[h].values
    x1 = g['DateTime'].values
    wellname, wellid = snake.getwellid(folder+'\\'+i,wellinfo)
    ylast = wellinfo[wellinfo['WellID']==wellid]['GroundElevation'].values[0] + wellinfo[wellinfo['WellID']==wellid]['Offset'].values[0] - snake.fcl(manual[manual['WellID']== wellid],max(g.index.to_datetime()))[1]
    yfirst = wellinfo[wellinfo['WellID']==wellid]['GroundElevation'].values[0] + wellinfo[wellinfo['WellID']==wellid]['Offset'].values[0] - snake.fcl(manual[manual['WellID']== wellid],min(g.index.to_datetime()))[1]
    xlast = (snake.fcl(manual[manual['WellID']== wellid],max(g.index.to_datetime()))).name.to_datetime()
    xfirst = (snake.fcl(manual[manual['WellID']== wellid],min(g.index.to_datetime()))).name.to_datetime()
    x4 = [xfirst,xlast]
    y4 = [yfirst,ylast]
    fig, ax1 = plt.subplots()
    ax1.scatter(x4,y4,color='purple')
    ax1.plot(x1,y1,color='blue',label='Water Level Elevation')
    ax1.set_ylabel('Water Level Elevation',color='blue')
    y_formatter = tick.ScalarFormatter(useOffset=False)
    ax1.yaxis.set_major_formatter(y_formatter)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Barometric Pressure (ft)', color='red') 
    ax2.plot(x1,y2,color='red',label='Barometric pressure (ft)')
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, loc=3)
    
    plt.title('Well:' + wellname + '  ' + 'Total Drift = ' + str(g['DriftCorrection'][-1]))
    pdf_pages.savefig(fig)
    
pdf_pages.close()


##### Import One File

#inputfile = "E:\\Snake Valley Water\\Transducer Data\\Raw_data_archive\\2015\\2015 q1\\sg22b 2015-03-05.xle"
#
#g = imp_new_well(inputfile, wellinfo, manual)
#glist = g.columns.tolist()
#for j in range(len(glist)):
#        if 'pw' in glist[j]:
#            h = glist[j]
#y1 = g['WaterElevation'].values
#y2 = g[h].values
#x1 = g['DateTime'].values
#
#wellname, wellid = getwellid(inputfile)
#ylast = wellinfo[wellinfo['WellID']==wellid]['GroundElevation'].values[0] + wellinfo[wellinfo['WellID']==wellid]['Offset'].values[0] - fcl(manual[manual['WellID']== wellid],max(g.index.to_datetime()))[1]
#yfirst = wellinfo[wellinfo['WellID']==wellid]['GroundElevation'].values[0] + wellinfo[wellinfo['WellID']==wellid]['Offset'].values[0] - fcl(manual[manual['WellID']== wellid],min(g.index.to_datetime()))[1]
#xlast = (fcl(manual[manual['WellID']== wellid],max(g.index.to_datetime()))).name.to_datetime()
#xfirst = (fcl(manual[manual['WellID']== wellid],min(g.index.to_datetime()))).name.to_datetime()
#x4 = [xfirst,xlast]
#y4 = [yfirst,ylast]
#
#fig, ax1 = plt.subplots()
#ax1.scatter(x4,y4,color='purple')
#ax1.plot(x1,y1,color='red')
#y_formatter = tick.ScalarFormatter(useOffset=False)
#ax1.yaxis.set_major_formatter(y_formatter)
#ax2 = ax1.twinx()
#ax2.plot(x1,y2,color='blue')
#plt.title(getfilename(inputfile)+'  '+str(g['DriftCorrection'][-1]))
#plt.show()

