#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 17:20:34 2020

"""

import json, pandas as pd, requests, time
from datetime import datetime as dt
from functions import display_bar

def query_composer(project, repo, commit):
    query = 'query{repository(owner:' + project +', name: ' + repo + ') {object(oid: ' + commit + ') {... on Commit {authoredDate}}}}'
    return query
    
def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section
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
data_rev = pd.read_csv('./input/input_reviewing_at_apache.csv', low_memory = False)
data_rev.drop_duplicates(keep = 'first', inplace = True)
print('\nThere are', len(data_rev), 'PRs, which have review comments, to be processed.')

################# STEP 2
# creating a new column that works as a flag for initial commits
# Warning: This step should be run once
#################
# display_bar()
# data_refs = pd.read_csv('./input/input_refactorings_at_apache.csv', low_memory = False)
# data_refs.drop_duplicates(keep = 'first', inplace = True)
# print('\nColumns of our original refactorings dataset:', list(data_refs.columns))
# data_refs["initial_flag"] = False
# print('\nColumns of our updated refactorings dataset:', list(data_refs.columns))
# data_refs.to_csv('./output/output_final_refactorings_at_apache.csv', index = False)


################# STEP 3
# Mining authoredDate of our sample's commits
#################

data_rev['created_at'] = pd.to_datetime(data_rev['created_at'])
project = 'apache'
display_bar()
count_requests = 0
for index, row in data_rev.iterrows():
    print(row['repo'], row['pr_number'])
    repo = row['repo'][7:] #excluding substring apache/
    pr_created_at = row['created_at']
    data_refs = pd.read_csv('./output/output_final_refactorings_at_apache.csv', low_memory = False)
    group_commits = data_refs[(data_refs['repo'] == row['repo']) & (data_refs['pr_number'] == row['pr_number'])].groupby(['commit'], sort = False)
    count_initial = 0
    n_commits = len(group_commits)
    first = True
    for index, row_c in group_commits:
        try:        
            if (first == True):
                count_requests = n_commits
                first = False
                
            if (count_requests < MAX_REQUESTS):
                result = run_query(query_composer(json.dumps(project), json.dumps(repo), json.dumps(index)))
                authored_date = dt.strptime(result["data"]["repository"]["object"]["authoredDate"], "%Y-%m-%dT%H:%M:%SZ")
                       
                if authored_date < pr_created_at:
                    data_refs.loc[(data_refs['repo'] == row['repo']) & (data_refs['pr_number'] == row['pr_number']) & (data_refs['commit'] == index), 'initial_flag'] = True
                    data_refs.to_csv('./output/output_final_refactorings_at_apache.csv', index = False)
                    count_initial += 1
                if (first == False):
                    count_requests += 1
            else:
                count_requests = 0
                print('delaying...')
                time.sleep(DELAY)            
        except TypeError:
            print('A type error occurred...')
            continue

    print(count_initial, 'initial commits\n')    
   


    
