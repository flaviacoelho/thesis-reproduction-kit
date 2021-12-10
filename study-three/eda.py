#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 09:11:18 2020
"""
from typing import List, Any

from scipy import stats
import datascience.util as dt, datascience.tables as dtt, matplotlib, matplotlib.pyplot as plt, numpy as np, statsmodels.api as sm
import pandas as pd
from scipy.stats import spearmanr
plt.rcParams.update({'figure.max_open_warning': 0})


def display_boxplot(data, column, flag_log, flag_proportion, path):
    print('\n', column, 'box-plot')
    fig, ax = plt.subplots()
    # Create the boxplot and store the resulting python dictionary
    box = ax.boxplot(data[column], showfliers = True, labels = ' ', meanline = True, showmeans = True)
    if (flag_log):
        plt.yscale('symlog')
    # Call the function to make labels
    make_labels(ax, box, flag_proportion)
    plt.grid(True, axis = 'y')
    display_ylabel(switcher, column)
    plt.savefig(path + column + '_boxplot.svg', dpi = 300, bbox_inches = 'tight', transparent = True, format = 'svg')
    return

def display_column_date(data, column):
    print('\nDataset\'s column:', column, 'by date')
    print(data[column].describe())
    print('\nDataset\'s column:', column, 'by year')
    print(data[column].dt.year.describe().apply("{0:.0f}".format))
    print('\nDataset\'s column', column, 'mode:')
    print(data[column].dt.year.mode())
    return

def count_refactorings(data_g):
  count_refactorings = 0
  for pair_c, group_c in data_g:
        commits = group_c.groupby(['commit'], sort = False)
        first_group = False #used to disconsider the first group = first commit
        for group in commits:
            if first_group == False:
                first_group = True
            else:
                count_refactorings += group[1]['refactoring_type'].count()
  print('Number of refactorings from the second commit:', count_refactorings)
  return

def display_univariate_vis(data, path):
    print('\nFeatures'+'\' magnitude and distribution')
    for column in data:
            if (column == 'created_at'):
                 display_plot_date(data, path)
                 plt.cla()
            if (column == 'length_discussion'):
                print('\nDataset\'s column:', column)
                print(data[column].describe())
                display_mode(data, column)
                display_histogram(data, column, False, path)
                plt.cla()
                display_boxplot(data, column, True, False, path)
                plt.cla()
            if (column == 'n_sub_file_changes'  or column == 'n_sub_additions' or column == 'n_review_comments' or column == 'time_to_merge' or column == 'n_sub_deletions' or column == 'n_sub_commits' or column == 'n_refactorings'):
                print('\nDataset\'s column:', column)
                print(data[column].describe())
                display_mode(data, column)
                display_histogram(data, column, True, path)
                plt.cla()
                display_boxplot(data, column, True, False, path)
                plt.cla()
            if (column == 'n_reviewers'):
                print('\nDataset\'s column:', column)
                print(data[column].describe())
                display_mode(data, column)
                display_histogram(data, column, False, path)
                display_boxplot(data, column, False, False, path)
                plt.cla()
    return

def display_histogram(data, column, flag_log, path):
    print('\n', column, 'histogram')
    data[column].hist(bins = 'auto', color = "skyblue")
    plt.grid(b = None)
    plt.grid(True, axis = 'y')
    display_xlabel(switcher, column)
    plt.ylabel('Frequency')
    plt.tight_layout()
    if (flag_log):
        plt.xscale('log')
    plt.savefig(path + column + '_histogram.svg', dpi = 300, bbox_inches = 'tight', transparent = True, format = 'svg')
    return

def display_histogram_date(data, path, flag = None): #specific to created_at and merged_at columns
    data['created_at'].dt.year.hist(bins = 'auto', color = "red", alpha = 0.5, label = 'PRs created in')
    data['merged_at'].dt.year.hist(bins = 'auto', color = "skyblue", alpha = 0.5, label = 'PRs merged in')
    print('\n created_at and merged_at histogram')
    plt.grid(True, axis = 'y')
    #plt.xlabel('Year')
    plt.legend()
    if (flag):
        plt.ylabel('Number of observations\n(PRs with refactorings)')
    elif (flag == False):
        plt.ylabel('Number of observations\n(PRs with no refactorings)')
    else:
        plt.ylabel('Frequency')
    plt.grid(b = None)
    plt.tight_layout()
    # if (flag != None):
    plt.savefig(path + str(flag) + '_created_and_merged_histogram.svg', dpi = 300, bbox_inches = 'tight', transparent = True)
    return

def display_histogram_refactoring(data, column, path):
    print('\n', column, 'histogram')
    #data[column].hist(bins = 'auto', color = "skyblue")
    data[column].hist(bins = 50, color = "skyblue")
    plt.grid(b = None)
    plt.grid(True, axis = 'y')
    plt.xticks(rotation=90)
    #plt.xlabel('Refactoring types')
    plt.ylabel('Number of observations (log)')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(path + column + '_histogram.png', dpi = 300, bbox_inches = 'tight', transparent = True)
    return

def display_mode(data, column):
    print('\nDataset\'s column', column, 'mode:')
    print(data[column].mode())
    return

def display_plot_date(data, path, flag = None):
    display_column_date(data, 'created_at')
    display_column_date(data, 'merged_at')
    display_histogram_date(data, path, flag)
    return

def display_pair_scatter(data, path, filename):
    data.plot.scatter(x = 'n_sub_commits', y = 'n_refactorings', color = "blue", alpha = 0.5)
    #plt.scatter(data['n_commits'].array, data['n_refactorings'].array, color = "blue", alpha = 0.7)
    plt.xlabel(switcher.get('n_sub_commits', "Invalid argument"))
    plt.ylabel(switcher.get('n_refactorings', "Invalid argument"))
    plt.savefig(path + 'sub_commits_vs_refactorings_' + filename, dpi = 300, bbox_inches = 'tight')
    # sns.pairplot(data, kind = "reg")
    plt.savefig(path + filename, dpi = 300, bbox_inches = 'tight')
    return

def display_xlabel(switcher, column):
    plt.xlabel(switcher.get(column, "Invalid argument"))
    return

def display_ylabel(switcher, column):
    plt.ylabel(switcher.get(column, "Invalid argument"))
    return

def make_labels(ax, boxplot, flag_proportion):
    # Adapted from https://stackoverflow.com/questions/55648729/python-how-to-print-the-box-whiskers-and-outlier-values-in-box-and-whisker-plo
    # Grab the relevant Line2D instances from the boxplot dictionary
    iqr = boxplot['boxes'][0]
    caps = boxplot['caps']
    med = boxplot['medians'][0]
    fly = boxplot['fliers'][0]
    # The x position of the median line
    xpos = med.get_xdata()
    # Lets make the text have a horizontal offset which is some
    # fraction of the width of the box
    xoff = 0.1 * (xpos[1] - xpos[0])
    # The x position of the labels
    xlabel = xpos[1] + xoff
    # The median is the y-position of the median line
    median = med.get_ydata()[1]
    # The 25th and 75th percentiles are found from the
    # top and bottom (max and min) of the box
    pc25 = iqr.get_ydata().min()
    pc75 = iqr.get_ydata().max()
    # The caps give the vertical position of the ends of the whiskers
    capbottom = caps[0].get_ydata()[0]
    captop = caps[1].get_ydata()[0]


    # Make some labels on the figure using the values derived above
    if (flag_proportion):
        ax.text(xlabel, median,
            '{:.2f}'.format(median), va='baseline')
        ax.text(xlabel, pc25,
                '{:.2f}'.format(pc25), va='baseline')
        ax.text(xlabel, pc75,
                '{:.2f}'.format(pc75), va='baseline')
        ax.text(xlabel, capbottom,
                '{:.2f}'.format(capbottom), va='baseline')
        ax.text(xlabel, captop,
                '{:.2f}'.format(captop), va='baseline')
    else:
        ax.text(xlabel, median,
                '{:.0f}'.format(median), va='baseline')
        ax.text(xlabel, pc25,
                '{:.0f}'.format(pc25), va='baseline')
        ax.text(xlabel, pc75,
                '{:.0f}'.format(pc75), va='baseline')
        ax.text(xlabel, capbottom,
                '{:.0f}'.format(capbottom), va='baseline')
        ax.text(xlabel, captop,
                '{:.0f}'.format(captop), va='baseline')
        # create a label for the biggest outlier
        ax.text(1.08 + xoff, np.amax(fly.get_ydata()), '{:.0f}'.format(np.amax(fly.get_ydata())), va='baseline')
    return

def summary_refactoring_kind(data):

  new_df = data.filter(['refactoring_type'], axis=1)
  new_df.dropna(inplace = True)
  new_df.loc[new_df['refactoring_type'].str.contains('change', case=False) & new_df['refactoring_type'].str.contains('type', case=False), 'refactoring_type'] = 'Change Type'
  new_df.loc[(new_df['refactoring_type'] == "Rename Attribute") | (new_df['refactoring_type'] == "Rename Method") | (new_df['refactoring_type'] == "Rename Variable") | (new_df['refactoring_type'] == "Rename Parameter") | (new_df['refactoring_type'] == "Rename Class"), 'refactoring_type'] = 'Rename'
  new_df.loc[(new_df['refactoring_type'] == "Extract Method") | (new_df['refactoring_type'] == "Extract Variable") | (new_df['refactoring_type'] == "Extract Class") | (new_df['refactoring_type'] == "Extract Attribute") | (new_df['refactoring_type'] == "Extract Superclass") | (new_df['refactoring_type'] == "Extract Interface") | (new_df['refactoring_type'] == "Extract Subclass"), 'refactoring_type'] = 'Extract'
  new_df.loc[(new_df['refactoring_type'] == "Move Class") | (new_df['refactoring_type'] == "Move Attribute") | (new_df['refactoring_type'] == "Move Method") | (new_df['refactoring_type'] == "Move Source Folder"), 'refactoring_type'] = 'Move'
  new_df.loc[new_df['refactoring_type'].str.contains('pull up', case=False), 'refactoring_type'] = 'Pull Up'
  new_df.loc[new_df['refactoring_type'].str.contains('inline', case=False), 'refactoring_type'] = 'Inline'
  new_df.loc[new_df['refactoring_type'].str.contains('extract and move', case=False), 'refactoring_type'] = 'Extract and Move'
  new_df.loc[new_df['refactoring_type'].str.contains('move and rename', case=False), 'refactoring_type'] = 'Move and Rename'
  new_df.loc[new_df['refactoring_type'].str.contains('replace', case=False), 'refactoring_type'] = 'Replace'
  new_df.loc[new_df['refactoring_type'].str.contains('push down', case=False), 'refactoring_type'] = 'Push Down'
  new_df.loc[new_df['refactoring_type'].str.contains('parameterize', case=False), 'refactoring_type'] = 'Parameterize'
  new_df.loc[new_df['refactoring_type'].str.contains('merge', case=False), 'refactoring_type'] = 'Merge'
  new_df.loc[new_df['refactoring_type'].str.contains('split', case=False), 'refactoring_type'] = 'Split'

  print(new_df['refactoring_type'].describe())
  print('\nSummarizing by kind of refactoring edits')
  print(new_df['refactoring_type'].value_counts())
  # display_histogram_refactoring(new_df.sort_values('refactoring_type'), 'refactoring_type', './eda/')
  return

def summary_refactoring_types_by_pull_request(data_g, data_r):
  count_refactoring_types = 0
  refactorings = []
  for pair_c, group_c in data_g:
    count_refactoring_types += group_c['refactoring_type'].nunique()
    if(count_refactoring_types == 1):
        refactorings.append(group_c['refactoring_type'].unique().tolist())
    index_pr = data_r[(data_r['repo'] == pair_c[0]) & (data_r['pr_number'] == pair_c[1])].index
    data_r.loc[index_pr, 'n_refactoring_types'] = count_refactoring_types
    count_refactoring_types = 0

  new_df = data_r.filter(['n_refactoring_types'], axis=1)
  print(new_df['n_refactoring_types'].describe())
  print('\nNumber of observations by unique values')
  print(new_df['n_refactoring_types'].value_counts())
  display_boxplot(new_df, 'n_refactoring_types', False, False, './eda/')
  return

def summary_sequence_refactoring_types_by_pull_request(data_ref, data_g, data_r):

  summary_multiple_types_refactoring(data_ref, data_r)
  summary_single_type_refactoring(data_ref, data_g, data_r)

  return

def summary_multiple_types_refactoring(data_ref, data_r):
    count_refactoring_types = 0
    refactorings = []
    sequence = []
    data_ref.dropna(subset = ['refactoring_type'], inplace=True)
    data_g = data_ref.groupby(['repo', 'pr_number'])
    for pair_c, group_c in data_g:
        count_refactoring_types += group_c['refactoring_type'].nunique()
        if (count_refactoring_types != 1):
            # sequence.append(group_c['refactoring_type'].unique().tolist())
            # refactorings.append(sequence)
            refactorings.append(sorted(group_c['refactoring_type'].unique().tolist()))
        index_pr = data_r[(data_r['repo'] == pair_c[0]) & (data_r['pr_number'] == pair_c[1])].index
        data_r.loc[index_pr, 'n_refactoring_types'] = count_refactoring_types
        count_refactoring_types = 0
    di = []
    for i in refactorings:
        i = tuple(i)
        di.append(i)
    dict1 = {}
    for i in di:
        if (i in dict1):
            dict1[i] += 1
        else:
            dict1[i] = 1
    print('There are', len(dict1), 'sequences of types of refactorings')
    for item in sorted(dict1.items(), key=lambda item: item[1]):
        print(item)

    return

def summary_single_type_refactoring(data_ref, data_g, data_r):
    count_refactoring_types = 0
    refactorings = []
    for pair_c, group_c in data_g:
        count_refactoring_types += group_c['refactoring_type'].nunique()
        if (count_refactoring_types == 1):
            refactorings.append(group_c['refactoring_type'].unique().tolist())
        index_pr = data_r[(data_r['repo'] == pair_c[0]) & (data_r['pr_number'] == pair_c[1])].index
        data_r.loc[index_pr, 'n_refactoring_types'] = count_refactoring_types
        count_refactoring_types = 0
    one_type = data_r.loc[data_r['n_refactoring_types'] == 1, :]

    one_type_list = one_type[['repo', 'pr_number']]
    keys = list(one_type_list.columns.values)
    i1 = data_ref.set_index(keys).index
    i2 = one_type.set_index(keys).index
    data_one_type = data_ref[i1.isin(i2)]
    print(data_one_type['refactoring_type'].value_counts())
    summary_refactoring_kind(data_one_type)
    return

def rq_one(data_r, data_ref):
    data_g = data_ref.groupby(['repo', 'pr_number'])

    # summarizing by type of refactorings
    summarizing_types_refactorings(data_ref)

    # summarizing by kind
    summary_refactoring_kind(data_ref)

    # summarizing the number of types of refactoring by pull request
    print('\nSummarizing number of types of refactoring by pull request')
    data_r.loc[:, 'n_refactoring_types'] = 0
    summary_refactoring_types_by_pull_request(data_g, data_r)

    # summarizing sequences of types of refactoring
    summary_sequence_refactoring_types_by_pull_request(data_ref, data_g, data_r)

    return

def summarizing_types_refactorings(data_ref):
    data_ref = data_ref.filter(['refactoring_type'], axis=1)
    print('\nSummarizing by type of refactorings')
    print(data_ref['refactoring_type'].describe())
    print('\nNumber of observations by unique values')
    print(data_ref['refactoring_type'].value_counts())
    return

def summarizing_levels_refactorings(data_ref):
    data_ref = data_ref.filter(['refactoring_type'], axis=1)
    print('\nSummarizing by level of refactorings')

    data_ref_high = data_ref.loc[(data_ref['refactoring_type'] == 'Pull Up Method') |
                                 (data_ref['refactoring_type'] == 'Pull Up Attribute') |
                                 (data_ref['refactoring_type'] == 'Push Down Method') |
                                 (data_ref['refactoring_type'] == 'Push Down Attribute') |
                                 (data_ref['refactoring_type'] == 'Extract Superclass') |
                                 (data_ref['refactoring_type'] == 'Extract Interface') |
                                 (data_ref['refactoring_type'] == 'Move Class') |
                                 (data_ref['refactoring_type'] == 'Move and Rename Class') |
                                 (data_ref['refactoring_type'] == 'Extract Class') |
                                 (data_ref['refactoring_type'] == 'Extract Subclass') |
                                 (data_ref['refactoring_type'] == 'Move and Rename Attribute')
                                ]
    print(data_ref_high['refactoring_type'].describe())
    print('\nNumber of observations by unique values')
    print(data_ref_high['refactoring_type'].value_counts())
    return

def rq_two(data_ref, data_riprs):

    # investigating correlation between subsequent commits and refactoring edits
    display_univariate_vis(data_riprs, './eda/')
    display_pair_scatter(data_riprs, './eda/', 'scatter.svg')
    stats_tests_Spearman(data_riprs, 'n_sub_commits')

    # summarizing the number of refactorings over the 3 initial subsequent commits
    summarizing_by_initial_sub_commits(data_ref)

    # summarizing by low- and high-levels
    summarizing_levels_refactorings(data_ref)
    return

def summarizing_by_initial_sub_commits(data_ref):
    data_g = data_ref.groupby(['repo', 'pr_number'])
    n_refactorings = 0
    for pair_c, group_c in data_g:
        sub_commits = group_c.groupby(['commit'], sort = False)
        count = 1
        for group in sub_commits:
            if count == 4:
                n_refactorings += (group[1]['refactoring_type'].notnull()).sum()
                break
            count += 1
    print('Number of refactorings:', n_refactorings)
    return

def stats_tests_Spearman(data_riprs, column):
    data_true = data_riprs[[column, 'n_refactorings']]

    for c in data_true.columns:
        print('_________________\nFeature:', c)
        prs = data_riprs.loc[:, c]

        # Assumption 2. Checking for normalility
        print('\nAssumption 2. Checking for normality')
        print('Shapiro-Wilk test:', stats.shapiro(prs))

    data_true.loc[:, column] = pd.qcut(data_true[column], labels=False, q=2)
    data_true.loc[:, 'n_refactorings'] = pd.qcut(data_true['n_refactorings'], labels=False, q=2)

    coef, p = spearmanr(data_true, axis=0)
    print('\nSpearman correlation coefficient:', coef)
    # interpret the significance
    alpha = 0.05
    if p > alpha:
        print('Samples are uncorrelated (fail to reject H0) p =', p)
    else:
        print('Samples are correlated (reject H0) p =', p)
    return


switcher = {
        'has_refactorings': "Presence of refactoring edits",
        'n_sub_file_changes': "Number of changed files (log)",
        'n_reviewers': "Number of reviewers",
        'length_discussion': "Length of discussion (log)",
        'n_comments': "Number of comments",
        'n_review_comments': "Number of review comments (log)",
        'n_sub_additions': "Number of added lines (log)",
        'n_sub_deletions': "Number of deleted lines (log)",
        'n_sub_commits': "Number of subsequent commits (log)",
        'n_refactorings': "Refactoring edits (log)",
        'churn': "Churn",
        'time_to_merge': "Time to merge in number of days (log)",
        'cluster_label': 'Cluster label',
        'n_refactoring_types': 'Number of types of refactoring by pull request'
    }

#################
# Descriptive statistics and quantitative data analysis
#################

data = pd.read_csv('./input/output_reviewing_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
# getting the dates as pandas datetime
data['created_at'] = pd.to_datetime(data['created_at'])
data['merged_at'] = pd.to_datetime(data['merged_at'])

data_riprs = data.loc[data['has_refactorings'] == True,:]
print('\nOur sample has', len(data_riprs), 'refactoring-inducing PRs.')

# data for quantitative analysis
data_ref = pd.read_csv('./input/input_refactorings_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
data_r_list = data_riprs[['repo','pr_number']]
keys = list (data_r_list.columns.values)
i1 = data_ref.set_index(keys).index
i2 = data_riprs.set_index(keys).index
data_ref = data_ref[i1.isin(i2)]
data_ref = data_ref.loc[data_ref['initial_flag'] == False, :] #refactorings in PR subsequent commits

# data for qualitative analysis
# data_valid_ref = pd.read_csv('./input/input_validated_refactorings.csv', engine = 'python', encoding = 'ISO-8859-1')

# plt.rcParams.update({'font.size': 13})
# print('\n____________________________')
# display_univariate_vis(data_riprs, './eda/')

#################
# research question 1
#################

rq_one(data_riprs, data_ref) #quantitative analysis
rq_one(data_riprs, data_valid_ref) #qualitative analysis

#################
# research question 2
#################

rq_two(data_ref, data_riprs)

raise SystemExit()

