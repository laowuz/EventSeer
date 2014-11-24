#! /usr/bin/python

import os,zipfile,cPickle,json
from datetime import date
from datetime import timedelta

#url = r'gdelt.utdallas.edu/data/dailyupdates/'
url_d = r'data.gdeltproject.org/events/'
dir = r'../data/dailyupdates/'
source_dir = r'../data/newssource/'

def download_dailyupdates(start_date,end_date):
    d = start_date
    while d <= end_date:
        url_zip = url_d + str(d).replace('-','') + '.export.CSV.zip'
        os.system('wget -P ../data/dailyupdates/ '+url_zip)
        d = d + timedelta(1)

def crawl_source(start_date, end_date):
    d = start_date
    while d <= end_date:
        sd = str(d).replace('-','')
        zf = zipfile.ZipFile(dir + sd + '.export.CSV' + '.zip','r')
        url_set = set()
        if not os.path.exists(source_dir+sd):
            os.system('mkdir '+source_dir+sd)
        else:
            break
        lines = zf.read(sd+'.export.CSV').strip().split('\n')
        for ln in lines:
            id = ln.split()[0]
            url = ln.split()[-1]
            if url not in url_set:
                url_set.add(url)
            os.system('wget -T 5 -t 2 -O '+source_dir+sd+'/'+id+'.html '+url)
        d = d + timedelta(1)

def get_gdelt_urls():
    dic = {}
    dic_url = {}
    start_date = date(2013,4,1)
    end_date = date(2013,12,3)
    d = start_date
    while d <= end_date:
        print d
        sd = str(d).replace('-','')
        zf = zipfile.ZipFile(dir + sd + '.export.CSV' + '.zip', 'r')
        url_set = set()
        lines = zf.read(sd+'.export.CSV').strip().split('\n')
        for ln in lines:
            id = ln.split()[0]
            url = ln.split()[-1]
            if url not in url_set:
                url_set.add((id,url))
        dic[sd] = url_set
        d = d + timedelta(1)
    out = open('gdelt_urls_dic.pkl','wb')
    cPickle.dump(dic,out)
    out.close()

def url_match_gdelt_and_wiki_bing():
    f = open('gdelt_urls_dic.pkl','rb')
    gdelt_dic = cPickle.load(f)
    f.close()
    wiki_urls_dic = cPickle.load(open('wiki-urls-dic.pkl','rb'))
    bing_urls_list = json.load(open('bing-urls.json'))
    match_urls = {}
    C = 0
    for day in wiki_urls_dic:
        print day
        day_rep = day.replace('-','')
        if day_rep not in gdelt_dic:
            continue
        gdelt_urls = gdelt_dic[day_rep]
        wiki_urls = wiki_urls_dic[day]
        g_url_to_id = {}
        for it in gdelt_urls:
            g_url_to_id[it[1]] = it[0]
        wb_urls = set()
        for id in wiki_urls:
            wb_urls = set(wiki_urls[id]) | set(bing_urls_list[id-1]['urls'])
            for url in wb_urls:
                if url in g_url_to_id:
                    if day not in match_urls[day]:
                        match_urls[day] = [(id,g_url_to_id[url],url)]
                    else:
                        match_urls[day].append((id,g_url_to_id[url],url))
                    C += 1
                    print C
    out = open('match_url_dic.pkl','wb')
    cPickle.dump(match_urls,out)
    out.close()


if __name__ == '__main__':
    start_date = date(2013,12,4)
    end_date = date(2014,2,23)
    download_dailyupdates(start_date,end_date)
    #crawl_source(start_date, end_date)
    #get_gdelt_urls()
    #url_match_gdelt_and_wiki_bing()
