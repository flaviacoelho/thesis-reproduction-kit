#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 7 16:13:00 2020

"""
# clustering
#    Main sources: 
#       [Preprocessing] https://scikit-learn.org/stable/modules/preprocessing.html       
#                       https://towardsdatascience.com/understanding-feature-engineering-part-3-traditional-methods-for-text-data-f6f7d70acd41
#                       A. Zheng and A. Casari. Feature Engineering for Machine Learning: 
#                                               Principles and Techniques for Data Scientists (1st. ed.). O’Reilly Media, Inc., 2018
#       [FP-Growth] http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/


import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth

def check_missing_values(data):
    print('\nThere are the following number of missing values')
    print(data.isna().sum())
    return

def display_bar(filename = None):
    if (filename == None):
        print("\n____________________________________________________")
    else:
        print("\n____________________________________________________", file = filename)
    return

def display_associations(result, filename):
    for index, r in result.iterrows():  
        print('\n', list(r['antecedents']), '->', list(r['consequents']), '\n', 'support:', r['support'], '\n', 'confidence:', r['confidence'], '\n', 'lift:', r['lift'], '\n', 'conviction:', r['conviction'], '\n', file = filename)
        print('\n', list(r['antecedents']), '->', list(r['consequents']), '\n', 'support:', r['support'], '\n', 'confidence:', r['confidence'], '\n', 'lift:', r['lift'], '\n', 'conviction:', r['conviction'], '\n')
    return

def run_one_encoded(data, flag = None):
    one_hot_encoded = pd.DataFrame(index = data.index)
    for df_c in data:    
    # creating range for new columns
        if (df_c == 'n_refactorings'):
            if (flag): # managing the clusters of PRs with refactoring edits                
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
        else:        
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

def run_fpgrowth(data, filename): # running for minimal support == .05    
    #display_bar()
    print('\nRunning for the minimal support = ', .1, file = filename)            
    print('\nRunning for the minimal support = ', .1) 
    result = fpgrowth(data, min_support = .1, use_colnames = True)
    # min_support (default = 0.5) - a float between 0 and 1 for minimum support (= the fraction 
    #   transactions_where_item(s)_occur/total_transactions) of the itemsets returned
    # use_colnames (default = False) - if true, uses the dataframes' column names in the 
    #   returned dataframe instead of column indices    
    output = association_rules(result, metric = "lift", min_threshold = 1) # after, lift > 1 was considered in the manual inspection 
    associations = output.loc[(output['lift'] > 1) & (output['confidence'] >= 0.5) & (output['conviction'] > 1), :] 
    print('\nFP-Growth found', len(associations), 'associations', file = filename)
    print('\nFP-Growth found', len(associations), 'associations') 
    display_associations(associations, filename)   
    return

def run_fpgrowth_by_has_refactoring(data, filename):
    columns = ['n_sub_commits','n_sub_file_changes','n_sub_additions','n_sub_deletions','n_reviewers','n_review_comments', 'time_to_merge', 'n_refactorings','length_discussion']

    data_riprs = data.loc[data['n_refactorings'] != 0, :]
    data_non_riprs = data.loc[data['n_refactorings'] == 0, :]

    display_bar(file_output)
    print('ARL - Refactoring-inducing pull requests\n')
    selected_features = data_riprs.loc[:, columns]
    one_hot_encoded_features = run_one_encoded(selected_features, True)
    print('\nThese are the columns of the one-hot encoded for RIPRs:\n', list(one_hot_encoded_features.columns), file = file_output)
    display_bar(file_output)
    print('\nFP-Growth results - RIPRs', file = filename)
    run_fpgrowth(one_hot_encoded_features, filename) 
    
    
    display_bar(file_output)
    print('ARL - non-Refactoring-inducing pull requests\n')
    selected_features = data_non_riprs.loc[:, columns]
    one_hot_encoded_features = run_one_encoded(selected_features)
    print('\nThese are the columns of the one-hot encoded for non-RIPRs:\n', list(one_hot_encoded_features.columns), file = file_output)
    display_bar(file_output)
    print('\nFP-Growth results - non-RIPRs', file = filename)
    run_fpgrowth(one_hot_encoded_features, filename)     
    return

# Loading the dataset
data_review = pd.read_csv('./input/output_reviewing_apache.csv', low_memory = False)
display_bar()
print('\nThere are', len(data_review), 'PRs to be processed.')
display_bar()
print('\nThese are the columns of our original dataset\n', list(data_review.columns))

# Loading our output file
file_output = open('./output/output_ARL_at_apache.txt', 'a')
# our ARL workflow 
    # 1. Selection of features
    # 2. Preparation of data
    # 3. Running of the algorithm
        
################# STEP 1
# Selection of features
    # We selected all features from our dataset, except 'repo',  'pr_number', 
    # 'pr_title', and 'pr_labels' that denote identifiers (repo and pr_number), 
    # titles (built on natural language) or labels (non-significant)
    # Since 'n_refactorings' gives the information about the presence and magnitude
    # of refactoring edits, we did not select the 'has_refactorings' attribute
    # Since 'time_to_merge' gives the information about the PR's time of life, we 
    # did not select the 'created_at' and 'merged_at' attributes
#################

selected_features = data_review[['n_sub_commits','n_sub_file_changes','n_sub_additions','n_sub_deletions','n_reviewers','n_review_comments', 'time_to_merge', 'n_refactorings','length_discussion']]          
print(selected_features)

# checking the quantiles of n_refactorings
display_bar()
print('\nDeciles of the selected features')
print(selected_features.quantile((.0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.), axis = 0))
display_bar()
# checking for missing values
check_missing_values(selected_features)

################# STEP 2
# Preparation of data
#################
display_bar()
print('\nOne-hot encoded data')
one_hot_encoded_features = run_one_encoded(selected_features)
print(one_hot_encoded_features)
print('\nThese are the columns of the one-hot encoded dataset\n', list(one_hot_encoded_features.columns))
display_bar()
# checking for missing values
check_missing_values(one_hot_encoded_features)

################# STEP 3
# Running the algorithm for clusters and noise
#################
run_fpgrowth_by_has_refactoring(data_review, file_output)
file_output.close()
data_review.to_csv('./output/output_ARL_at_apache.csv', index = False)

print('\nEnd of the association rule learning')
