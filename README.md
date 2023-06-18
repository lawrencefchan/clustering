## Overview
The visual analysis of time-series data of a large number of distinct profiles is a challenging exercise using a standard line plot. This is because numerous trends may be present but obscured by the density of information present within the plot.

This code applies a method of categorising battery profiles based on similarity using hierarchical agglomerative clustering to simplify the visualisation. Battery voltage data at a 30-second resolution has been taken from 480 cells within one string of a BESS to evaluate the suitability of clustering for identifying dominant battery behaviours at high states of charge.

The original data is shown below as an indication of the challenge of drawing conclusions from this quantity of data.

![Alt text](/charts/Original data.png?raw=true "Original data")

## Approach
In this example we use the straightforward euclidean distance as the distance metric. We get a well balanced dendogram as a result, which indicates how the time series can be clusterd.

![Alt text](/charts/dendrogram-average method.png?raw=true "Dendrogram")


Evaluating the dendogram with 3 clusters with the charts below confirm that the time series are properly separated and assigned to coherent clusters.

![Alt text](/charts/Cluster 1 (154).png?raw=true "Cluster 1")
![Alt text](/charts/Cluster 2 (95).png?raw=true "Cluster 2")
![Alt text](/charts/Cluster 3 (50).png?raw=true "Cluster 3")
