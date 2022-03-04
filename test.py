import csv
import json

import utils.get_code_find_missed as get_code_find_missed

def test1():
    with open('/Users/a057/Desktop/extensions-2021.json','r') as f:
        full_list=json.load(f)
    res=[]
    for item in full_list:
        tmp=[item['name'],20]
        res.append(tmp)

    with open('/Users/a057/Desktop/full-names.csv','w') as f:
        writer=csv.writer(f)
        writer.writerows(res)

def dropbox_test():

    full_list_file='/Users/a057/Desktop/extensions-2021.json'
    browser='chrome'
    log_file='./download_log.txt'
    get_code_find_missed.download_ext_by_file_store_in_dropbox(full_list_file, browser, log_file)


dropbox_test()