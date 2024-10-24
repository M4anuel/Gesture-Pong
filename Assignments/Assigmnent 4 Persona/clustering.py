import pandas as pd
import scipy.cluster.hierarchy as hierarchy
import matplotlib
from numpy import ndarray
from pandas import DataFrame, Series

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# load the data
data: DataFrame = pd.read_csv('Umfrage_Ergebnis.csv')

data: DataFrame = data.loc[data["Interesse_Stromverbrauch"] == 1]
data.drop(["Interesse_Stromverbrauch"], axis=1, inplace=True)

linkage_array: ndarray = hierarchy.complete(data)
hierarchy.dendrogram(linkage_array, color_threshold=5.4)
# plot dendrogram
plt.xlabel("Data Object")
plt.ylabel("Cluster Distance")
# plt.show()
# assign cluster labels

cluster_labels: ndarray = hierarchy.fcluster(linkage_array, t=5.4, criterion='distance')

# add cluster labels to the dataframe
data['Cluster'] = cluster_labels

# calculate average properties of all clusters
cluster_averages = data.groupby('Cluster').mean()

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(cluster_averages.T)
    """
    for i in range(1, 4, 1):
        row: Series = cluster_averages.loc[i]
        row_filtered: Series = row[row > 0.0]
        print(row_filtered)
    """