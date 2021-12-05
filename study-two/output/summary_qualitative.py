#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  19 12:01:22 2020
"""

import pandas as pd, numpy as np, statistics as stats

def display_bar(filename = None):
    if (filename == None):
        print("\n____________________________________________________")
    else:
        print("\n____________________________________________________", file = filename)
    return

def display_stats(data, column):    
    print('mean:', data[column].mean())
    print('sd:', stats.stdev(data[column]))
    print('median:', data[column].median())
    quartiles = np.quantile(data[column], [0.25, 0.75])
    print('iqr:', quartiles[1] - quartiles[0])

def summarizing(data):
    print('\nNumber of review comments:', data['n_review_comments'].sum())
    print('\nNumber of discussing comments:', data['length_discussion'].sum()-data['n_review_comments'].sum())
    print('\nNumber of subsequent commits:', data['n_sub_commits'].sum())
    print('\nNumber of refactoring edits:', data['n_refactorings'].sum())
    
    display_bar()
    print('\nStats - number of reviewers:')
    display_stats(data,'n_reviewers')
    
    display_bar()
    print('\nStats - number of review comments:')
    display_stats(data,'n_review_comments')
    
    display_bar()
    print('\nStats - number of subsequent commits:')
    display_stats(data,'n_sub_commits')
   
    display_bar()
    print('\nStats - time to merge:')
    display_stats(data,'time_to_merge')
    
    display_bar()
    print('\nStats - number of file changes:')
    display_stats(data,'n_sub_file_changes')
    
    display_bar()
    print('\nStats - number of added lines:')
    display_stats(data,'n_sub_additions')
    
    display_bar()
    print('\nStats - number of deleted lines:')
    display_stats(data,'n_sub_deletions')
    
    display_bar()
    print('\nStats - number of refactoring edits:')
    display_stats(data,'n_refactorings')
        
    return


################# 
# Results 
#################

data_review = pd.read_csv('../input/original_output_reviewing_apache.csv', engine = 'python', encoding = 'ISO-8859-1')

data = pd.read_csv('./sample4/final_sample_4_spreadsheet.csv', engine = 'python', encoding = 'ISO-8859-1')
url_list = data['pr_url'].unique().tolist()
data_prs = pd.DataFrame(url_list,columns=['pr_url'])

# summarizing the complete sample
print('\nNumber of repositories:', len(data_review.groupby(['repo'])))  
print(data_review['repo'].describe())
print(data_review['repo'].value_counts())
print('\nNumber of subsequent commits:', data_review['n_sub_commits'].sum())
print('\nNumber of refactoring edits:', data_review['n_refactorings'].sum())
print('\nNumber of review comments:', data_review['n_review_comments'].sum())
print('\nNumber of refactoring-inducing PRs:', data_review.loc[data_review['has_refactorings'] == True])

display_bar()
# recovering repository's name and PR's number
data_prs['repo'] = ""
data_prs['pr_number'] = 0

for row in data_prs.iterrows():
    output = str(row[1]['pr_url']).split('/')    
    row[1]['repo'] = 'apache/' + output[4]
    row[1]['pr_number'] = output[6]
    data_prs.loc[row[0], 'repo'] = 'apache/' + output[4]
    data_prs.loc[row[0], 'pr_number'] = output[6]
    
data_prs.drop('pr_url', inplace=True, axis = 1)

data_review_sample = pd.DataFrame(columns=['repo', 'pr_number', 'has_refactorings', 'n_changed_files',
       'n_reviewers', 'length_discussion', 'n_comments', 'n_review_comments',
       'n_additions', 'n_deletions', 'created_at', 'merged_at', 'pr_title',
       'pr_labels', 'n_sub_commits', 'n_sub_file_changes', 'n_sub_additions',
       'n_sub_deletions', 'n_refactorings', 'time_to_merge'])


# selecting data review to our sample
for row in data_prs.iterrows():
    repo = str(row[1]['repo'])
    pr_number = int(row[1]['pr_number'])
    index_pr = data_review.loc[(data_review['repo'] == repo) & (data_review['pr_number'] == pr_number)].index.values
    data_review_sample = data_review_sample.append(data_review.iloc[index_pr], ignore_index=True)


print('Summarizing refactoring-inducing PRs')
summarizing(data_review_sample.loc[data_review_sample['has_refactorings'] == True])

display_bar()
print('Summarizing non-refactoring-inducing PRs')
summarizing(data_review_sample.loc[data_review_sample['has_refactorings'] == False])

raise SystemExit()
