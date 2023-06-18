## Overview
The visual analysis of time-series data of a large number of distinct profiles is a challenging exercise using a standard line plot. This is because numerous trends may be present but obscured by the density of information present within the plot.

This code applies a method of categorising battery profiles based on similarity using hierarchical agglomerative clustering to simplify the visualisation. Battery voltage data at a 30-second resolution has been taken from 480 cells within one string of a BESS to evaluate the suitability of clustering for identifying dominant battery behaviours at high states of charge.

The original data is shown below as an indication of the challenge of drawing conclusions from this quantity of data.
<p align="center">
  <img src="https://github.com/lawrencefchan/clustering/blob/main/charts/Original%20data.png" width=50% height=50%>
</p>

## Approach
In this example we use the straightforward euclidean distance as the distance metric. We get a well balanced dendogram as a result, which indicates how the time series can be clusterd.
<p align="center">
  <img src="https://github.com/lawrencefchan/clustering/blob/main/charts/dendrogram-average%20method.png" width=50% height=50%>
</p>

Evaluating the dendogram with 3 clusters with the charts below confirm that the time series are properly separated and assigned to coherent clusters.
<p align="center">
  <img src="https://github.com/lawrencefchan/clustering/blob/main/charts/Cluster%201%20(154).png" width=50% height=50%>
  <img src="https://github.com/lawrencefchan/clustering/blob/main/charts/Cluster%202%20(95).png" width=50% height=50%>
  <img src="https://github.com/lawrencefchan/clustering/blob/main/charts/Cluster%203%20(50).png" width=50% height=50%>
</p>
