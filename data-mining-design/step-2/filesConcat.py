
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created on October 8th, 2019

# Cleaning data 

import pandas as pd

def drop_unnamed_columns(data):
    data.drop([col for col in data.columns if "Unnamed" in col], axis = 1, inplace = True)
    return

def merge_refactoring_detail(data):    
    data.loc[:, 'refactoring_detail'] = data[data.columns[6:]].apply(lambda x: ','.join(x.dropna().astype(str)), axis = 1)
    return data


################# STEP 1
# acessing refactoring detection at commit level
#################

data_step1 = pd.read_csv('./results/refactorings_at_apache_commits_level_complete.csv', engine = 'python', encoding = 'ISO-8859-1')
data_step1 = merge_refactoring_detail(data_step1)
drop_unnamed_columns(data_step1)
data_step1['refactoring_level'] = "commit"
data_step1.drop_duplicates(keep = 'first', inplace = True)
print(data_step1)
print('File with refactoring detection at commit level was organized...')


################# STEP 2
# acessing refactoring detection at PR level
#################

data_step2 = pd.read_csv('./results/refactorings_at_apache_prs_level_complete.csv', engine = 'python', encoding = 'ISO-8859-1')
data_step2 = merge_refactoring_detail(data_step2)
drop_unnamed_columns(data_step2)
data_step2['refactoring_level'] = "pr"
data_step2.drop_duplicates(keep = 'first', inplace = True)
print(data_step2)
print('File with refactoring detection at PR level was organized...')


################# STEP 3
# changing the refactoring_target field from NA value to "method" 
#################

data_step1.loc[data_step1.refactoring_type == 'Change Return Type', 'refactoring_target'] = "method"
data_step2.loc[data_step2.refactoring_type == 'Change Return Type', 'refactoring_target'] = "method"
print('refactoring_target field was changed in the files...')


################# STEP 4
# Dropping pull requests that contain only one commit 
#################
print('Dropping pull requests that contain only one commit')

data_step1 = data_step1[data_step1.groupby(['repo', 'pr_number'])['commit'].transform('nunique') > 1]
print(data_step1)
#data_step1.to_csv('./results/output_refactorings_at_apache_commits_level.csv', index = False)

data_step2 = data_step2[data_step2.groupby(['repo', 'pr_number'])['commit'].transform('nunique') > 1]
print(data_step2)
#data_step2.to_csv('./results/output_refactorings_at_apache_prs_level.csv', index = False)


################# STEP 5
# concatenating the output files 
#################

target = './results/output_refactorings_at_apache.csv'

with open(target, 'a') as f:
    data_step1.to_csv(f, header = True, index = False)
    data_step2.to_csv(f, header = False, index = False)
print('The files were concatenated')
