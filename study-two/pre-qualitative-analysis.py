
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:23:11 2020

"""
import numpy as np, pandas as pd

def display_bar(filename = None):
    if (filename == None):
        print("\n____________________________________________________")
    else:
        print("\n____________________________________________________", file = filename)
    return

def add_category(riprs, non_riprs):
    review_riprs = riprs.loc[riprs.index]
    review_riprs['category'] = 'refactoring-inducing PR'
    review_non_riprs = non_riprs.loc[non_riprs.index]
    review_non_riprs['category'] = 'non-refactoring-inducing PR'
    return review_riprs, review_non_riprs

def create_spreadsheet(result, file_name):
    spreadsheet = pd.DataFrame(columns=['inspector','repo', 'pr_number','category', 'pr_url','commit','commit_url','initial_flag','refactoring_type','refactoring_detail','confirmed_refactoring_flag','covered_refactoring_flag','floss_refactoring_flag','direct_review_comment_flag','discussion_flag','notes'])
    url = "https://github.com/"
    
    data_refs = pd.read_csv('./input/input_refactorings_apache.csv', low_memory = False)    
    for index, row in result.iterrows():
        pr_url = url + row['repo'] + '/pull/' + str(row['pr_number'])
        print(pr_url)
        group_commits = data_refs[(data_refs['repo'] == row['repo']) & (data_refs['pr_number'] == row['pr_number'])]
        for index,row_c in group_commits.iterrows():
            commit_url = url + row['repo'] + '/commit/' + row_c['commit']
            new_row = {'inspector':'', 'repo':row['repo'],'pr_number':row['pr_number'],
                      'category':row['category'],'pr_url':pr_url,'commit':row_c['commit'],
                      'commit_url':commit_url,'initial_flag':row_c['initial_flag'],
                      'refactoring_type':row_c['refactoring_type'],
                      'refactoring_detail':row_c['refactoring_detail'],
                      'confirmed_refactoring_flag':'','covered_refactoring_flag':'',
                      'floss_refactoring_flag':'','direct_review_comment_flag':'',
                      'discussion_flag':'','notes':''}
            spreadsheet = spreadsheet.append(new_row, ignore_index=True)
    
    spreadsheet.to_csv('./output/'+ file_name + '.csv', index = False)
    return

def generate_sample_one(data_review):

    display_bar()
    print('Describing number of reviewers of our sample')
    print(data_review['n_reviewers'].describe())

    display_bar()
    data_2_reviewers = data_review.loc[data_review['n_reviewers'] == 2]
    print('PRs with 2 reviewers')
    print(data_2_reviewers)
    
    display_bar()
    data_2_reviewers_riprs = data_2_reviewers.loc[data_2_reviewers['has_refactorings'] == True]
    print('There are', len(data_2_reviewers_riprs), 'RIPRs with 2 reviewers')
    
    display_bar()
    data_2_reviewers_non_riprs = data_2_reviewers.loc[data_2_reviewers['has_refactorings'] == False]
    print('There are', len(data_2_reviewers_non_riprs), 'non-RIPRs with 2 reviewers')
    
    display_bar()
    print('Describing number of review comments in PRs with 2 reviewers')
    print(data_2_reviewers_riprs['n_review_comments'].describe())
    print(data_2_reviewers_non_riprs['n_review_comments'].describe())
    
    display_bar()
    data_2_reviewers_5_review_comments = data_2_reviewers.loc[data_2_reviewers['n_review_comments'] == 5]
    print('PRs with 2 reviewers and 5 review comments')
    print(data_2_reviewers_5_review_comments)
    
    display_bar()
    data_2_reviewers_5_review_comments_riprs = data_2_reviewers_5_review_comments.loc[data_2_reviewers_5_review_comments['has_refactorings'] == True]
    print('There are', len(data_2_reviewers_5_review_comments_riprs), 'RIPRs with 2 reviewers and 5 review comments')
    print(data_2_reviewers_5_review_comments_riprs)
    
    display_bar()
    data_2_reviewers_5_review_comments_non_riprs = data_2_reviewers_5_review_comments.loc[data_2_reviewers_5_review_comments['has_refactorings'] == False]
    print('There are', len(data_2_reviewers_5_review_comments_non_riprs), 'non-RIPRs with 2 reviewers and 5 review comments')
    
    display_bar()
    data_riprs = data_2_reviewers_5_review_comments_riprs.sample(n = SAMPLE_SIZE)
    data_non_riprs = data_2_reviewers_5_review_comments_non_riprs.sample(n = SAMPLE_SIZE)
    
    data_review_riprs, data_review_non_riprs = add_category(data_riprs, data_non_riprs)
    
    data_review_result = pd.DataFrame()   
    data_review_result = data_review_result.append(data_review_riprs, ignore_index=True)
    data_review_result = data_review_result.append(data_review_non_riprs, ignore_index=True)
    print(data_review_result)
    
    display_bar()
    create_spreadsheet(data_review_result, 'sample1/sample_1_spreadsheet')  
    return


def generate_sample_two(data_review):    
    display_bar()
    data_1_subcommit = data_review.loc[data_review['n_sub_commits'] == 1]
    print('PRs with 1 subsequent commit')
    print(data_1_subcommit)
        
    display_bar()
    data_1_subcommit_riprs = data_1_subcommit.loc[data_1_subcommit['has_refactorings'] == True]
    print('There are', len(data_1_subcommit_riprs), 'RIPRs with 1 subsequent commit')
    
    display_bar()
    data_1_subcommit_non_riprs = data_1_subcommit.loc[data_1_subcommit['has_refactorings'] == False]
    print('There are', len(data_1_subcommit_non_riprs), 'non-RIPRs with 1 subsequent commit')

    display_bar()
    print('Describing number of review comments in PRs with 1 subsequent commit')
    print(data_1_subcommit_riprs['n_review_comments'].describe())
    print(data_1_subcommit_non_riprs['n_review_comments'].describe())

    display_bar()
    data_1_subcommit_1_refactoring = data_1_subcommit_riprs.loc[data_1_subcommit_riprs['n_refactorings'] == 1]
    print('RIPRs with 1 subsequent commit and 1 refactoring edit')
    print(data_1_subcommit_1_refactoring)
    
    display_bar()
    data_riprs = data_1_subcommit_1_refactoring.sample(n = SAMPLE_SIZE)
    data_non_riprs = data_1_subcommit_non_riprs.sample(n = SAMPLE_SIZE)
    
    data_review_riprs, data_review_non_riprs = add_category(data_riprs, data_non_riprs)
        
    data_review_result = pd.DataFrame()   
    data_review_result = data_review_result.append(data_review_riprs, ignore_index=True)
    data_review_result = data_review_result.append(data_review_non_riprs, ignore_index=True)
    print(data_review_result)
    
    display_bar()
    create_spreadsheet(data_review_result, 'sample2/sample_2_spreadsheet')        

    return


def collect_riprs(riprs, refactorings, matches):
        
    count_matches = 0  
    
    data_review_result = pd.DataFrame()    
    
    for index, row in riprs.iterrows():
        display_bar()
        print(row['repo'], row['pr_number'])
  
        commits = refactorings[(refactorings['repo'] == row['repo']) & (refactorings['pr_number'] == row['pr_number'])].groupby(['commit'], sort = False)

        match = False
        for pair, group in commits:              
            if (match == True):
                match = False
                count_matches += 1
                index_pr = data_review.loc[(data_review['repo'] == row['repo']) & (data_review['pr_number'] == row['pr_number'])].index.values
                data_review_result = data_review_result.append(data_review.iloc[index_pr], ignore_index=True)
                break

            if (group['initial_flag'].all() == False):   
                for c in group['refactoring_type']:  
                    if any(x in c for x in matches):
                        match = True
                        print(c)
                        break
                        
        print('PRs that contain one of the matches:',count_matches)
    
    print(data_review_result)
    
    return data_review_result


def display_refactorings(data_review_result, refactorings, matches):
    
    for index, row in data_review_result.iterrows():
        display_bar()
        print(row['repo'], row['pr_number'])
  
        commits = refactorings[(refactorings['repo'] == row['repo']) & (refactorings['pr_number'] == row['pr_number'])].groupby(['commit'], sort = False)

        for pair, group in commits:                          
            if (group['initial_flag'].all() == False):   
                for c in group['refactoring_type']:                                          
                    if any(x in c for x in matches):
                        print(c)
    return


def pre_generate_sample_three(data_review):
    
    riprs = data_review.loc[data_review['has_refactorings'] == True]
    
    refactorings = pd.read_csv('./input/input_refactorings_apache.csv', low_memory = False)
    refactorings["refactoring_type"].fillna("No refactoring", inplace = True)
    refactorings['refactoring_type'] = refactorings['refactoring_type'].str.upper()
    
    matches = ['Pull Up Method'.upper(),'Pull Up Attribute'.upper(),
               'Push Down Method'.upper(),'Push Down Attribute'.upper(),
               'Extract Superclass'.upper(),'Extract Interface'.upper(),
               'Move Class'.upper(),'Move and Rename Class'.upper(),
               'Extract Class'.upper(),'Extract Subclass'.upper(),
               'Move and Rename Attribute'.upper()]    
    
    # It should be run once!    
    data_review_result = collect_riprs(riprs, refactorings, matches)    
    raise SystemExit()

    display_refactorings(data_review_result, refactorings, matches)
    data_review_result.to_csv('./output/sample3/'+ 'sample_riprs.csv', index = False)
    # manual inspection of refactorings in order to compose a purposive sample of refactoring-inducing PRs
    # now, sample_riprs.csv consists of the selected refactoring-inducing PRs

    return


def generate_sample_three(data_review):
    
    SAMPLE_3_SIZE = 13
    
    display_bar()
    data_riprs = pd.read_csv('./output/sample3/phase1/pre_sample_riprs.csv', low_memory = False)
    
    print('Describing number of review comments in refactoring-inducing PRs')
    print(data_riprs['n_review_comments'].describe())
    
    non_riprs = data_review.loc[data_review['has_refactorings'] == False]
    non_riprs_10_review_comments = non_riprs.loc[non_riprs['n_review_comments'] == 10]
    print(non_riprs_10_review_comments)

    data_non_riprs = non_riprs_10_review_comments.sample(n = SAMPLE_3_SIZE)
    
    data_review_riprs, data_review_non_riprs = add_category(data_riprs, data_non_riprs)
        
    data_review_result = pd.DataFrame()   
    data_review_result = data_review_result.append(data_review_riprs, ignore_index=True)
    data_review_result = data_review_result.append(data_review_non_riprs, ignore_index=True)
    print(data_review_result)
    
    display_bar()
    create_spreadsheet(data_review_result, 'sample3/sample_3_spreadsheet')        
    
    return


def display_refactorings_all(data_review_result, refactorings):    
    file_output = open('./output/sample4/output_refactorings.txt','a')  
    for index, row in data_review_result.iterrows():
        display_bar(file_output)
        print(row['repo'], row['pr_number'], file = file_output)
  
        commits = refactorings[(refactorings['repo'] == row['repo']) & (refactorings['pr_number'] == row['pr_number'])].groupby(['commit'], sort = False)

        for pair, group in commits:                          
            if (group['initial_flag'].all() == False):  
                print(group['commit'], '\n', group['refactoring_type'], file = file_output)
                
    return


def detect_outliers(data):
    # Source: https://onestopdataanalysis.com/python-outlier-detection/
    # find q1 and q3 values
    q1, q3 = np.percentile(sorted(data), [25, 75])
     # compute IRQ
    iqr = q3 - q1
    # find lower and upper bounds
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    outliers = [x for x in data if x <= lower_bound or x >= upper_bound]

    return outliers


def pre_generate_sample_four(data_review):    
    riprs = data_review.loc[data_review['has_refactorings'] == True]
    riprs = riprs.loc[data_review['n_refactorings'] != 1]    
    refactorings = pd.read_csv('./input/input_refactorings_apache.csv', low_memory = False)
    
    # It should be run once!
    display_refactorings_all(riprs, refactorings)
    
    # After a manual inspection of refactoring-inducing PRs, that consist of 
    # distinct sequence of refactoring edits, ./output/sample4/pre_sample_4_riprs.csv contains
    # sample 4
    return


def generate_sample_four(data_review):
    SAMPLE_4_SIZE = 26
    
    display_bar()
    data_riprs = pd.read_csv('./output/sample4/phase1/pre_sample4_riprs.csv', low_memory = False)
    
    print('Describing number of review comments in refactoring-inducing PRs')
    print(data_riprs['n_review_comments'].describe())
        
    non_riprs = data_review.loc[data_review['has_refactorings'] == False]
    non_riprs_7_review_comments = non_riprs.loc[non_riprs['n_review_comments'] == 7]
    print(non_riprs_7_review_comments)

    data_non_riprs = non_riprs_7_review_comments.sample(n = SAMPLE_4_SIZE)
    
    data_review_riprs, data_review_non_riprs = add_category(data_riprs, data_non_riprs)
        
    data_review_result = pd.DataFrame()   
    data_review_result = data_review_result.append(data_review_riprs, ignore_index=True)
    data_review_result = data_review_result.append(data_review_non_riprs, ignore_index=True)
    print(data_review_result)
    
    display_bar()
    create_spreadsheet(data_review_result, 'sample4/sample_4_spreadsheet')        
    return


SAMPLE_SIZE = 10
# preparing data for qualitative analysis

display_bar()
data_review = pd.read_csv('./input/output_reviewing_apache.csv', engine = 'python', encoding = 'ISO-8859-1')
print('\nThere are', len(data_review), 'PRs in our sample')
print('\t*',len(data_review.loc[data_review['has_refactorings'] == True]),'refactoring-inducing PRs: {:.1%}'.format(len(data_review.loc[data_review['has_refactorings'] == True])/len(data_review)))
print('\t*',len(data_review.loc[data_review['has_refactorings'] == False]),'non-refactoring-inducing PRs: {:.1%}'.format(len(data_review.loc[data_review['has_refactorings'] == False])/len(data_review)))

# generating a purposive sample for each round
generate_sample_one(data_review)

generate_sample_two(data_review)

pre_generate_sample_three(data_review)
generate_sample_three(data_review)

pre_generate_sample_four(data_review)
generate_sample_four(data_review)

print('\nSample selected!')
