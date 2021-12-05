#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  19 12:01:22 2020
"""

import pandas as pd

def display_bar(filename = None):
    if (filename == None):
        print("\n____________________________________________________")
    else:
        print("\n____________________________________________________", file = filename)
    return


################# 
# Results 
#################

data_review = pd.read_csv('./input/output_ARL_at_apache.csv', engine = 'python', encoding = 'ISO-8859-1')

data = pd.read_csv('./input/output_spreadsheet.csv', engine = 'python', encoding = 'ISO-8859-1')
url_list = data['pr_url'].unique().tolist()
data_prs = pd.DataFrame(url_list,columns=['pr_url'])

# summarizing the complete sample
print('\nNumber of repositories:', len(data_review.groupby(['repo'])))  
print(data_review['repo'].describe())
print(data_review['repo'].value_counts())
print('\nNumber of subsequent commits:', data_review['n_sub_commits'].sum())
print('\nNumber of refactoring edits:', data_review['n_refactorings'].sum())
print('\nNumber of review comments:', data_review['n_review_comments'].sum())

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


def summarizing(data):
    print('\nNumber of review comments:', data['n_review_comments'].sum())
    print('\nNumber of discussing comments:', data['length_discussion'].sum()-data['n_review_comments'].sum())
    print('\nNumber of subsequent commits:', data['n_sub_commits'].sum())
    print('\nNumber of refactoring edits:', data['n_refactorings'].sum())
    print('\nStats - number of refactoring edits (describe):', data['n_refactorings'].describe())
    print('\nStats - number of refactoring edits (count_values):', data['n_refactorings'].value_counts())
    return

print('Summary of data review from our stratified sample')
display_bar()
summarizing(data_review_sample)

display_bar()
N_STRATUM = 57

def summarizing_results(data):
    count_induced = 0
    count_induced_by_level = 0
    count_index = 0
    data_g = data.groupby(['pr_url'])
    for pair_c, group_c in data_g:
        count_index += 1
        commits = group_c.groupby(['commit'], sort = False)
        for pair, group in commits:
            if (group['covered_refactoring_flag'].eq(True).any() | 
                group['covered_refactoring_flag'].eq('VERDADEIRO').any() | 
                group['covered_refactoring_flag'].eq('Verdadeiro').any() |
                group['covered_refactoring_flag'].eq('verdadeiro').any() | 
                group['covered_refactoring_flag'].eq('TRUE').any() | 
                group['covered_refactoring_flag'].eq('True').any() | 
                group['covered_refactoring_flag'].eq('true').any()):
                count_induced += 1
                count_induced_by_level += 1
                break
        if (count_index == N_STRATUM):
            print('Number of refactoring-inducing PRs which refactoring edits were induced by code review - by level:',count_induced_by_level)
            count_induced_by_level = 0
            count_index = 0
    print('Number of refactoring-inducing PRs which refactoring edits were induced by code review:',count_induced)
    return

print('Summary of RIPRs induced by code review for our stratified sample')
display_bar()
summarizing_results(data)

# summarizing by category
data_low = data_review_sample[0:57]
data_medium = data_review_sample[57:114]
data_high = data_review_sample[114:171]
data_very_high = data_review_sample[171:228]

def summarizing_by_category(data, level):
    display_bar()
    print('PRs containing a', level, 'number of refactoring edits')
    summarizing(data)
    return

summarizing_by_category(data_low, 'LOW')
summarizing_by_category(data_medium, 'MEDIUM')
summarizing_by_category(data_high, 'HIGH')
summarizing_by_category(data_very_high, 'VERY HIGH')

data_ref_low = data[0:57]
data_ref_medium = data[57:114]
data_ref_high = data[114:171]
data_ref_very_high = data[171:228]

raise SystemExit()
