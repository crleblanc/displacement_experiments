#!/usr/bin/env python
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# This script read input GPS data and uses KMeans clustering to determine the displacement in three dimensions.  Note: this is
# very dependant on the input data quality.  Noisy input will give meaningless results.  Please check the graphs to confirm a good fit.

parser = argparse.ArgumentParser(description='Find displacements in 3 dimensions in input GPS records')
parser.add_argument('filenames', type=str, nargs='+', help='One or more input files to process')
parser.add_argument('--c', dest='clusters', type=int, default=2,
                    help='The number of clusters to find. Usually 2, a cluster before and after the quake')

def read_file(fname, cols):
    data = pd.read_csv(fname, delim_whitespace=True, usecols=cols)
    data = data.set_index('sec-past-eq')
    return data

def get_displacement(dframe, columns, n):
    """Use KMeans clustering to find the cluster centers and return a modified dataframe and time ordered numpy array of displacements (XYZ)"""
    km = KMeans(n_clusters=n)
    clusters = km.fit_predict(dframe[columns].values)

    # add a new column for the cluster id
    dframe['cluster_id'] = pd.Series(clusters, index=dframe.index)

    # add columns for the mean X/Y/Z for each cluster from min to max time (straight lines)
    mean_columns = []
    for col in columns:
        col_name = col + '_mean'
        mean_columns.append(col_name)
        dframe[col_name] = pd.Series(np.zeros(dframe.shape[0], dtype=np.float64), index=dframe.index)

    cluster_times = []

    # get a list of min/max times of clusters so we can sort them by time, this will give us relative displacement by time
    for i, centers in enumerate(km.cluster_centers_):

        times = dframe.index[dframe['cluster_id'] == i]
        cluster_times.append(times.mean())

        # record the mean value of the cluster for each component in the output dataframe
        for i, col_name in enumerate(mean_columns):
            dframe[col_name][times] = centers[i]


    # record the relative displacement
    displacements = []
    cluster_idx = 0
    previous_xyz = None
    for sorted_idx in np.argsort(cluster_times):
        if cluster_idx == 0:
            previous_xyz = km.cluster_centers_[sorted_idx]

        else:
            delta = km.cluster_centers_[sorted_idx] - previous_xyz
            displacements.append(delta)

        previous_xyz = km.cluster_centers_[sorted_idx]

        cluster_idx += 1

    return np.array(displacements)

def main():
    args = parser.parse_args()

    # columns in the input file to parse
    cols = ['sec-past-eq', 'n(cm)', 'e(cm)', 'u(cm)']

    for fname in args.filenames:
        components = cols[1:]
        dframe = read_file(fname, cols)
        disp = get_displacement(dframe, components, args.clusters)

        title = 'File: %s, displacement(s) for' % fname
        for i, event in enumerate(disp):
            title += (' event %d :%s=%.2f %s=%.2f %s=%.2f' % (i+1, components[0], event[0], components[1], event[1], components[2], event[2]))

        dframe.plot(title=title)

    plt.show()

if __name__ == '__main__':
    main()