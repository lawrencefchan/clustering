'''Heirachical agglomeratic clustering using scipy
References:
https://alpynepyano.github.io/healthyNumerics/posts/time_series_clustering_with_python.html
https://stackoverflow.com/questions/21638130/tutorial-for-scipy-cluster-hierarchy
'''

# %%
# import datetime
# import numpy as np

import pandas as pd
import matplotlib.pyplot as plt

import kidata

import scipy.stats as stats
import scipy.cluster.hierarchy as hac
import scipy.signal as signal


def cleandata(file):
    # Time index, battery columns

    data = kidata.mungedata(file)
    data.columns = [i[10:] for i in data.columns]

    return data


# --- Define spearman correlation to use as distance metric
def myMetric(x, y):
    r = stats.pearsonr(x, y)[0]
    return 1 - r


# ---- Applies scipy sav-gol filter then trims output
def posttrim_savgol(data, window=31):
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


# ---- Applies scipy resample then trims output
def sp_resample(data):
    factor = 20
    num = len(data.index) // factor

    sp_resample = pd.DataFrame(signal.resample(data, num),
                               index=data.index[::factor],
                               columns=data.columns)

    trim = sp_resample.iloc[210 // factor:-140 // factor]
    return trim


# ---- Applies scipy sav-gol filter after trimming first
def pretrim_savgol(data, window=31):
    # trim refresh edges to isolate profile
    trim = data.iloc[210:-140]

    timestamps = trim.index
    battnames = trim.columns

    # Savitzky-Golay
    filtered_data = signal.savgol_filter(trim, window, 3, axis=0)
    filtered_data = pd.DataFrame(filtered_data,
                                 index=timestamps,
                                 columns=battnames)

    return filtered_data


# --- Return clusters along column axis from input data using scipy function
def make_clusters(data, cut_off, method, metric):
    D = hac.linkage(data.T, method=method, metric=metric)
    raw_clusters = pd.Series(hac.fcluster(D, cut_off, criterion='maxclust'))

    return raw_clusters


def cluster_summary(data, cut_off, method='single', metric='euclidean'):
    '''Returns a summary of clusters (elements, indices), as well as the
    original data for easy integration with plot_clusters function.
    Parameters:
    -----------
    data: a pandas series of battery position and equivalent cluster

    cut_off: number of clusters to make
    '''
    raw_clusters = make_clusters(data, cut_off, method, metric)
    clusters = [i for i in range(1, cut_off+1)]

    cluster_indices, lens, batts = [], [], []

    for c in clusters:
        indices = list(raw_clusters[raw_clusters == c].index)
        cluster_indices.append(indices)
        lens.append(len(indices))
        batts.append(list(data.columns[indices]))

    d = {'Cluster': clusters,
         'Indices': cluster_indices,
         'No. Elements': lens,
         'Battery position': batts}

    summary = pd.DataFrame(d).sort_values('No. Elements', ascending=False) \
                             .reset_index(drop=True)

    return summary, data  # returns original data for plotting convenience


def sm_highlights(h_list, summary):
    '''Append selected batteries for highlighting to summary df
    Parameters:
    -----------
    h_list: list of batteries to highlight
    '''
    # Rename labels for compatibility with grafana csv
    # labels = ['{pos: ' + str(i) + ', sid: 2}' for i in h_list]
    labels = h_list

    # list of batteries with trim belonging to each cluster
    highlight = []
    for i in summary['Battery position']:
        # highlight.append([j for j in labels if j in i])
        highlight.append([j for j in labels if j in i])
    summary['highlight'] = highlight

    return summary


def plot_clusters(sm, data, nplots=10, envelope=False,
                  highlights=False, legend=True, plot_title='',
                  save_plot=False):
    '''Plots clusters from data using cluster summary
    Parameters:
    -----------
    sm: cluster summary
    data: data to plot
    envelope: plots a shaded
    min-max envelope if True
    highlights: list of batteries to highlight

    NOTE: highlights is not tested.
    '''
    if highlights:
        dt_color, dt_alpha = '0.8', 0.5
    else:
        dt_color, dt_alpha = None, None

    if save_plot:
        figsize = (10, 7)
    else:
        figsize = (6, 3.5)

    # todo: remove indices from sm (if useful)
    # check enumerate over Battery pos, automatic highlights if in sm
    for idx, i in enumerate(sm['Battery position']):

        if idx < nplots:
            fig, ax = plt.subplots(figsize=figsize)
            elements = f'{sm["No. Elements"][idx]}'

            if envelope:
                # --- Individual traces visible
                data.plot(legend=False,
                          color='0.8',
                          alpha=0.3,
                          ax=ax)

            data.loc[:, i].plot(legend=False,
                                color=dt_color,
                                alpha=dt_alpha,
                                ax=ax)
            # ax.set_ylim((2.05, 2.45))

            if highlights:
                hlt = data.loc[:, sm['highlight'][idx]]
                hlts = len(sm['highlight'][idx])
                elements = f'{hlts}/{sm["No. Elements"][idx]}'

                if hlts > 0:
                    h_ax = ax.twinx()
                    hlt.plot(ax=h_ax, legend=legend)

                    if legend:
                        h_ax.legend(loc='lower center', ncol=5)

                    h_ax.get_yaxis().set_ticks([])
                    h_ax.set_ylim(ax.get_ylim())

            cl_name = (f'Cluster {idx} ({elements}) - average method')
            ax.set_ylabel("Battery Voltage")
            ax.set_xlabel("")
            ax.set_title(cl_name)

            # Show legend if there are < 7 batteries displayed
            # Need to edit this to account for behaviour with highlights
            if sm["No. Elements"][idx] < 7:
                ax.legend(sm["Battery position"][idx])

            if save_plot:
                plt.savefig('charts\\' + cl_name,
                            bbox_inches='tight',
                            dpi=200)
            print(data.index[0], data.index[-1])

        else:
            break
    plt.show()


# ========== Input parameters ==========
data = cleandata(file='30sec data.csv')
nclusters = 4   # dendrogram cutoff
save_plot = False
behaviour = 0
# ========== ================ ==========

if __name__ == "__main__":
    # plot clusters based on original grafana export
    filtered_data = sp_resample(data)
    sm = cluster_summary(filtered_data, nclusters,
                            method='average', metric='euclidean')
    plot_clusters(*sm, envelope=True, nplots=nclusters, save_plot=save_plot)

    # --- tuning levers:
    # filter width
    # distance measure (linkage metric)
    # linkage method
    # hac fcluster criterion

    # %% --- plot all
    fig, ax = plt.subplots(figsize=(10, 7))
    filtered_data.loc['2019-04-05 23:15:00':'2019-04-06 09:45:00'].plot(legend=False, ax=ax, alpha=0.6)
    ax.set_ylim(bottom=2.125796267022751)  # top=2.4355774314830554
    ax.set_ylabel('Battery Voltage')

    # if save_plot:
    #     plt.savefig('Original data', bbox_inches='tight', dpi=200)
    plt.show()
