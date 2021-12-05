#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 17:20:34 2020

"""

import json, pandas as pd, requests, time

def query_composer(project, repo, number):
    # query = 'query ($owner_query:String = ' + project + ', $repo_query:String = ' + repo + '){repository(owner:$owner_query, name:$repo_query){pullRequest(number: ' + number + '){commits {totalCount}timelineItems(itemTypes:[HEAD_REF_FORCE_PUSHED_EVENT]){totalCount}}}}'
    query = 'query ($owner_query:String = '+ project +', $repo_query:String = '+ repo +'){repository(owner:$owner_query, name:$repo_query){pullRequest(number:'+ number +'){commits {totalCount} timelineItems(last:1,itemTypes:[HEAD_REF_FORCE_PUSHED_EVENT]){totalCount nodes{... on HeadRefForcePushedEvent{beforeCommit {oid} afterCommit {oid}}}} mergeCommit {oid}}}}'
    return query
    
def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

MAX_REQUESTS = 20
DELAY = 10

# GRAPHQL API v4
#   using an access token   
#################
access_token = 'your-access-token'
headers = {'Authorization': 'Bearer '+ access_token}


################# STEP 1
# preparing data
#################
# data_rev = pd.read_csv('./input/output_ARL_at_apache.csv', low_memory = False)
# #data_rev = pd.read_csv('./results/tmp_output_apache_refactorings_review.csv', low_memory = False)
# data_rev.drop_duplicates(keep = 'first', inplace = True)
# print('\nThere are', len(data_rev), 'PRs, which have review comments, to be processed.')
# print('\nColumns of our original refactorings dataset:', list(data_rev.columns))

################# STEP 2
# creating a new column that works as a flag for initial commits
# Warning: This step should be run once
#################
# display_bar()
# data_refs = pd.read_csv('./results/output_refactorings_at_apache.csv', low_memory = False)
# data_refs.drop_duplicates(keep = 'first', inplace = True)
# print('\nColumns of our original refactorings dataset:', list(data_refs.columns))
# data_refs["initial_flag"] = False
# print('\nColumns of our updated refactorings dataset:', list(data_refs.columns))
# data_refs.to_csv('./results/output_final_refactorings_at_apache.csv', index = False)


################# STEP 3
# Checking rebased pull requests
#################

file_output = open('./output/checking-rebase.txt', 'a')

project = 'apache'
count_squashed = 0
count_commit_merged = 0
count_requests = 0
data_rev = pd.read_csv('./output/output_review_at_apache.csv', low_memory = False)

for index, row in data_rev.iterrows():    
    if (count_requests >= MAX_REQUESTS):
        count_requests = 0
        print('delaying...')
        time.sleep(DELAY)            
           
    print('\n__Result__')
    print(row['repo'], row['pr_number'])
    print(row['repo'], row['pr_number'], file = file_output)
    repo = row['repo'][7:] #excluding substring apache/
    number = row['pr_number']
    data_rev = pd.read_csv('./output/output_review_at_apache.csv', low_memory = False)

    result = run_query(query_composer(json.dumps(project), json.dumps(repo), json.dumps(number)))
    n_commits = result["data"]["repository"]['pullRequest']['commits']['totalCount']
    print('Number of PR commits:',n_commits)
    print('Number of PR commits:',n_commits, file = file_output)
    n_events = result["data"]["repository"]['pullRequest']['timelineItems']['totalCount']
    print('Number of force-push events:',n_events)
    print('Number of force-push events:',n_events, file = file_output)
    if(n_events == 0):
        count_commit_merged += 1
        print('\nThere are', len(data_rev), 'PRs in our sample.')
    else:
        try: 
            merge_commit = result["data"]["repository"]['pullRequest']['mergeCommit']['oid']
            after_commit = result["data"]["repository"]['pullRequest']['timelineItems']['nodes'][0]['afterCommit']['oid']
               
            if(n_events == 1 and after_commit == merge_commit and n_commits == 1):
                 count_squashed += 1
            else:                
                index = data_rev[(data_rev['repo'] == row['repo']) & (data_rev['pr_number'] == number)].index
                data_rev.drop(index, inplace=True)
                data_rev.to_csv('./output/output_review_at_apache.csv', index = False)
                print('\nThere are', len(data_rev), 'PRs in our sample.')
        except TypeError:
            print('None object found in', repo)
            index = data_rev[(data_rev['repo'] == row['repo']) & (data_rev['pr_number'] == number)].index
            data_rev.drop(index, inplace=True)
            data_rev.to_csv('./output/output_review_at_apache.csv', index = False)
            print('\nThere are', len(data_rev), 'PRs in our sample.')            
    count_requests += 1        

    print('\n_________________')
    print('\n_________________', file = file_output)
    print(count_squashed, 'squashed pull requests')        
    print(count_squashed, 'squashed pull requests', file = file_output)        
    print(count_commit_merged, 'pull requests merged by a commit merge\n')        
    print(count_commit_merged, 'pull requests merged by a commit merge\n', file = file_output)        
    
file_output.close()
   


    
