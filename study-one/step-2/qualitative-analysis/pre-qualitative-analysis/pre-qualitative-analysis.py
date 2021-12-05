
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

def run_one_encoded(data, flag = None):
    one_hot_encoded = pd.DataFrame(index = data.index)
    for df_c in data:  
        # creating new columns with the 0 and 1 encoding
        one_hot_encoded['n_refactorings_0'] = 0.0
        one_hot_encoded.loc[(data['n_refactorings'] == 0), 'n_refactorings_0'] = 1.0            
        range_begin = [data[df_c].quantile(.0), data[df_c].quantile(.25), data[df_c].quantile(.5), data[df_c].quantile(.75)]
        range_end = [data[df_c].quantile(.25), data[df_c].quantile(.5), data[df_c].quantile(.75), data[df_c].quantile(1.)]
        column_range = zip(range_begin, range_end)
        # iterating and creating new columns, with the 0 and 1 encoding
        iterations = 1
        for c in column_range:                
            if (iterations != 4):
                one_hot_encoded.loc[:, df_c +"_%d_to_%d" % c] = data[df_c].apply(lambda l: 1.0 if l >= c[0] and l < c[1] else 0.0)                        
                iterations += 1
            else:
                one_hot_encoded.loc[:, df_c +"_%d_to_%d" % c] = data[df_c].apply(lambda l: 1.0 if l >= c[0] and l <= c[1] else 0.0)                        
    return one_hot_encoded


STRATUM = 57
# preparing data for qualitative analysis
# This code should be run once

display_bar()
data_review = pd.read_csv('./input/output_ARL_at_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
print('\nThere are', len(data_review), 'PRs to be processed.')

display_bar()
data_review_comments = pd.read_csv('./input/input_review_comments_at_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
data_review_comments.drop_duplicates(keep = 'first', inplace = True)
# print('\nThere are', len(data_review_comments), 'review comments to be processed.')
# print('\nThese are the columns of our original code review comments dataset:', list(data_review_comments.columns))

common = data_review.merge(data_review_comments,on=['repo','pr_number'])
print('\nThere are',len(common),'review comments in', len(common.groupby(['repo','pr_number'])), 'PRs.')
print('\nThese are the columns of our code review comments dataset:', list(common.columns))


display_bar()
data_review_riprs = data_review.loc[data_review['has_refactorings'] == True]
print(data_review_riprs['n_refactorings'].describe())

selected_features = data_review_riprs[['n_refactorings']]          
print(selected_features)

display_bar()
data_review_riprs = data_review_riprs[['repo', 'pr_number']]
print(data_review_riprs)

display_bar()
print('\nOne-hot encoded data')
one_hot_encoded_features = run_one_encoded(selected_features)
print(one_hot_encoded_features)
print('\nThese are the columns of the one-hot encoded dataset\n', list(one_hot_encoded_features.columns))

for c in one_hot_encoded_features.columns:
    if c != 'n_refactorings_0':
        print (c + ": ", (one_hot_encoded_features[c] != 0).sum())

display_bar()
data_low = one_hot_encoded_features[one_hot_encoded_features.n_refactorings_1_to_1 != 0].sample(n=STRATUM)
data_medium = one_hot_encoded_features[one_hot_encoded_features.n_refactorings_1_to_3 != 0].sample(n=STRATUM)
data_high = one_hot_encoded_features[one_hot_encoded_features.n_refactorings_3_to_7 != 0].sample(n=STRATUM)
data_very_high = one_hot_encoded_features[one_hot_encoded_features.n_refactorings_7_to_321 != 0].sample(n=STRATUM)

data_review_low = data_review_riprs.loc[data_low.index]
data_review_low['category'] = 'low'
data_review_medium = data_review_riprs.loc[data_medium.index]
data_review_medium['category'] = 'medium'
data_review_high = data_review_riprs.loc[data_high.index]
data_review_high['category'] = 'high'
data_review_very_high = data_review_riprs.loc[data_very_high.index]
data_review_very_high['category'] = 'very high'

data_review_result = pd.DataFrame()   
data_review_result = data_review_result.append(data_review_low, ignore_index=True)
data_review_result = data_review_result.append(data_review_medium, ignore_index=True)
data_review_result = data_review_result.append(data_review_high, ignore_index=True)
data_review_result = data_review_result.append(data_review_very_high, ignore_index=True)
print(data_review_result)

spreadsheet = pd.DataFrame(columns=['inspector','pr_url','commit','commit_url','initial_flag','refactoring_type','refactoring_detail','p_confirmed_refactorings','p_covered_refactorings','notes'])
url = "https://github.com/"

display_bar()
data_refs = pd.read_csv('./input/input_refactorings_at_apache.csv', low_memory = False)
for index, row in data_review_result.iterrows():
    pr_url = url + row['repo'] + '/pull/' + str(row['pr_number'])
    print(pr_url)
    group_commits = data_refs[(data_refs['repo'] == row['repo']) & (data_refs['pr_number'] == row['pr_number'])]
    for index,row_c in group_commits.iterrows():
        commit_url = url + row['repo'] + '/commit/' + row_c['commit']
        new_row = {'inspector':'', 'pr_url':pr_url,'commit':row_c['commit'],
               'commit_url':commit_url,'initial_flag':row_c['initial_flag'],
               'refactoring_type':row_c['refactoring_type'],
               'refactoring_detail':row_c['refactoring_detail'],
               'p_confirmed_refactorings':'','p_covered_refactorings':'',
               'notes':''}
        spreadsheet = spreadsheet.append(new_row, ignore_index=True)

spreadsheet.to_csv('./output/spreadsheet.csv', index = False)
print('\nThe pre-processing finished')