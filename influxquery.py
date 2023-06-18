'''
This code provides a framework for querying and analyzing data from influxdb
'''

# %% Import modules
import os
import pandas as pd

from influxdb import DataFrameClient

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# --- Define functions
def query_str(batt, str_no=1, date=None, meas='cell'):
    '''Returns a query string to call using dbclient.query() given inputs
    battery position, string number and date.

    NOTE: Currently only works for smc database.

    Parameters
    ----------
    batt: battery position. For KI this is an integer between 1
    and 480 inclusive.

    str_no: battery string. For KI this is an integer between 1
    and 3 inclusive.

    date: query date. Default is None, and returns the previous 1-hour
    of data.
    '''
    def query_bounds(date):
        if date == None:
            query = "time > now() - 1h"

        else:
            dt = pd.to_datetime(date)
            start = f"'{dt.isoformat()}Z'"
            stop = f"'{(dt+pd.DateOffset(days=1)).isoformat()}Z'"
            query = f"time > {start} and time < {stop}"

        return query

    dates = query_bounds(date)
    batt_pos = '("pos"' + f"='{batt}')"
    batt_str = '("sid"' + f"='{str_no}')"

    condlist = [dates, batt_pos, batt_str]
    conds = ' and '.join(condlist)

    return f"SELECT * FROM {meas} WHERE {conds} limit 50000"


def runquery(client, batt, str_no, meas, date=None):
    '''
    Runs influx query and returns a dictionary of dataframes
    Parameters
    ----------
    client: influxdb's DataFrameClient class
    '''
    db_query = query_str(batt, str_no, date, meas=meas)
    str_df = client.query(db_query)
    return str_df


def querysample(start, stop, save=False, batt=1, str_no=1, meas='cell'):
    # --- Plot Vc of a single battery between given dates
    for d in pd.date_range(start, stop):
        # Query db
        db_query = query_str(batt, str_no, date=d)
        str_df = dbclient.query(db_query)

        try:
            assert len(str_df) > 0
        except AssertionError:
            continue

        str_df = str_df[meas]
        str_df.index = str_df.index.tz_convert('Etc/GMT-11')

        # Dealing with the timezone conversion
        matplotlib.rcParams['timezone'] = 'Etc/GMT-11'

        ax = str_df.Vc.plot()
        ax.set_ylabel('Battery Voltage (V)')
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax.xaxis.grid(True, which='major')

    plt.title(f'KI {start} - {stop}')

    if save:
        plt.savefig('KI March refresh.png')

    plt.show()


def export_db(meas):
    '''
    Query db and save data from all batteries as csv
    '''
    # --- Setup query for all batteries in all strings
    mydir = r'C:\Users\lawrence.chan\Desktop\ki_data'
    os.chdir(mydir)
    dates = ['2019/05/01']
    strings = [1, 2, 3]

    for date in dates[-1:]:

        for str_no in strings:

            query_out = pd.DataFrame()

            print(f'Querying string {str_no}: {date}')
            for batt in range(1, 481):
                print(f'String {str_no}, battery no.: {batt}')
                db_query = query_str(batt=batt, str_no=str_no, date=date)
                str_df = dbclient.query(db_query)

                try:
                    assert len(str_df) > 0
                except AssertionError:
                    print('No data')
                    continue

                str_df = str_df[meas][['Vc']]
                str_df.columns = [batt]
                str_df.index = pd.to_datetime(str_df.index).round('1s')
                str_df.index = str_df.index + pd.DateOffset(hours=10)

                query_out = pd.concat([query_out, str_df], axis=1, sort=False)

            query_out.index = query_out.index.tz_convert(None)

            sv_date = pd.to_datetime(date).strftime('%Y-%m-%d')
            query_out.to_csv(f'{mydir}\{sv_date}-string {str_no}.csv')

    print('Complete')


def get_trimmed():
    '''
    NOTE: Deprecated function

    # --- Queries influxdb and returns a list of trimmed batteries
    The aim of the code below is to identify if there is a degree of
    correlation between whether a cell is or has been trimed, and whether
    it affects performance.

    Although the basic case is a binary scenario (i.e. trim is on/off),
    this could be a non-trivial problem due to the fact that trim
    is occasionally adjusted, and therefore adds another dimension to the
    dataset.

    Solving this helps approaching datasets with higher dimensionality

    # Note: for this set of data, all trim durations were identical (29239),
    # but in future, unexpected trim behaviour should also be considered
    '''
    lst = []
    for i in range(1, 15):
        db_query = query_str(i)

        str_df = dbclient.query(db_query)[meas]
        str_df.index = pd.to_datetime(str_df.index) \
                         .round('1s') \
                         .tz_localize(None)
        trim_check = sum([1 if i is True else 0 for i in str_df['trimOn']])
        # df = str_df[['Vc', 'Trim']].resample('3T').mean()
        lst.append((i, trim_check))

    trimmed = [batt for (batt, trim) in lst if trim == 29239]

    return trimmed


def init_client(host='172.20.2.52', port=8089,
               user=os.environ.get('influxQueryUser'),
               password=os.environ.get('influxQueryPass'),
               database='smc', timeout=5,
               check_status=False):
    '''
    Create an InfluxDBClient object using the influxdb library.
    Default parameters correspond to KI host using the smc database.
    '''
    dbclient = DataFrameClient(host,
                               port,
                               user,
                               password,
                               database,
                               timeout)

    if check_status:
        db_list = [db['name'] for db in dbclient.get_list_database()]
        print(db_list)

    return dbclient


# --- Run query
if __name__ == "__main__":
    meas = 'cell'
    str_no = 1
    batt = 1

    # --- Setup influx query using default client
    dbclient = init_client()

    # --- Plot voltage of one battery between start and stop dates
    start_date = '2019/03/25'
    stop_date = '2019/04/05'
    # querysample(start_date, stop_date, batt=batt, str_no=str_no, meas=meas)

    # --- Query single battery between defined times
    df = runquery(dbclient, batt=batt, str_no=str_no, meas=meas, date=start_date)
    if len(df) > 0:
        df = df[meas]
        df.Vc[start_date+' 22:45':start_date+' 22:50'].plot()
        plt.show()
    else:
        print('No data to plot')
