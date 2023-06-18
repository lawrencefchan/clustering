# %% Import Modules / Load Parameters
import os
import pandas as pd
from IPython.display import display

import kicluster
import kidata

# --- Parameters
DATA_FOLDER = r'C:\Users\lawrence.chan\Desktop\ki_data\2019-03'
NCLUSTERS = 2
KEY_DATES = {  # date of event: (event start: event finish)
    '2019-03-26': ('11:00', '23:40'),  # refresh
    '2019-03-27': ('10:00', '15:00'),  # capacity test
    }

# --- Display cluster summary
cp = pd.DataFrame()

for d, times in KEY_DATES.items():
    refresh = [f for f in os.listdir(DATA_FOLDER) if f[19:-4] == d]
    start, stop = f'{d}-{times[0]}', f'{d}-{times[1]}'

    # Q: Does dropna affect resample?
    for i in refresh:
        data = kidata.open_kidata_csv(os.path.join(DATA_FOLDER, i)) \
                  .dropna(axis=0, how='any')
        filtered_data = data.resample('10T').mean()[start:stop]

        df = kicluster.cluster_summary(filtered_data, NCLUSTERS,
                                 method='ward', metric='euclidean')
        # kicluster.plot_clusters(*df, envelope=True, nplots=NCLUSTERS)

        # Record cluster participation
        cp[f'{d} {i.split("_")[1]}'] = df[0]['Battery position']


# %% Contribution ratio of elements to capacity test clusters by refresh clusters
def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return len(s1.intersection(s2)) / len(s2)


a = cp.iloc[0, 0]
b = cp.iloc[1, 0]
c = cp.iloc[0, 1]
d = cp.iloc[1, 1]

m = [a, b, c, d]

display(cp)

for i in range(2):
    j = i + 1
    while j < 4:
        if j > 1:
            print(f'{i} -> {j}', f'{jaccard_similarity(m[i], m[j]):.2f}')
        j += 1

