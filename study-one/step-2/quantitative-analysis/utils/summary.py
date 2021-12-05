#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 12:01:22 2020
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

data = pd.read_csv('./input/output_reviewing_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
display_bar()
print('\nNumber of repositories:', len(data.groupby(['repo'])))  
print(data['repo'].describe())
print(data['repo'].value_counts())

display_bar()
print(data['pr_labels'].describe())
print(data['pr_labels'].value_counts())

print('\nNumber of subsequent commits:', data['n_sub_commits'].sum())

print('\nNumber of refactoring edits:', data['n_refactorings'].sum())

print('\nNumber of review comments:', data['n_review_comments'].sum())

display_bar()
print('\nRefactoring-inducing PRs')  
print(data['has_refactorings'].describe())
print(data['has_refactorings'].value_counts())

display_bar()
data_refs = pd.read_csv('../input/input_refactorings_at_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
data_grouped = data_refs.groupby(['repo', 'pr_number'])
 
      
