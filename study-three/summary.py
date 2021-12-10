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
# Summary of sample for quantitative analysis
#################

data = pd.read_csv('./input/output_reviewing_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
data_riprs = data.loc[data['has_refactorings'] == True,:]

display_bar()
print('\nNumber of repositories:', len(data_riprs.groupby(['repo'])))
print(data_riprs['repo'].describe())

display_bar()
print('\nNumber of subsequent commits:', data_riprs['n_sub_commits'].sum())
print('\nNumber of refactoring edits:', data_riprs['n_refactorings'].sum())

raise SystemExit()



