
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 10:23:11 2020

"""
import pandas as pd

def display_bar(filename = None):
    if (filename == None):
        print("\n____________________________________________________")
    else:
        print("\n____________________________________________________", file = filename)
    return

def get_n_refactorings(data_g, data_r):
    for pair_c, group_c in data_g:             
        commits = group_c.groupby(['commit'], sort = False)
        count_refactorings = 0        
        for group in commits:            
            if (group[1]['initial_flag'].eq(False).all()): #Is the commit not an initial commit?
                count_refactorings += group[1]['refactoring_type'].count()                            
        index_pr = data_r[(data_r['repo'] == pair_c[0]) & (data_r['pr_number'] == pair_c[1])].index        
        data_r.loc[index_pr, 'n_refactorings'] = count_refactorings            
    return data_r


# preparing data for clustering
display_bar()
data_review = pd.read_csv('./input/input_reviewing_at_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
data_review.drop_duplicates(keep = 'first', inplace = True)
print('\nThere are', len(data_review), 'PRs, which have review comments, to be processed.')
print('\nThese are the columns of our original code review dataset:', list(data_review.columns))

# dropping PRs that have 0 (zero) files changed due to undefined error during data mining
zero_changed_files = data_review[data_review.n_sub_file_changes == 0]
print(zero_changed_files.iloc[:,[0,1]])
data_review = data_review[data_review.n_sub_file_changes != 0]
print('\nAfter dropping PRs that have 0 file changes, there are', len(data_review), 'PRs, which have review comments, to be processed.')

display_bar()
print('Number of repositories:', len(data_review.groupby(['repo'])))  
print(data_review['repo'].describe())
print(data_review['repo'].value_counts())

data = pd.read_csv('./input/input_refactorings_at_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
print('\nThese are the columns of our original refactorings dataset:', list(data.columns))
data_grouped = data.groupby(['repo', 'pr_number'])

# creating a new column n_refactorings
data_review['n_refactorings'] = 0 

display_bar()
print('Number of subsequent commits:', data_review['n_sub_commits'].sum())
print(data_review)

display_bar()
print('\nAdding n_refactorings attribute')
data_review = get_n_refactorings(data_grouped, data_review) # refactoring edits considered only from the second commit
print(data_review)
print('Number of refactorings:', data_review['n_refactorings'].sum())

# setting the has_refactorings attribute
display_bar()
print('\nSetting the has_refactorings attribute')
data_review.loc[data_review['n_refactorings'] == 0, 'has_refactorings'] = False
data_review.loc[data_review['n_refactorings'] > 0, 'has_refactorings'] = True
print(data_review['has_refactorings'].describe())

display_bar()
data_review.to_csv('./output/output_pre_arl_at_apache.csv', index = False)

print('The pre-processing finished')