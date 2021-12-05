#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Mining data from GitHub with PyGithub (REST API v3) and Requests (GraphQL API v4)
# Created on August 7th, 2019
# Main sources: https://developer.github.com/v3/
#               https://developer.github.com/v4/
#               https://pygithub.readthedocs.io 
#               https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad


from github import Github, RateLimitExceededException
import csv, json, os.path, pandas as pd, requests, time

MAX_REQUESTS_REPOS = 500
DELAY_REPOS = 60 # defined after a few tests

MAX_REQUESTS_COMMITS = 100
DELAY_COMMITS = 300 # defined after a few tests

def collect_merged_prs_from_repo(project, repo):             
    try:
        save_to_file(file_name_composer(repo), 'repo', 'pr_number', 'before_commit', 'after_commit')
        result = run_query(query_composer(json.dumps(project), json.dumps(repo)))            
        print("Number of merged prs:", result["data"]["repository"]["pullRequests"]["totalCount"])
        collect_push_events(result, json.dumps(repo))                
        while True:   
            if (result["data"]["repository"]["pullRequests"]["pageInfo"]["hasNextPage"]) == False:
                break
            result = run_query(query_composer(json.dumps(project), json.dumps(repo), json.dumps(result["data"]["repository"]["pullRequests"]["pageInfo"]["endCursor"])))
            collect_push_events(result, json.dumps(repo))
    except KeyError:
        print('Merged PRs not found in', repo)           
    return

def collect_push_events(result, repo):
    before_commit = after_commit = ""
    for pr in result["data"]["repository"]["pullRequests"]["edges"]:
        pr_number = pr["node"]["number"]                
        try:         
            for i in pr["node"]["timelineItems"]["nodes"]:
                after_commit = i["afterCommit"]["commitUrl"]                    
                before_commit = i["beforeCommit"]["commitUrl"]
        except TypeError:
            print('None object found in', repo)
        save_to_file(file_name_composer(json.loads(repo)), repo, pr_number, before_commit, after_commit)
        before_commit = after_commit = ""    
    return

def count_merged_prs_from_repo(file):
    with open(file, 'r') as csvfile:
        csv_dict = [row for row in csv.DictReader(csvfile)]
        return(len(csv_dict))

def create_list_of_repositories(repos):    
    try:
        repos_list = []
        count_requests = 0
        for r in repos:            
            repos_list.append(r.name)            
            if count_requests == MAX_REQUESTS_REPOS:
                print('delaying...')
                time.sleep(DELAY_REPOS)
            count_requests += 1            
    except RateLimitExceededException:
        print('GitHub API rate limit exceeded...')
    return repos_list

def extract_commit_sha(commit_url):
    start = commit_url.find('commit/')    
    return commit_url[start+7:len(commit_url)]
    
def extract_repo_name(file):
    start = file.find('prs_')
    end = file.find('.csv', start)    
    return file[start+4:end]

def file_name_composer(repo):  
    return './data/merged_prs_' + repo + '.csv'

def gather_merged_prs(project, repo_list):    
    try:
        for r in repo_list:
            if os.path.exists(file_name_composer(r)):
                print('Merged PRs have already collected for', r)
                continue
            collect_merged_prs_from_repo(project, r)
            print('delaying...')
            time.sleep(DELAY_REPOS)
            print('Merged PRs collected from', "Apache/"+r)
    except RateLimitExceededException:
        print('GitHub API rate limit exceeded...')
    return

def gather_repositories(user):
    query_user = 'user:' + user + ' language:java archived:false'
    return g.search_repositories(query = query_user, sort = 'updated')

def is_empty_file(file):
    with open(file, 'r') as csvfile:
        csv_dict = [row for row in csv.DictReader(csvfile)]
        if len(csv_dict) == 0:            
            return True
    return False

def list_repositories_to_process():
    repos = []
    for f in os.listdir("./data"):    
        file = "./data/" + f
        if (is_empty_file(file) == False):
            repos.append(file)  
    return repos

def process_commits(project, file_in):
    file_out = './process/all_commits_to_process.csv'  
    save_to_file(file_out, "repo_url", "pr_number", "commit") 
    file_out_prs = './process/prs_to_process.csv'          
    count_requests = 0
    with open(file_in, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)         
        count_commits = 0  
        try:
            for row in csv_reader: 
                if (count_requests == MAX_REQUESTS_COMMITS):
                    print('delaying...')
                    time.sleep(DELAY_COMMITS)
                    count_requests = 0                                               
                repo = g.get_repo(repos_full_name_composer(project, row["repo"]))                        
                after_parents = repo.get_commit(row["after_commit"]).parents 
                if (len(after_parents) == 1):
                    # after's parent, before
                    for c in repo.compare(after_parents[0].sha, row["before_commit"]).commits:
                        save_to_file(file_out, row["repo_url"], row["pr_number"], c.sha)     
                        count_commits += 1
                    print(count_commits, 'commits were selected')                
                    count_requests += 1
                else:
                    print("Warning> There are", len(after_parents),"after_commits' parents!")                
                    save_to_file(file_out_prs, row["repo_url"], row["pr_number"])                         
        except RateLimitExceededException:
            print('GitHub API rate limit exceeded...')
    return count_commits

def process_repositories(project, repos):
    count_processed = 0
    file_prs = './process/prs_to_process.csv'
    save_to_file(file_prs, "repo_url", "pr_number")
    file_commits = './process/commits_to_pre_process.csv'
    save_to_file(file_commits, "repo", "pr_number", "repo_url", "before_commit", "after_commit")
    for r in repos:
        count_processed += read_from_file_and_write_to_process(project, r, file_prs, file_commits)
    return count_processed

def query_composer(project, repo, start_in = None):
    if (start_in == None):
        query = 'query ($owner_query:String = ' + project + ', $repo_query:String = ' + repo + ', $after_var:String){repository(owner:$owner_query, name:$repo_query) {pullRequests(first:100, after:$after_var, orderBy:{field:CREATED_AT, direction:DESC},states:MERGED) {totalCount edges {node {number timelineItems(last:1, itemTypes:[HEAD_REF_FORCE_PUSHED_EVENT]) {nodes{__typename ... on HeadRefForcePushedEvent{beforeCommit {commitUrl} afterCommit {commitUrl}}}}}}pageInfo {hasNextPage endCursor }}}}'
    else:
        query = 'query ($owner_query:String = ' + project + ', $repo_query:String = ' + repo + ', $after_var:String = ' + start_in +'){repository(owner:$owner_query, name:$repo_query) {pullRequests(first:100, after:$after_var, orderBy:{field:CREATED_AT, direction:DESC},states:MERGED) {totalCount edges {node {number timelineItems(last:1, itemTypes:[HEAD_REF_FORCE_PUSHED_EVENT]) {nodes{__typename ... on HeadRefForcePushedEvent{beforeCommit {commitUrl} afterCommit {commitUrl}}}}}}pageInfo {hasNextPage endCursor }}}}'
    return query

def read_from_file_and_write_to_process(project, file_in, file_out_prs, file_out_commits):    
    repo_url = "https://www.github.com/" + project + '/' + extract_repo_name(file_in) + '.git'
    with open(file_in, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)         
        line_count = 0
        for row in csv_reader:            
            if (row["before_commit"] == "" and row["after_commit"] == "") or (row["before_commit"] == ""): # to deal with "true merge"
                save_to_file(file_out_prs, repo_url, row["pr_number"])
            else:                
                save_to_file(file_out_commits, row["repo"], row["pr_number"], repo_url, extract_commit_sha(row["before_commit"]), extract_commit_sha(row["after_commit"]))
            line_count += 1                       
    return line_count

def read_from_file_to_filter(file_in):
    data = pd.read_csv(file_in)    
    filtered_commits = data.groupby(["repo_url", "pr_number"]).filter(lambda x: len(x) > 1)
    filtered_commits.to_csv('./process/commits_to_process.csv', encoding = 'utf-8', index = False)
    return len(filtered_commits)

def record_result_merged_prs_by_repository(project, repos):
    number_merged_prs = 0
    save_to_file('./results/number_merged_prs_by_repository.csv', 'repo', 'number_merged_prs')
    for r in repos:
        repo_full_name = project + '/' + extract_repo_name(r)
        number_merged_prs += count_merged_prs_from_repo(r)    
        save_to_file('./results/number_merged_prs_by_repository.csv', repo_full_name, count_merged_prs_from_repo(r))
    return number_merged_prs

def repos_full_name_composer(project, repo):
    return project + '/' + json.loads(repo)

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def save_to_file(file, firstcolumn, secondcolumn = None, thirdcolumn = None, fourthcolumn = None, fifthcolumn = None, sixthcolumn = None):
    if (secondcolumn == None and thirdcolumn == None and fourthcolumn == None and fifthcolumn == None and sixthcolumn == None):
        row = [firstcolumn]
    elif (thirdcolumn == None and fourthcolumn == None and fifthcolumn == None and sixthcolumn == None):
        row = [firstcolumn, secondcolumn]        
    elif (fourthcolumn == None and fifthcolumn == None and sixthcolumn == None):
        row = [firstcolumn, secondcolumn, thirdcolumn]        
    elif (fifthcolumn == None and sixthcolumn == None):
        row = [firstcolumn, secondcolumn, thirdcolumn, fourthcolumn]        
    elif (sixthcolumn == None):
        row = [firstcolumn, secondcolumn, thirdcolumn, fourthcolumn, fifthcolumn]        
    else:
        row = [firstcolumn, secondcolumn, thirdcolumn, fourthcolumn, fifthcolumn, sixthcolumn]
    with open(file, 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)            
    csvFile.close()
    return


################# STEP 1
# REST API v3
#   using username and password
g = Github("youruser", "yourpassword")
  
# GRAPHQL API v4
#   using an access token   
#################
access_token = '8a4e398d1f865c0c37f6aad04610165ab42bb75f'
headers = {'Authorization': 'Bearer '+ access_token}


################# STEP 2
# gathering public repositories from the selected GitHub projects
#################
project = 'apache'
repos_apache = gather_repositories(project) 
print('There are', repos_apache.totalCount, 'repositories!')


################# STEP 3
# gathering all merged PRs from the repositories
#################
repositories_list = create_list_of_repositories(repos_apache) 
print('A list of', len(repositories_list), 'repositories were created!')
gather_merged_prs(project, repositories_list)
print('Merged PRs collected!')


################# STEP 4
# excluding repositories with no merged PRs
#################
repositories_to_process = list_repositories_to_process()
print('There are', len(repositories_to_process), project +'\'s repositories for investigation')


################# STEP 5
# saving the number of merged PRs by repository 
#   output: ./results/number_merged_prs_by_repository.csv
#################
number_merged_prs_to_process = record_result_merged_prs_by_repository(project, repositories_to_process)
print('There are', number_merged_prs_to_process, 'merged PRs for investigation')


################# STEP 6
# preprocessing all merged PRs, classifying them in order to RefactoringMiner's refactoring detection (by PR number or commit SHA)
#   output: ./process/commits_to_pre_process.csv 
#           ./process/prs_to_process.csv
#################
number_processed_merged_prs = process_repositories(project, repositories_to_process)
print(number_processed_merged_prs, project + '\'s merged PRs were preprocessed')


################# STEP 7
# searching for all commits to the RefactoringMiner's refactoring detection (by commit SHA)
#   output: ./process/all_commits_to_process.csv 
#################
number_selected_commits = process_commits(project, './process/commits_to_pre_process.csv')
print(number_selected_commits, project + '\'s commits were selected')


################# STEP 8
# filtering PRs in order to select PRs that have more than two commits
#   output: ./process/commits_to_process.csv 
#################
number_filtered_commits = read_from_file_to_filter('./process/all_commits_to_process.csv')
print(number_filtered_commits, project + '\'s commits were selected')

print('Mining of'+ project + 'project on GitHub finished!')
