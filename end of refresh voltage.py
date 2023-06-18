# %% Import modules, define funcs
import os
import pandas as pd
import matplotlib.pyplot as plt

import time

# --- File and end time of each refresh
date = {'2019-03-26': '2019-03-26, 23:20',
        '2019-04-05': '2019-04-06, 10:50',
        '2019-04-07': '2019-04-07, 22:20',
        }


def plot_eor():
    for d, start in date.items():
        files = [f for f in os.listdir() if d in f and
                 'string 1' in f.lower()]

        f = files[0]

        df = pd.read_csv(f, usecols=[0, 1], index_col=0)
        df.index = pd.to_datetime(df.index)
        df = df.resample('5T').mean()

        ax = df.plot()
        ax.set_title(d)

        plt.show()


plot_eor()

# %%


def get_settled_ocv(n):
    # Get settled ocv 'n' hours after refresh

    strings = [1, 2, 3]
    ocv = pd.DataFrame()

    for d, start in date.items():
        files = [f for f in os.listdir() if d in f]
        start = pd.to_datetime(start)

        # Define settled ocv as 'n' hours after end of refresh
        stop = start + pd.DateOffset(hours=n)

        eor_voltage = []

        for s in strings:
            f = [f for f in files if f'string {s}' in f.lower()]
            df = pd.read_csv(f[0], index_col=0).mean(axis=1).to_frame()
            df.index = pd.to_datetime(df.index)
            df = df[start:stop]
            df.columns = [f'{s}, {df.iloc[-1]}']

            eor_voltage.append(df.iloc[-1][0])

        ocv[d] = eor_voltage

    ocv.index = ['String '+str(s) for s in strings]
    ocv.columns = pd.to_datetime(ocv.columns)

    return ocv


# %% Plot results
n = 3
ocv = get_settled_ocv(n)

fig, ax = plt.subplots()
ocv.T.plot(ax=ax, marker='.')
ax.set_title(f'Settled OCV ({n} hours after refresh)')
ax.xaxis.grid(True)
ax.set_ylabel('Voltage')
