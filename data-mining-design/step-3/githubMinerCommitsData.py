#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 17:20:34 2020

"""

import json, pandas as pd, requests, time
from datetime import datetime as dt

def display_bar(filename = None):
    if (filename == None):
        print("\n____________________________________________________")
    else:
        print("\n____________________________________________________", file = filename)
    return

def query_composer(project, repo, commit):
    query = 'query{repository(owner:' + project +', name: ' + repo + ') {object(oid: ' + commit + ') {... on Commit {changedFiles additions deletions}}}}'
    return query
    
def run_query(query): # A simple function to use requests.post to make the API call
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

MAX_REQUESTS = 100
DELAY = 60

# GRAPHQL API v4
#   using an access token   
#################
access_token = 'your-access-token'
headers = {'Authorization': 'Bearer '+ access_token}


################# STEP 1
# preparing data
#################
display_bar()
data_rev_iter = pd.read_csv('./input/input_reviewing_at_apache.csv', low_memory = False)
data_rev_iter.drop_duplicates(keep = 'first', inplace = True)
print('\nThere are', len(data_rev_iter), 'PRs, which have review comments, to be processed.')
print('\nColumns of our reviewing dataset:', list(data_rev_iter.columns))

display_bar()
data_refs = pd.read_csv('./input/input_refactorings_at_apache.csv', low_memory = False)
data_refs.drop_duplicates(keep = 'first', inplace = True)
print('\nColumns of our refactorings dataset:', list(data_refs.columns))

################# STEP 2
# creating a new column that counts the number of subsequent PR commits
# Warning: This step should be run once
#################
# data_rev["n_sub_commits"] = 0
# data_rev["n_sub_file_changes"] = 0
# data_rev["n_sub_additions"] = 0
# data_rev["n_sub_deletions"] = 0
# print('\nColumns of our review dataset:', list(data_rev.columns))
# data_rev.to_csv('./output/output_reviewing_at_apache.csv', index = False)

################# STEP 3
# Mining changed files, added lines, and deleted lines of our sample's subsequent PR commits
#################
project = 'apache'
display_bar()
count_requests = 0
for index, row in data_rev_iter.iterrows():
    print(row['repo'], row['pr_number'])
    repo = row['repo'][7:] #excluding substring apache/
    group_commits = data_refs[(data_refs['repo'] == row['repo']) & (data_refs['pr_number'] == row['pr_number'])].groupby(['commit'], sort = False)
    n_commits = len(group_commits)
    n_sub_commits = n_sub_file_changes = n_sub_additions = n_sub_deletions = 0
    first = True
    data_rev = pd.read_csv('./output/output_reviewing_at_apache.csv', low_memory = False)

    for index, row_c in group_commits:        
        try:
            if (first == True):
                count_requests = n_commits
                first = False
                
            if (count_requests < MAX_REQUESTS):
                if (row_c['initial_flag'].eq(False).all()):
                     n_sub_commits += 1
                     result = run_query(query_composer(json.dumps(project), json.dumps(repo), json.dumps(index)))
                     n_sub_file_changes += result["data"]["repository"]["object"]["changedFiles"]
                     n_sub_additions += result["data"]["repository"]["object"]["additions"]
                     n_sub_deletions += result["data"]["repository"]["object"]["deletions"]
                
                if (first == False):
                    count_requests += 1
            else:
                count_requests = 0
                print('delaying...')
                time.sleep(DELAY)            
        
        except TypeError:
            print('A type error occurred...')
            continue
    
    data_rev.loc[(data_rev['repo'] == row['repo']) & (data_rev['pr_number'] == row['pr_number']), 'n_sub_commits'] = n_sub_commits
    data_rev.loc[(data_rev['repo'] == row['repo']) & (data_rev['pr_number'] == row['pr_number']), 'n_sub_file_changes'] = n_sub_file_changes
    data_rev.loc[(data_rev['repo'] == row['repo']) & (data_rev['pr_number'] == row['pr_number']), 'n_sub_additions'] = n_sub_additions
    data_rev.loc[(data_rev['repo'] == row['repo']) & (data_rev['pr_number'] == row['pr_number']), 'n_sub_deletions'] = n_sub_deletions
    data_rev.to_csv('./output/output_reviewing_at_apache.csv', index = False)
                  
    print(n_sub_commits, ' subsequent commits') 
    print(n_sub_file_changes, ' file changes') 
    print(n_sub_additions, ' added lines') 
    print(n_sub_deletions, ' deleted lines\n') 
   
   
print('Mining finished')

    
