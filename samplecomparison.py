'''Notes:
This compares the different resampling methods available.

A working dendrogram is also included, as well as a broken
clustervar.

Refactoring to do:
* It would make sense to move all of the resampling
into this file and import kicluster.py as necessary
* kicluster.cleandata should go to kidata
* dendrogram/clustervar should go to kicluster maybe

'''
# %%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import scipy.signal as signal
import scipy.cluster.hierarchy as hac

import kicluster


def posttrim_savgol(data, window=31):
    '''
    Applies scipy sav-gol filter then trims output
    '''
    timestamps = data.index
    battnames = data.columns

    # Savitzky-Golay
    filtered_data = signal.savgol_filter(data, window, 3, axis=0)
    filtered_data = pd.DataFrame(filtered_data,
                                 index=timestamps,
                                 columns=battnames)

    # trim refresh edges to isolate profile
    trim = filtered_data.iloc[210:-140]
    return trim


def resamplecomparison(data, factor=10, save_plot=False):
    '''
    Compare different resample methods
    factor: downsample factor-must be a factor of 1620
    '''

    data = data.iloc[:, [0]]

    n_time = factor * 0.5
    # number of samples to take
    n_samples = len(data.index) // factor

    # filter then trim
    pt_savgol = posttrim_savgol(data)

    # Pandas resample
    pd_resample = data.resample(f'{n_time}Min').mean()

    # Scipy resample
    scipy_resample = pd.DataFrame(signal.resample(data, n_samples),
                                  index=data.index[::factor])

    # Scipy decimate
    decimated = np.transpose(signal.decimate(data.T, factor, ftype='fir'))
    decimated = pd.DataFrame(decimated, index=data.index[::factor])

    fig, ax = plt.subplots()  # figsize=(30, 8))

    compare = {'original': data,
               'filter then trim': pt_savgol,
               'pandas resample': pd_resample,
               'scipy resample': scipy_resample,
               'scipy decimate': decimated
               }

    start = '2019-04-05, 23:00'
    stop = '2019-04-06, 9:30'

    for key in compare.keys():
        alpha = 1
        if key == 'original':
            alpha = 0.6
        compare[key][start:stop].plot(ax=ax, alpha=alpha)

    ax.legend(compare.keys(), loc='best')
    ax.set_ylim((2.15, 2.4))
    # ax.set_xlim((1554465200.0, 1554507070.0))

    if save_plot:
        plt.savefig(f'charts/resample_comparison', transparent=True, bbox_inches='tight')
        plt.close(fig)

    plt.show()


# ---- Evaluate metrics, dendograms
def dendrogram(data, p=30, save_plot=False):
    # metrics = [(myMetric, 0.018), ('correlation', 0.018), ('euclidean', 0.6)]
    # for metric, scale in metrics:

    method = ['single', 'complete', 'average', 'weighted', 'centroid', 'ward']
    for i in method:
        D = hac.linkage(data.T, method=i, metric='euclidean')

        fig, ax = plt.subplots(figsize=(10, 8))
        hac.dendrogram(D, p=p, truncate_mode='lastp')

        plt.title(f'Cluster method: {i}')
        ax.tick_params(axis='both', which='major', labelsize=10)
        plt.xlabel('Cluster number')
        plt.ylabel('Distance')
        # plt.ylim(0, 5)
        ax.xaxis.set_ticklabels([])

        if save_plot:
            plt.savefig(f'charts/dendrogram-{i} method', transparent=True, bbox_inches='tight')
            plt.close(fig)

        plt.show()

def clustervar(data):
    '''Compute cluster size variance based on method
    NOTE: This is broken due to standardising dataframes to have time index
    '''
    filter_window = range(51, 252, 50)
    metrics = ['euclidean']
    method = ['single', 'complete', 'centroid', 'ward']
    for i in filter_window:
        filtered_data = posttrim_savgol(data, i)

        for j in method:
            for k in metrics:
                sm = kicluster.cluster_summary(filtered_data, nclusters, j, k)
                print(f"{i}, {j}, {k}, Std: {sm['No. Elements'].std():.2f}")
                
                # filtered_data.loc[:, sm['Battery position'][0]].plot(legend=False)
                # plt.title(f"window: {i}, metric: {j}, method: {k}")
                # plt.show()


# ========== Input parameters ==========
data = kicluster.cleandata('30sec data.csv')
nclusters = 12   # dendogram cutoff
# ========== ================ ==========

dendrogram(data, p=120)
resamplecomparison(data, factor=20)
clustervar(data)
