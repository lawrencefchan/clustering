# %%
import os
import pandas as pd

import kidata as kid
import kicluster as cluster


# %% Get refresh data
def mar_refresh(string):
    os.chdir(r'C:\Users\lawrence.chan\Desktop\ki_data\2019-03')

    refreshdate = '2019-03-26'  # refresh

    # --- Compare with refresh cluster
    file = kid.get_files(d=refreshdate, s=string)[0]

    # Resample and trim to refresh
    data = kid.open_kidata_csv(file).resample('5T').mean()
    data = data['2019-03-26-11:00':'2019-03-26-23:30']

    return data


def apr_refresh_1(string=1):
    os.chdir(r'C:\Users\lawrence.chan\Desktop\ki_data\2019-04')

    dates = ['2019-04-05', '2019-04-06']
    files = kid.get_files(dates, string)
    df1 = kid.open_kidata_csv(files[0]).resample('5T').mean()
    df2 = kid.open_kidata_csv(files[1]).resample('5T').mean()

    df = pd.concat([df1, df2])

    return df['2019-04-05, 18:00':'2019-04-06, 11:00']


# %% Compare low/high battery position between refreshes
for i in range(1, 4):
    str_no = i
    apr_data = apr_refresh_1(str_no)
    mar_data = mar_refresh(str_no)

    d = {'Cluster': 1,
         'Indices': [list(range(480))],
         'Battery position': [[i for i in apr_data.columns]],
         'No. Elements': 480
         }

    # --- Timestep to select low/high from --- #
    tstp = '2019-03-26, 22:00'
    low, high = kid.get_low_high(mar_data, 10, timemin=tstp)

    # Plot data
    sm = pd.DataFrame(d)
    sm = cluster.sm_highlights(low, sm)
    cluster.plot_clusters(sm, mar_data, highlights=True,
                          plot_title=f'String {i}-lowest batteries Apr-6')

    sm = pd.DataFrame(d)
    sm = cluster.sm_highlights(high, sm)
    cluster.plot_clusters(sm, mar_data, highlights=True,
                          plot_title=f'String {i}-highest batteries Apr-6')

# %%
