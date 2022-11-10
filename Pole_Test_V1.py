from viconnexusapi import ViconNexus
import pandas as pd
import numpy as np
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

vicon = ViconNexus.ViconNexus()

sys.path.append( 'C:\\Users\\gaitlab\\miniconda3\\envs\\PoleTest2\\Lib\\site-packages')
sys.path.append( 'C:\\Program Files (x86)\\Vicon\\Nexus2.12\\SDK\\Win32\\Python')

def main() -> None:
    #remember coordinates of FP 1 and 2 are rotated 90deg
    COP1y, ready, rate = vicon.GetDeviceChannel(6,3,1)
    COP1x, ready, rate = vicon.GetDeviceChannel(6,3,2)
    COP1z, ready, rate = vicon.GetDeviceChannel(6,3,3)
    COP2x, ready, rate = vicon.GetDeviceChannel(7,3,1) # note this and
    COP2y, ready, rate = vicon.GetDeviceChannel(7,3,2) # this are swapped around intentionally
    COP2z, ready, rate = vicon.GetDeviceChannel(7,3,3)

    Fz_FP1, ready, rate = vicon.GetDeviceChannel(6,1,3)
    Fz_FP2, ready, rate = vicon.GetDeviceChannel(7,1,3)

    arr_leng = len(COP1x)
    df = pd.DataFrame({
        'COP1x' :COP1x[:arr_leng:10],
        'COP1y' :COP1y[:arr_leng:10],
        'COP1z' :COP1z[:arr_leng:10],
        'COP2x' :COP2x[:arr_leng:10],
        'COP2y' :COP2y[:arr_leng:10],
        'COP2z' :COP2z[:arr_leng:10]
    })

    medians = []
    df_len = len(df['COP1x'])
    for x in range(vicon.GetUnlabeledCount()):
        trajX, trajY, trajZ, trajExists = vicon.GetUnlabeled(x)
        df_labelx = 'trajX' + str(x)
        df_labely = 'trajY' + str(x)
        df_labelz = 'trajZ' + str(x)
        df[df_labelx] = trajX[:df_len]
        df[df_labely] = trajY[:df_len]
        df[df_labelz] = trajZ[:df_len]
        
        medians.append(np.median(df[df_labelz]))
        
    medians = pd.Series(medians)
    medians.sort_values(ascending=False)
    higher_markers_indexs = medians.nlargest(4).index # The 4 highest medians of the marker trajectories in the z direction, correspond to the top markers (highest 2 medians) and the bottom markers (2nd highest 2 medians)

    fs = 100
    N = df.shape[0]
    cutoff = [10, 15]
    nyq = 0.5 * fs
    order = [2, 2]

    normal_cutoff_COP = cutoff[0] / nyq
    normal_cutoff_traj = cutoff[1] / nyq

    b, a = butter(order[0], normal_cutoff_COP, btype='low', analog=False) # filter for force plate data
    d, c = butter(order[1], normal_cutoff_traj, btype='low', analog=False) # filter for marker trajectory data

    for col in df.columns:
        if 'COP' in col:
            df[col] = filtfilt(b, a, df[col])
        if 'traj' in col:
            df[col] = filtfilt(d, c, df[col])

    #top group
    base_label_names = ['trajX', 'trajY', 'trajZ']
    df_labels = []
    for x in higher_markers_indexs: #this variable is defined in step 4
        for y in base_label_names:
            #this will give the correct label i.e. 'trajX0' or 'trajX3'
            label = y + str(x)
            df_labels.append(label)

    # because of the way the data was sorted above, the order of the labels will always be defined in the same way
    df['midXtop'] = ( df[df_labels[0]] + df[df_labels[3]] ) / 2
    df['midYtop'] = ( df[df_labels[1]] + df[df_labels[4]] ) / 2
    df['midZtop'] = ( df[df_labels[2]] + df[df_labels[5]] ) / 2

    df['midXbot'] = ( df[df_labels[6]] + df[df_labels[9]] ) / 2
    df['midYbot'] = ( df[df_labels[7]] + df[df_labels[10]] ) / 2
    df['midZbot'] = ( df[df_labels[8]] + df[df_labels[11]] ) / 2    

    df['diffX'] = df['midXtop'] - df['midXbot']
    df['diffY'] = df['midYtop'] - df['midYbot']
    df['diffZ'] = df['midZtop'] - df['midZbot']

    df['xcoord'] = ((df['diffX'] * -1 * df['midZbot'])/(df['diffZ'])) + df['midXbot']
    df['ycoord'] = ((df['diffY'] * -1 * df['midZbot'])/(df['diffZ'])) + df['midYbot']

    df['distance_between_Markers'] = (((df['diffX'])**2)+((df['diffY'])**2)+((df['diffZ'])**2))**0.5

    df['COP1x'] = df['COP1x'] + 300
    df['COP1y'] = ( df['COP1y'] * -1 ) - 200
    df['COP2x'] = ( df['COP2x'] * -1 ) + 200
    df['COP2y'] = ( df['COP2y'] * -1 ) + 300

    fig, axs = plt.subplots(1, 2)

    axs[0].plot(df['COP1x'], label='COP1x')
    axs[0].plot(df['COP2x'], label='COP2x')
    axs[0].plot(df['xcoord'], label='xcoord')
    axs[0].legend()
    axs[1].plot(df['COP1y'], label='COP1y')
    axs[1].plot(df['COP2y'], label='COP2y')
    axs[1].plot(df['ycoord'], label='ycoord')
    axs[1].legend()
    fig.set_figwidth(15)
    fig.set_figheight(5)

    Fz_FP1 = np.array(Fz_FP1[:arr_leng:10])
    Fz_FP2 = np.array(Fz_FP2[:arr_leng:10])

    base_labels = ['COP1y', 'COP1x', 'COP2y', 'COP2x', 'ycoord', 'xcoord']
    no_of_steps_FP1 = 0
    no_of_steps_FP2 = 0
    #start with force plate 1
    for label in base_labels:
        if '1' in label:
            idx = np.where(Fz_FP1 != 0)[0]
            split_array = np.split(df[label][idx],np.where(np.diff(idx)!=1)[0]+1) # This bit of code will split the data series into a multiple arrays, using the sections where Fz = 0 as the splitting marker
            no_of_steps = len(split_array)
            no_of_steps_FP1 = no_of_steps
            for step in range(no_of_steps):
                step_label = label + '_step' + str(step)
                df[step_label] = split_array[step] #This bit of code will assign each split array to its own data series with an identifiable name
                
        elif '2' in label:
            idx = np.where(Fz_FP2 != 0)[0]
            split_array = np.split(df[label][idx],np.where(np.diff(idx)!=1)[0]+1)
            no_of_steps = len(split_array)
            no_of_steps_FP2 = no_of_steps
            for step in range(no_of_steps):
                step_label = label + '_step' + str(step)
                df[step_label] = split_array[step]
        else:
            idx = np.where(Fz_FP1 != 0)[0]
            split_array = np.split(df[label][idx],np.where(np.diff(idx)!=1)[0]+1)
            no_of_steps = len(split_array)
            for step in range(no_of_steps):
                step_label = label + '_FP1_step' + str(step)
                df[step_label] = split_array[step]
            idx = np.where(Fz_FP2 != 0)[0]
            split_array = np.split(df[label][idx],np.where(np.diff(idx)!=1)[0]+1)
            no_of_steps = len(split_array)
            for step in range(no_of_steps):
                step_label = label + '_FP2_step' + str(step)
                df[step_label] = split_array[step]

    RMS_values = []
    RMS_labels = []
    pass_or_fail = []
    COP_label_names = ['COP1y_step', 'COP1x_step', 'COP2y_step', 'COP2x_step']
    coord_label_names = ['ycoord_FP1_step', 'xcoord_FP1_step', 'ycoord_FP2_step', 'xcoord_FP2_step']
    for x in range(4):
        
        if '1' in COP_label_names[x]:
            no_of_steps_FPX = no_of_steps_FP1
        elif '2' in COP_label_names[x]:
            no_of_steps_FPX = no_of_steps_FP2
        
        for step in range(no_of_steps_FPX):
            COP_label = COP_label_names[x] + str(step)
            coord_label = coord_label_names[x] + str(step)
            
            if len(df[COP_label].dropna()) < 200:
                continue
            
            COP_series = df[COP_label].dropna()
            coord_series = df[coord_label].dropna()
            truncated_COP_series = COP_series[25:len(COP_series)-25]
            truncated_coord_series = coord_series[25:len(coord_series)-25]
            
            MSE = (np.square(np.subtract(truncated_COP_series,truncated_coord_series))).mean() #mean squared error
            RMS_values.append(MSE ** 0.5) #root mean squared error
            RMS_labels.append(COP_label + '___' + coord_label)
            if (MSE ** 0.5) < 20:
                pass_or_fail.append('Pass')
            else:
                pass_or_fail.append('Fail')

    average_distance_between_markers = np.mean(df['distance_between_Markers'])
    RMS_labels.append('Average_Distance_Between_Markers')
    RMS_values.append(average_distance_between_markers)
    if average_distance_between_markers <= 215 & average_distance_between_markers >= 205:
        pass_or_fail.append('Pass')
    else:
        pass_or_fail.append('Fail')
                
    results = pd.DataFrame({
        'RMSE_values':RMS_values,
        'Passed?':pass_or_fail}, index=RMS_labels)

    date_name = datetime.today().strftime('%Y-%m-%d')
    filename = 'Pole_Test_' + date_name + '.csv'
    filepath = 'C:\\Users\\gaitlab\\Documents\\Code\\Pole_Test\\Results\\' + filename
    results.to_csv(filepath)

if __name__ == "__main__":
    main()