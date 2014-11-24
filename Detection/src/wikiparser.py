#! /usr/bin/python
# -*- coding: utf-8 -*-

from datetime import date
from bs4 import BeautifulSoup
import MySQLdb,os,cPickle
from gensim import corpora,models,similarities
import logging,re
from nltk.stem import *
import codecs,string,math

def download_wiki_monthly_events(start,end):
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    for year in range(2014,2015):
        for month in months[start:end]:
            os.system('wget http://en.wikipedia.org/wiki/'+month+'_'+str(year)+' --directory-prefix=../data/wiki/')

def wiki_event_extract_2003(month,year,dir):
#extractor for 2003.1~2006.4 
    events = []
    print month,year
    sp = BeautifulSoup(open(dir+month+'_'+year))
    spans = sp.find_all('span','mw-headline')
    span_dates = [s for s in spans if s.text.find(year)>=0]
    for span_date in span_dates:
        date = span_date.text
        day = ''
        for d in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:
            if date.find(d)>=0:
                day = d
                break
        type = ''
        lis = span_date.find_next('ul')('li')
        parent = None
        for li in lis:
            title,txt,anchs,urls='','',[],[]
            lis2 = li('li')
            if len(lis2)>0:
                parent = li
                try:
                    if li.contents[1].startswith(':'):
                        title = li.a.text
                except:
                    print 'Type err'
                for li2 in lis2:
                    txt = li2.text
                    txt = txt[:txt.rfind('.')]
                    anchs = '||'.join(link.text+'=>'+link['title'] for link in li2("a") if link['href'].startswith('/wiki/'))
                    urls = '||'.join(lk['href'] for lk in li2("a","external text"))
                    if len(urls)==0:
                        sups = li('sup','reference')
                        refs = [sp.find(id=lk.a['href'][1:]) for lk in sups]
                        if len(refs)>0:
                            hrefs = [ref('a','external free')[0]['href'] for ref in refs if len(ref('a','external free'))>0]
                            if len(hrefs)==0:
                                hrefs = [ref('a','external text')[0]['href'] for ref in refs if len(ref('a','external text'))>0]
                            urls = '||'.join(hrefs)
                    if len(urls)==0:
                        urls = '||'.join(lk['href'] for lk in li2('a','external autonumber'))
                    events.append((date,day,type,title,txt,anchs,urls))
            else:
                if li.find_parent().find_parent()==parent:
                    continue
                txt = li.text
                txt = txt[:txt.rfind('.')]
                anchs = '||'.join(link.text+'=>'+link['title'] for link in li("a") if link['href'].startswith('/wiki/'))
                urls = '||'.join(lk['href'] for lk in li("a","external text"))
                if len(urls)==0:
                    sups = li('sup','reference')
                    refs = [sp.find(id=lk.a['href'][1:]) for lk in sups]
                    if len(refs)>0:
                        hrefs = [ref('a','external free')[0]['href'] for ref in refs if len(ref('a','external free'))>0]
                        if len(hrefs)==0:
                            hrefs = [ref('a','external text')[0]['href'] for ref in refs if len(ref('a','external text'))>0]
                        urls = '||'.join(hrefs)
                if len(urls)==0:
                    urls = '||'.join(lk['href'] for lk in li('a','external autonumber'))
                events.append((date,day,type,title,txt,anchs,urls))
    return events
    
def wiki_event_extract_2013(month,year,dir):
#extractor for 2006.5~2013.11
    print month,year
    events = []
    page = dir+month+'_'+year;
    #if year == '2013':
    #    page += '.html'
    sp = BeautifulSoup(open(page))
    tbs=sp.find_all("table", "vevent")
    for tb in tbs:
        date = tb.table("span","summary")[0]("span","bday dtstart published updated")[0].string
        day = tb.table("span","summary")[0].contents[-1].strip(' ()')
        dts = tb("dt")
        for dt in dts:
            type = dt.text
            lis = dt.find_next()("li")
            parent = None
            for li in lis:
                lis2 = li("li")
                title,txt,anchs,urls="","",[],[]
                if len(lis2)>0:
                    parent = li
                    title = li.a.text
                    str_li = str(li).split('<ul>')[0]
                    if str_li.find('href=') == -1:
                        title = str_li.strip('<li>\n')
                    print title
                    for li2 in lis2:
                        txt = li2.text
                        txt = txt[:txt.rfind('.')]
                        anchs = '||'.join(link.text+'=>'+link['title'] for link in li2("a") if link['href'].startswith('/wiki/'))
                        urls = '||'.join(lk['href'] for lk in li2("a","external text"))
                        events.append((date,day,type,title,txt,anchs,urls))
                else:
                    if li.find_parent().find_parent()==parent:
                        continue
                    txt = li.text
                    txt = txt[:txt.rfind('.')]
                    anchs = '||'.join(link.text+'=>'+link['title'] for link in li("a") if link['href'].startswith('href'))
                    urls = '||'.join(lk['href'] for lk in li("a","external text"))
                    events.append((date,day,type,title,txt,anchs,urls))
    return events

def create_table():
    #db = MySQLdb.connect("sundance","zzw109","cse598s12","wiki_event")
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cursor = db.cursor()
    sql = """create table wikievents03to12 (
          date char(10),
          day char(10),
          type char(30),
          title char(100),
          content varchar(10000),
          anchs varchar(1000),
          urls varchar(5000),
          id int(10) unsigned not null auto_increment,
          primary key (id))"""
    cursor.execute(sql)
    db.commit()
    db.close()

 
def create_table_eventulrs():
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cursor = db.cursor()
    sql = """create table wikieventurls (
          date char(10),
          newstitle varchar(2000),
          description varchar(10000),
          url varchar(5000),
          eventid int(10) unsigned )"""
    cursor.execute(sql)
    db.commit()
    db.close()

def insert_table_eventurls_gdelt():
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cursor = db.cursor()
    sql0 = 'insert into wikieventurls (date,newstitle,description,url,eventid) values ('
    

def insert_table_eventurls(start_id):
    table = 'wikievents'
    wikitext_dir = '/home/zzw109/project/social/data/wikitext_new/'
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cursor = db.cursor()
    cursor.execute('select id,date,urls from wikievents where title!=\'\' and id > '+str(start_id))
    items = cursor.fetchall()
    sql0 = 'insert into wikieventurls (date,newstitle,description,url,eventid) values ('
    for it in items:
        id,date,urls = it[0],it[1],it[2].split('||')
        if re.search(r'\d{4}\-\d{2}\-\d{2}',date) is None:
            continue
        id_insert = id
        if table == 'wikievents03to12':
            id_insert += 100000000
        for url in urls:
            if len(url)==0:
                continue
            print 'url: '+url
            fname = date+'-'+str(id)+'-'+url.split('/')[2]
            if os.path.exists(wikitext_dir+fname) is not True:
                print fname,'url not exist'
                continue
            title,text = open(wikitext_dir+fname).read().strip().split('%%%%%%%%%%')
            title = title.replace('–','-')
            title = filter(lambda x: x in string.printable, title)
            lines = text.strip().split('\n')
            cands = []
            for line in lines:
                if title.lower().find(line.lower())!=-1:
                    continue
                words = line.split()
                if len(words) < 9:
                    continue
                if len(words) < 20 and re.search('[\.\?\!]',words[-1]) is None:
                    continue
                cands.append(line)
                if len(cands)>=3:
                    break
            description = filter(lambda x: x in string.printable, ' '.join(cands))
            #print 'tit: '+title
            #print 'des: '+description+'\n'
            sql1 = sql0+'\''+date+'\',\''+title.replace('\'','\\\'')+'\',\''+description.replace('\'','\\\'')+'\',\''+url+'\','+str(id_insert)+')'
            try:
                cursor.execute(sql1.encode('utf-8'))
            except:
                continue
    db.commit()
    db.close()

def create_table_story():
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cursor = db.cursor()
    sql = """create table wikistoriesfrom2003 (
          date char(10),
          cate char(2),
          title char(100),
          content varchar(10000),
          anchs varchar(1000),
          urls varchar(5000),
          id int(10) unsigned,
          before13 char(1))"""
    cursor.execute(sql)
    db.commit()
    db.close()

def insert_table_story(start_id_in_wikievents):
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cursor = db.cursor()
    cate_dic = {'Business and economy':6, 'Arts and culture':9, 'Economy and finance':6, 'Entertainment':9, 'Media':9, 'Armed Conflicts and attacks':1, 'Politics and elections':4, 'Sports':8, 'Environment':10, 'Religion':9, 'Business and economies':6, 'Attacks and conflicts':1, 'Law and justice':5, 'Law and crime':5, 'Health and science':7, 'Armed conflict and attack':1, 'Politics and government':4, 'Technology and science':7, 'Business':6, 'Attacks and armed conflicts':1, 'Disasters and accidents':2, 'Law, crime and accidents':5, 'Conflicts and attacks':1, 'Law and Crime':5, 'Business and economics':6, 'Politics and Elections':4, 'Law & crime':5, 'International Relations':3, 'Aerospace':7, 'Disasters':2, 'Science':7, 'Business and finance':6, 'Politics & Elections':4, 'Health and enviroment':10, 'Disasters and Accidents':2, 'Armed conflict and attacks':1, 'Science and technology':7, 'Technology':7, 'Science and environment':7, 'Laws and crime':5, 'Business and Economy':6, 'Armed conflicts and attack':1, 'Archaeology':7, 'Politics':4, 'Disasters and accidents,':2, 'Disaster and accidents':2, 'Education':11, 'International relations':3, 'Health and medicine':10, 'Deaths':12, 'Health and environment':10, 'Armed conflicts and attacks':1, 'Art and culture':9, 'Assassinations':5, 'Armed conflicts':1, 'Natural disasters':2, 'Science and Technology':7, 'Arts and Culture':9, 'Politics and election':4, 'Health':10, 'Law and order':5, 'Armed attacks and conflicts':1, 'Sport':8, 'Attacks and conficts':1, 'Disasters and impacts':2}
    cursor.execute('select distinct title from wikistoriesfrom2003')
    titles = cursor.fetchall()
    title_dic = {}
    for t in titles:
        if t[0] not in title_dic:
            title_dic[t[0]] = 1
    cursor.execute('select type,date,title,content,anchs,urls,id from wikievents where id >'+str(start_id_in_wikievents)+' order by title')
    items = cursor.fetchall()
    sql0 = 'insert into wikistoriesfrom2003 (cate, date, title, content, anchs, urls, id, before13) values ('
    for it in items:
        if len(it[2])==0:
            continue
        title = it[2].replace('–','-')
        title = filter(lambda x: x in string.printable, title)
        title_new = title
        if title not in title_dic:
            for key in title_dic:
                if levenshtein(title.lower(),key.lower())<3:
                    title_new = key
                    break
            if title_new == title:
                title_dic[title] = 1
        cate = ''
        if it[0] in cate_dic:
            cate = str(cate_dic[it[0]])
        e = [it[1],title_new]
        e.extend(it[3:6])
        sql = sql0+'\''+str(cate)+'\',\''+'\',\''.join(ei.replace('\'','\\\'') for ei in e)+'\','+str(it[6])+',\'n\''+')'
        cursor.execute(sql)
    db.commit()
    db.close()

def levenshtein(a,b):
    #"Calculates the Levenshtein distance between a and b."
    a,b = a.decode('utf-8'),b.decode('utf-8')
    n, m = len(a), len(b)
    if n > m:
    # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return current[n]


def dump_urls(table,out,startID):
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select id, date, urls from '+table+' where id >='+str(startID))
    data = cur.fetchall()
    db.close()
    dic = {}
    for it in data:
        if re.search(r'\d{4}\-\d{2}\-\d{2}',it[1]) is None:
            continue
        if it[1] not in dic:
            dic[it[1]] = {int(it[0]):it[2].split('||')}
        else:
            dic[it[1]][int(it[0])] = it[2].split('||')
    out = open(out,'wb')
    cPickle.dump(dic,out)
    out.close()

def export_to_file(f):
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select id, date, content from wikievents')
    data = cur.fetchall()
    txt = '\n'.join(str(data[i][0])+'\t'+data[i][1]+'\t'+data[i][2].replace('\n',' ') for i in range(len(data)))
    fh = open(f,'w')
    fh.write(txt)
    fh.close()
    db.close()

def import_to_table(events):
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('delete from wikievents03to12')
    cur.execute('alter table wikievents03to12 auto_increment = 1')
    sql0 = 'insert into wikievents03to12 (date, day, type, title, content, anchs, urls) values ('
    for e in events:
        #sql = sql+'\''+str(e[0])+'\',\''+str(e[1])+'\',\''+str(e[2])+'\',\''+str(e[3])+'\',\''+str(e[4])+'\',\''+str(e[5]
        sql = sql0+'\''+'\',\''.join(e[i].replace('\'','\\\'') for i in range(7))+'\')'
        try:
            cur.execute(sql.encode('utf-8'))
        except:
            print sql
    db.commit()
    db.close()

def insert_to_table(events):
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select id,date from wikievents order by id desc limit 1')
    item = cur.fetchall()[0]
    day = item[1].split('-')
    last_date = date(int(day[0]),int(day[1]),int(day[2]))
    last_id = int(item[0]) + 1
    cur.execute('alter table wikievents auto_increment='+str(last_id))
    sql0 = 'insert into wikievents (date, day, type, title, content, anchs, urls) values ('
    for e in events:
        #sql = sql+'\''+str(e[0])+'\',\''+str(e[1])+'\',\''+str(e[2])+'\',\''+str(e[3])+'\',\''+str(e[4])+'\',\''+str(e[5]
        day_e = str(e[0]).split('-')
        if date(int(day_e[0]),int(day_e[1]),int(day_e[2]))<=last_date:
            print 'oK'
            continue
        sql = sql0+'\''+'\',\''.join(e[i].replace('\'','\\\'') for i in range(7))+'\')'
        #print day_e,sql
        try:
            cur.execute(sql.encode('utf-8'))
            #print 'executing...'
        except:
            print sql
    db.commit()
    db.close()

def download_wiki_source(pkl):
    d = cPickle.load(open(pkl,'rb'))
    for k in d:
        for id in d[k]:
            urls = d[k][id]
            for url in urls:
                if len(url)==0:
                    continue
                fname = k+'-'+str(id)+'-'+url.split('/')[2]
                if os.path.exists(r'../data/wikisource_new/'+fname):
                    continue
                #print 'fname: '+fname
                #print 'url: '+url
                try:
                    os.system('wget -T 5 -t 2 -O ../data/wikisource_new/'+fname+' '+url)
                except:
                    print 'unknow error in url'
                    continue

def generate_event_chain_GT():
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select title,date,id from wikievents order by title')
    items = cur.fetchall()
    db.close()
    chains = {}
    for it in items:
        if len(it[0])==0:
            continue
        if it[0] not in chains:
            chains[it[0]] = [(it[1],int(it[2]))]
        else:
            chains[it[0]].append((it[1],int(it[2])))
    s_chains = sorted(chains.items(),key=lambda x:x[0])
    fw = open('event-chains.GT','w')
    for it in s_chains:
        fw.write(it[0]+': '+str(sorted(it[1],key=lambda x:x[1]))+'\n')
    fw.close()

def topic_modeling():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select title,id,content,anchs from wikievents order by title')
    items = cur.fetchall()
    db.close()
    documents = [it[2] for it in items]
    stopwords = open('stopwords').read().strip().split('\n')
    stemmer = PorterStemmer()
    texts = [[stemmer.stem(word) for word in doc.lower().split() if word not in stopwords] for doc in documents]
    dic = corpora.Dictionary(texts)
    dic.save('wikinews-topic-modeling.dict')
    corpus = [dic.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('wikinews-topic-modeling.mm',corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    #lsi = models.LsiModel(corpus_tfidf, id2word=dic,num_topics=30)
    lda = models.LdaModel(corpus_tfidf, id2word=dic, num_topics=20, update_every=1,chunksize=10000,passes=1)
    #corpus_lsi = lsi[corpus_tfidf]
    print 'examples:.........'
    #lsi.print_topics(20)
    lda.print_topics(20)

def check_id():
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select id from wikievents')
    items = cur.fetchall()
    db.close()
    ids = set(it[0] for it in items)
    print len(set(range(1,5344)).difference(ids))

def count_urls():
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select urls from wikievents')
    items = cur.fetchall()
    db.close()
    dic = {}
    for it in items:
        urls = it.split('||')
        for url in urls:
            start = url.find('://')+3
            end = url.find('/',start+1)
            host = url[start:end]
            if host not in dic:
                dic[host] = 1
            else:
                dic[host] += 1
    print len(dic),sum(dic[host] for host in dic)

def getWikiTitles():
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select type,anchs from wikievents')
    items = cur.fetchall()
    db.close()
    dic = {}
    dic_title = {}
    dic_type = {}
    for it in items:
        type = it[0]
        anchs = it[1].split('||')
        if type not in dic_type:
            dic_type[type] = {}
        for anch in anchs:
            if anch.find('=>') < 0:
                continue
            text,ref = anch.split('=>')
            if ref not in dic_type[type]:
                dic_type[type][ref] = 1
            else:
                dic_type[type][ref] +=1
            if 0:
                if text not in dic:
                    dic[text] = {ref:1}
                else:
                    if ref not in dic[text]:
                        dic[text][ref] = 1
                    else:
                        dic[text][ref] += 1
                if ref not in dic_title:
                    dic_title[ref] = 1
                else:
                    dic_title[ref] += 1
    #fp = open('wikiText2Concepts.pkl','wb')
    #cPickle.dump(dic,fp)
    #fp.close()
    fp1 = open('wikiTypeConcepts.pkl','wb')
    cPickle.dump(dic_type,fp1)
    fp1.close()

def conceptCategories():
    #1:conflict, attack
    #2:disaster, accident
    #3:international relations
    #4:politics and elections
    #5:law and crime
    #6:business and economy
    #7:science and technology
    #8:sports
    #9:arts and culture
    #10:health,medicine,environment
    #11:education
    #12:deaths
    cate_dic = {'Business and economy':6, 'Arts and culture':9, 'Economy and finance':6, 'Entertainment':9, 'Media':9, 'Armed Conflicts and attacks':1, 'Politics and elections':4, 'Sports':8, 'Environment':10, 'Religion':9, 'Business and economies':6, 'Attacks and conflicts':1, 'Law and justice':5, 'Law and crime':5, 'Health and science':7, 'Armed conflict and attack':1, 'Politics and government':4, 'Technology and science':7, 'Business':6, 'Attacks and armed conflicts':1, 'Disasters and accidents':2, 'Law, crime and accidents':5, 'Conflicts and attacks':1, 'Law and Crime':5, 'Business and economics':6, 'Politics and Elections':4, 'Law & crime':5, 'International Relations':3, 'Aerospace':7, 'Disasters':2, 'Science':7, 'Business and finance':6, 'Politics & Elections':4, 'Health and enviroment':10, 'Disasters and Accidents':2, 'Armed conflict and attacks':1, 'Science and technology':7, 'Technology':7, 'Science and environment':7, 'Laws and crime':5, 'Business and Economy':6, 'Armed conflicts and attack':1, 'Archaeology':7, 'Politics':4, 'Disasters and accidents,':2, 'Disaster and accidents':2, 'Education':11, 'International relations':3, 'Health and medicine':10, 'Deaths':12, 'Health and environment':10, 'Armed conflicts and attacks':1, 'Art and culture':9, 'Assassinations':5, 'Armed conflicts':1, 'Natural disasters':2, 'Science and Technology':7, 'Arts and Culture':9, 'Politics and election':4, 'Health':10, 'Law and order':5, 'Armed attacks and conflicts':1, 'Sport':8, 'Attacks and conficts':1, 'Disasters and impacts':2}
    concept_dic = {}
    dic_type = cPickle.load(open('wikiTypeConcepts.pkl','rb'))
    for type in dic_type:
        cate = cate_dic[type]
        for c in dic_type[type]:
            if c not in concept_dic:
                concept_dic[c] = [0]*12
                concept_dic[c][cate-1] = dic_type[type][c]
            else:
                concept_dic[c][cate-1] += dic_type[type][c]
    fp = open('wikiConceptsCates.pkl','wb')
    cPickle.dump(concept_dic,fp)
    fp.close()

def conceptCatesEvents(table,outDic):
#for table wikievents
    cate_dic = {'Business and economy':6, 'Arts and culture':9, 'Economy and finance':6, 'Entertainment':9, 'Media':9, 'Armed Conflicts and attacks':1, 'Politics and elections':4, 'Sports':8, 'Environment':10, 'Religion':9, 'Business and economies':6, 'Attacks and conflicts':1, 'Law and justice':5, 'Law and crime':5, 'Health and science':7, 'Armed conflict and attack':1, 'Politics and government':4, 'Technology and science':7, 'Business':6, 'Attacks and armed conflicts':1, 'Disasters and accidents':2, 'Law, crime and accidents':5, 'Conflicts and attacks':1, 'Law and Crime':5, 'Business and economics':6, 'Politics and Elections':4, 'Law & crime':5, 'International Relations':3, 'Aerospace':7, 'Disasters':2, 'Science':7, 'Business and finance':6, 'Politics & Elections':4, 'Health and enviroment':10, 'Disasters and Accidents':2, 'Armed conflict and attacks':1, 'Science and technology':7, 'Technology':7, 'Science and environment':7, 'Laws and crime':5, 'Business and Economy':6, 'Armed conflicts and attack':1, 'Archaeology':7, 'Politics':4, 'Disasters and accidents,':2, 'Disaster and accidents':2, 'Education':11, 'International relations':3, 'Health and medicine':10, 'Deaths':12, 'Health and environment':10, 'Armed conflicts and attacks':1, 'Art and culture':9, 'Assassinations':5, 'Armed conflicts':1, 'Natural disasters':2, 'Science and Technology':7, 'Arts and Culture':9, 'Politics and election':4, 'Health':10, 'Law and order':5, 'Armed attacks and conflicts':1, 'Sport':8, 'Attacks and conficts':1, 'Disasters and impacts':2}
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select type,title,anchs from '+table)
    items = cur.fetchall()
    db.close()
    dic = {}
    for it in items:
        cate = cate_dic[it[0]]
        title = it[1]
        if len(title)==0:
            continue
        anchs = it[2].split('||')
        if cate not in dic:
            dic[cate] = {}
        if title not in dic[cate]:
            dic[cate][title] = {}
        for anch in anchs:
            if anch.find('=>') < 0:
                continue
            text,ref = anch.split('=>')
            if ref not in dic[cate][title]:
                dic[cate][title][ref] = 1
            else:
                dic[cate][title][ref] +=1
    fp1 = open(outDic,'wb')
    cPickle.dump(dic,fp1)
    fp1.close()

def conceptCatesEvents2(table,outDic):
#for table wikistories*
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select cate,title,anchs from '+table)
    items = cur.fetchall()
    db.close()
    dic = {}
    for it in items:
        cate = it[0]
        title = it[1]
        if len(title)==0:
            continue
        anchs = it[2].split('||')
        if cate not in dic:
            dic[cate] = {}
        if title not in dic[cate]:
            dic[cate][title] = {}
        for anch in anchs:
            if anch.find('=>') < 0:
                continue
            text,ref = anch.split('=>')
            if ref not in dic[cate][title]:
                dic[cate][title][ref] = 1
            else:
                dic[cate][title][ref] +=1
    fp1 = open(outDic,'wb')
    cPickle.dump(dic,fp1)
    fp1.close()


def conceptCateStory(inDic,outDic):
    dic = cPickle.load(open(inDic,'rb'))
    dic_story = {}
    for type in dic:
        for s in dic[type]:
            for c in dic[type][s]:
                if c not in dic_story:
                    dic_story[c] = {type:{s:dic[type][s][c]}}
                else:
                    if type not in dic_story[c]:
                        dic_story[c][type] = {s:dic[type][s][c]}
                    else:
                        if s not in dic_story[c][type]:
                            dic_story[c][type][s] = dic[type][s][c]
                        else:
                            dic_story[c][type][s] += dic[type][s][c]
    fp = open(outDic,'wb')
    cPickle.dump(dic_story,fp)
    fp.close()

def conceptStoryFreq(inDic,outDic):
    dic = cPickle.load(open(inDic,'rb'))
    dic_c = {}
    for c in dic:
        stories = []
        for v in dic[c].values():
            stories.extend(v.keys())
        dic_c[c] = len(set(stories))
    fp = open(outDic,'wb')
    cPickle.dump(dic_c,fp)
    fp.close()

def conceptStoryTFIDF(concept2cate2story,conceptDF,outDic):
    dic = cPickle.load(open(concept2cate2story,'rb'))
    dic_df = cPickle.load(open(conceptDF,'rb'))
    dic_tfidf = {}
    dic_s = {}
    for con in dic:
        if con not in dic_tfidf:
            dic_tfidf[con] = {}
        for cate in dic[con]:
            for s in dic[con][cate]:
                if s not in dic_s:
                    dic_s[s] = 1
                if s not in dic_tfidf[con]:
                    dic_tfidf[con][s] = dic[con][cate][s]
                else:
                    dic_tfidf[con][s] += dic[con][cate][s]
    N = len(dic_s)+0.0
    print N
    for c in dic_tfidf:
        for s in dic_tfidf[c]:
            dic_tfidf[c][s] = dic_tfidf[c][s]*math.log(N/dic_df[c],2)
    fp = open(outDic,'wb')
    cPickle.dump(dic_tfidf,fp)
    fp.close()

def storyConceptTFIDF(cate2story2concept,conceptDF,outDic):
    dic = cPickle.load(open(cate2story2concept,'rb'))
    dic_df = cPickle.load(open(conceptDF,'rb'))
    dic_s = {}
    for cate in dic:
        for s in dic[cate]:
            if s not in dic_s:
                dic_s[s] = {}
            for con in dic[cate][s]:
                if con not in dic_s[s]:
                    dic_s[s][con] = dic[cate][s][con]
                else:
                    dic_s[s][con] += dic[cate][s][con]
    N = len(dic_s) + 0.0
    print N
    for s in dic_s:
        sum_tf = sum(dic_s[s].values())
        for con in dic_s[s]:
            dic_s[s][con] = (dic_s[s][con]+0.0)/sum_tf*math.log(N/dic_df[con],2)
    fp = open(outDic,'wb')
    cPickle.dump(dic_s,fp)
    fp.close()

def story2date(table,outDic):
#for table wikistories*
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select date,title from '+table)
    items = cur.fetchall()
    db.close()
    dic = {}
    for it in items:
        dat,title = it
        if re.search(r'\d{4}\-\d{2}\-\d{2}',dat) is None:
            continue
        d = date(int(dat[:4]),int(dat[5:7]),int(dat[8:10]))
        if title not in dic:
            dic[title] = [d]
        else:
            dic[title].append(d)
    for title in dic:
        dic[title] = [min(dic[title]),max(dic[title])]
    fp = open(outDic,'wb')
    cPickle.dump(dic,fp)
    fp.close()

def story2events(table,outDic):
#for table wikistories*
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select date,title,id from '+table)
    items = cur.fetchall()
    dic = {}
    for it in items:
        dat,title,id = it
        if re.search(r'\d{4}\-\d{2}\-\d{2}',dat) is None:
            continue
        d = date(int(dat[:4]),int(dat[5:7]),int(dat[8:10]))
        if title not in dic:
            dic[title] = [(d,id)]
        else:
            dic[title].append((d,id))
    fp = open(outDic,'wb')
    cPickle.dump(dic,fp)
    fp.close()
    db.close()

def eventid2titledes(table,outDic):
#for table wikieventurls
    db = MySQLdb.connect("sundance","root","311aistpsu","wiki_event")
    cur = db.cursor()
    cur.execute('select eventid,newstitle,description,url from '+table)
    items = cur.fetchall()
    dic = {}
    for it in items:
        id,title,des,url = it
        if id not in dic:
            dic[id] = [(title,des,url)]
        else:
            dic[id].append((title,des,url))
    fp = open(outDic,'wb')
    cPickle.dump(dic,fp)
    fp.close()
    db.close()


if __name__ == '__main__':
    #insert_table_eventurls(6137)
    #create_table_eventulrs()
    #insert_table_story(6137)
    #create_table_story()
    #conceptCatesEvents2('wikistoriesfrom2003','cate2story2conceptfrom2003.pkl')
    #conceptCateStory('cate2story2conceptfrom2003.pkl','concept2cate2storyfrom2003.pkl')
    #conceptStoryFreq('concept2cate2storyfrom2003.pkl','conceptDF.pkl')
    #conceptStoryTFIDF('concept2cate2storyfrom2003.pkl','conceptDF.pkl','concept2storyTFIDF.pkl')
    #storyConceptTFIDF('cate2story2conceptfrom2003.pkl','conceptDF.pkl','story2conceptTFIDF.pkl')
    #story2date('wikistoriesfrom2003','story2date.pkl')
    #story2events('wikistoriesfrom2003','story2events.pkl')
    #eventid2titledes('wikieventurls','eventid2titledes.pkl')
    #download_wiki_monthly_events(3,5)
    #insert_to_table([])
    #export_to_file('../data/wiki-events-2013-12-4.txt')
    dump_urls('wikievents','urls-05-22.pkl',6221)
    download_wiki_source('urls-05-22.pkl')
    #generate_event_chain_GT()
    #topic_modeling()
    #check_id()
    #getWikiTitles()
    #conceptCategories()
    if 0:
        months = ['January','February','March','April','May','June','July','August','September','October','November','December']
        dir = r'/home/zzw109/project/social/data/wiki/'
        C = 0
        C_url = 0
        events = []
        if 0:
            for y in range(2003,2006):
                for m in months:
                    events.extend(wiki_event_extract_2003(m,str(y),dir))
            for m in months[:4]:
                events.extend(wiki_event_extract_2003(m,'2006',dir))
            for m in months[4:]:
                events.extend(wiki_event_extract_2013(m,'2006',dir))
        for y in range(2014,2015):
            for m in months[3:5]:
                events.extend(wiki_event_extract_2013(m,str(y),dir))
            #print events
        print len(events),sum(len(event[-1].split('||')) for event in events)
        #fp = open('event07-12.pkl','wb')
        #cPickle.dump(events,fp)
        #fp.close()
        insert_to_table(events)
