'''
All data munge returns time index and battery columns
'''

# %%
import os
import pandas as pd
import matplotlib.pyplot as plt

# --- Munges a Grafana file
def mungedata(file):
    df = pd.read_csv(file, sep=';', skiprows=1)

    df['Time'] = (pd.to_datetime(df.Time, utc=True) +
                  pd.DateOffset(hours=11)).dt.tz_convert(tz=None)

    df = df.set_index('Time')

    # Label battery by position (to refactor)
    # df.columns = [i[10:].split(',')[0].split()[1] for i in df.columns]

    # df = df.dropna(axis=0, how='all')
    # df.index = df.index.round('1s')

    return df


# --- Munges InfluxDB_Monthly backup files (extracted .csv.gz from \\ki_data)
def open_kidata_csv(file, idx='date', get_i=False, get_soc=False):
    '''
    Returns current if get_i is True
    '''
    skip_cols = ['I', 'V', 'soc', 'sid']

    if get_i:
        skip_cols.remove('I')

    if get_soc:
        skip_cols.remove('soc')

    df = pd.read_csv(file, index_col=idx,
                     usecols=lambda x: x not in skip_cols)

    df.index = pd.to_datetime(df.index)
    df = df.dropna(axis=1, how='all')

    return df


def get_files(d, s):
    '''
    Get list of filenames from ki_data by matching date and string
    Parameters
    ----------
    d: list of dates

    s: list of strings
    '''
    if type(d) != list:
        d = [d]
    if type(s) != list:
        s = [s]

    files = [f for f in os.listdir() if f[19:-4] in d and int(f[17]) in s]

    return files


def plot_kidata(files, current=False):
    '''
    Take a list of files and plot the voltage/current of one battery from
    each file on a single graph.
    '''
    if current:
        for file in files:
            date = file[19:-4]

            # get last battery (99) and current
            df = open_kidata_csv(file, get_i=True).iloc[:, -5:-3]

            fig, ax = plt.subplots()
            # df.plot(legend=False, ax=ax, alpha=0.6)
            res = df.resample('5T').mean()
            res.plot(y='1', label='Voltage', ax=ax)
            plt.ylim((1.7, 2.5))

            res.plot(y='I', color='C1', secondary_y=True, label='Current', ax=ax)

            plt.ylim((-300, 350))
            ax.set_title(date)
            plt.show()

    else:
        fig, ax = plt.subplots()
        for file in files:
            df = open_kidata_csv(file).iloc[:, 0]

            df.plot(ax=ax)
            ax.xaxis.grid(True, which='major')

        plt.show()


def save_refresh():
    '''
    Combine a refresh that extends over multiple dates and create a new df
    using concat. Trim df down to refresh period only and save output as csv
    '''
    dates = ['2019-03-26', '2019-03-27']

    for string in range(1, 4):
        mydir = r'C:\Users\lawrence.chan\Desktop\ki_data\2019-03'
        os.chdir(mydir)
        files = get_files(dates, string)

        df = pd.DataFrame()
        for file in files:
            df = pd.concat([df, open_kidata_csv(file)], axis=0)

        # --- trim to refresh
        df = df['2019-03-26, 10:30':'2019-03-27, 09:00']

        df.to_csv(f'{dates[0]}_String {string}.csv')


# --- Return low/high batteries from a csv file
def get_low_high(df, num=10, timemin=None):
    # df = open_kidata_csv('30sec data.csv')
    # df = df.resample('5T').mean()

    if timemin is None:
        timemin = df.idxmin().mode()  # timestamp at min voltage
        ordered = list(df.loc[timemin].sort_values(timemin[0], axis=1).columns)

    else:
        ordered = list(df.at_time(timemin)
                         .sort_values(timemin, axis=1)
                         .columns)

    lowest, highest = ordered[:num], ordered[-num:]

    return lowest, highest


def get_low_batteries(num=20):
    '''
    Unlike get_low_high(), this function selects a slice of the df to deal
    with min values hidden by the smoothing effect of resampling
    '''
    df = open_kidata_csv('30sec data.csv')

    # isolate a deep discharge, return min from each string
    discharge = df.iloc[12400:12800, :480]
    # .plot(legend=False)
    # plt.show()

    timemin = discharge.idxmin().mode()

    ordered = list(df.loc[timemin].sort_values(timemin[0], axis=1).columns)
    lowest, highest = ordered[:num], ordered[-num:]

    return lowest, highest


if __name__ == "__main__":
    # --- Test plot_kidata()
    if __name__ == "__main__":
        dates = ['2019-04-07', '2019-04-08']
        mydir = r'C:\Users\lawrence.chan\Desktop\ki_data\2019-04'
        os.chdir(mydir)

        string = 3
        files = get_files(dates, string)
        files

        # plot_kidata(files)
