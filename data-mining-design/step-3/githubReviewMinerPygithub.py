# Gathering code review data from GitHub with Github3
# Created on February 20, 2020
# Main source: https://github3py.readthedocs.io

from github import Github
import csv, pandas as pd, time

MAX_REQUESTS_REPOS = 5
DELAY_REPOS = 120 # defined after a few tests

def counter_reviewers(list):
    reviewers = []
    try:
        for r in list:
            reviewers.append(r.user.name) 
        reviewers = (dict.fromkeys(reviewers))
    except AttributeError:
        print('A NoneType object has no attribute name')                
    return len(reviewers)

def get_name(input_list): #specific to attribute 'name' of a list object
    output = []
    for i in input_list:
        output.append(i.name) 
    output = (dict.fromkeys(output))
    return list(output.keys())

def mine_pr(file_in_review, file_in_review_comments, repo_name, pr_number, has_refactorings, pr):       
    if (pr.review_comments > 0) and (not was_collected(repo_name, pr_number, data_collected)): # (was_collected() - in need of re-running; remember to comment the lines of the output files's header
        row = [repo_name, pr_number, has_refactorings, pr.changed_files, counter_reviewers(pr.get_review_comments()), pr.comments + pr.review_comments, pr.comments, pr.review_comments, pr.additions, pr.deletions, pr.created_at, pr.merged_at, pr.title, get_name(pr.get_labels())]
        save_to_file(file_in_review, row)                
        for r in pr.get_review_comments():
            row = [repo_name, pr_number, has_refactorings, r.original_commit_id, r.id, r.in_reply_to_id, r.diff_hunk, r.body, r.created_at, pr.created_at]
            save_to_file(file_in_review_comments, row)                   
        print(time.ctime() + ': {} PR {} was processed...'.format(repo_name, pr_number))
    else:
        print(time.ctime() + ': {} PR {} was already processed or it does not review comments...'.format(repo_name, pr_number))
    return 

def save_to_file(file, row):
    with open(file, 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)            
    csvFile.close()
    return

def was_collected(repo, pr, df):        
    # Delete these row indexes from dataFrame
    indexNames = df[(df['repo'] == repo) & (df['pr_number'] == pr)].index
    df.drop(indexNames, inplace = True)

    if(len(indexNames) != 0): 
        return True
    return False


################# STEP 1
# REST API v3
#   using username and password
    
miner = Github("youruser", "yourpassword")


################# STEP 2
# data is grouped by repository, pr_number, after dropping duplicates and PRs that have only one commit
#################

data_refactorings = pd.read_csv('./data/output_refactorings_at_apache.csv', low_memory = False)
data_refactorings.drop_duplicates(keep = 'first', inplace = True)
data = data_refactorings.groupby(["repo", "pr_number"]).filter(lambda x: len(x) > 1)

data_grouped = data.groupby(["repo", "pr_number"])
print('There are ' + str(len(data_grouped)) + ' PRs to be processed...')

################# STEP 3
# mining GitHub to each repository, pr_number
#################

file_output_review = './results/refactorings_at_apache_output_review.csv'
file_output_review_comments = './results/refactorings_at_apache_output_review_comments.csv'
save_to_file(file_output_review, ['repo', 'pr_number', 'has_refactorings', 'n_changed_files', 'n_reviewers', 'length_discussion', 'n_comments', 'n_review_comments', 'n_additions', 'n_deletions', 'created_at', 'merged_at', 'pr_title', 'pr_labels'])
save_to_file(file_output_review_comments, ['repo', 'pr_number', 'has_refactorings', 'original_commit', 'review_comment_id', 'in_reply_to_id', 'diff_hunk', 'review_comment_body', 'review_comment_created_at', 'pr_created_at'])

data_collected = pd.read_csv('./results/refactorings_at_apache_output_review.csv', low_memory = False)

count_requests = 0
for pair, group in data_grouped:             
#    pair[0] = project/repository
#    pair[1] = pr_number                
    repo = miner.get_repo(pair[0])    
    pr = repo.get_pull(int(pair[1]))    
    
    # verifying if the PR has performed refactorings
    has_refactorings = False
    for idx, row in group.iterrows():
        if not (pd.isna(row['refactoring_type'])):
            has_refactorings = True            
            break        
    try:
        mine_pr(file_output_review, file_output_review_comments, str(pair[0]), int(pair[1]), has_refactorings, pr)
        count_requests += 1
        print()
        if count_requests == MAX_REQUESTS_REPOS:
            print('delaying...')
            time.sleep(DELAY_REPOS)
            count_requests = 0                           
    except ConnectionError:
        print('A connection-level exception occurred')
        continue    
        
print('The processed has finished...')
