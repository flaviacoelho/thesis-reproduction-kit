#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 14:46:58 2020

"""

import pandas as pd, requests, json

def drop_unnamed_columns(data):
    data.drop([col for col in data.columns if "Unnamed" in col], axis = 1, inplace = True)
    return

def extract_repo_name(project, repo):
    start = repo.find(project+'/')    
    return repo[start + len(project) + 1:]

def query_composer(project, repo):
    return 'query ($owner_query: String = ' + project + ', $repo_query: String = ' + repo + ') {repository(owner: $owner_query, name: $repo_query) {isMirror mirrorUrl}}'

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


project = 'apache'

################# STEP 0
# GRAPHQL API v4
#   using an access token   
#################
access_token = 'your-access-token'
headers = {'Authorization': 'Bearer '+ access_token}

################# STEP 1
# dropping duplicates
#################
data_review = pd.read_csv('./results/refactorings_at_apache_output_review.csv', low_memory = False)
print(data_review)
data_review.drop_duplicates(keep = 'first', inplace = True)
print('There are', len(data_review), 'PRs, which have review comments, to be processed.')

data_review_comments = pd.read_csv('./results/refactorings_at_apache_output_review_comments.csv', low_memory = False)
print(data_review_comments)
data_review_comments.drop_duplicates(keep = 'first', inplace = True)
print('There are', len(data_review_comments), 'review comments to be processed.')


################# STEP 2
# dropping unnamed columns from dataframes
#   It is used in case of addition of extra columns, after pandas read_csv execution  
#################
drop_unnamed_columns(data_review)
drop_unnamed_columns(data_review_comments)


################# STEP 3
# checking if there are mirror repositories
#################
data_repo = data_review.groupby(['repo'])
has_mirror = False
for r in data_repo:
    result = run_query(query_composer(json.dumps(project), json.dumps(extract_repo_name(project, r[0]))))
    if(result["data"]["repository"]["isMirror"] == True):
        has_mirror = True
        print('URL: ' + result["data"]["repository"]["mirrorUrl"])
if (has_mirror):
    print('\nThere are mirror repositories')
else:
    print('\nThere are no mirror repositories')


################# STEP 4
# dropping PRs that have 0 (zero) reviewers (due user undefined)
#################
zero_reviewers = data_review[data_review.n_reviewers == 0]
print(zero_reviewers.iloc[:,[0,1]])
data_review = data_review[data_review.n_reviewers != 0]
print('\nAfter dropping PRs that have 0 reviewers, there are', len(data_review), 'PRs, which have review comments, to be processed.')
data_review_comments = data_review_comments.loc[~((data_review_comments.repo.isin(zero_reviewers['repo'])) & (data_review_comments.pr_number.isin(zero_reviewers['pr_number']))),:]
print('After dropping PRs that have 0 reviewers, there are', len(data_review_comments), 'review comments to be processed.')


################# STEP 5
# dropping PRs that have 0 (zero) changed files 
#################
zero_changed_files = data_review[data_review.n_changed_files == 0]
print(zero_changed_files.iloc[:,[0,1]])
data_review = data_review[data_review.n_changed_files != 0]
print('\nAfter dropping PRs that have 0 changed files, there are', len(data_review), 'PRs, which have review comments, to be processed.')
data_review_comments = data_review_comments.loc[~((data_review_comments.repo.isin(zero_changed_files['repo'])) & (data_review_comments.pr_number.isin(zero_changed_files['pr_number']))),:]
print('After dropping PRs that have 0 changed files, there are', len(data_review_comments), 'review comments to be processed.')

print('Number of repositories:', len(data_review.groupby(['repo'])))  
print(data_review['repo'].describe())
print(data_review['repo'].value_counts())

################# STEP 6
# saving the final version of dataframes
#################
data_review.to_csv('./results/step1-phase2/output_apache_refactorings_review.csv', encoding = 'utf-8', index = False)
data_review_comments.to_csv('./results/step1-phase2/output_apache_refactorings_review_comments.csv', encoding = 'utf-8', index = False)

print('\nThis process has finished...')
