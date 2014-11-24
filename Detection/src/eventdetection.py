#! /usr/bin/python

import os,cPickle,re,math,zipfile,string
from datetime import date,timedelta

class EventEncoding():
    def __init__(self):
        pass

    def buildActorDic(self):#build actor list from CAMEO and Wikipedia
        pass
    
    def buildActionDic(self):
        pass

class EventClustering():
    def __init__(self,dic_concept2story,dic_conceptDF,dic_story2concept,dic_story2date,dic_story2events,dic_eventid2titledes,input_dir):
        self.concept2story = dic_concept2story
        self.story2concept = dic_story2concept
        self.conceptDF = dic_conceptDF
        self.story2date = dic_story2date
        self.story2events = dic_story2events
        self.eventid2titledes = dic_eventid2titledes
        self.newsdir = input_dir
        self.newsset = os.listdir(input_dir)
        self.N = len(self.story2concept)+0.0
   
    def sim_hash(self,hashfile):
        gid2hash = {}


    def vectoring(self):
        pass
    
    def lsh(self,doc):
        """
        A simple modified lsh based on entities
        """
        fopen = open(doc)
        content = fopen.read().lower()
        fopen.close()
        dic_story = {}
        for k in self.concept2story:
            if content.find(k.lower()) >= 0:
                for s in self.concept2story[k]:
                    if s not in dic_story:
                        dic_story[s] = [k]
                    else:
                        dic_story[s].append(k)
        story_list = sorted(dic_story.items(), key=lambda x:len(x[1]), reverse=True)
        if len(story_list)<1:
            #print 'none'
            return None
        #print doc.split('/')[-1]
        #print story_list[:2]
        L = len(content.split())+0.0
        inPr,A = 0,0
        story,cons = story_list[0]
        for con in cons:
            tf = len(re.findall(con.lower()+'[\.,:\?\!\'\";\s]',content))/L
            tfidf =tf*math.log(self.N/self.conceptDF[con],2)
            inPr += tfidf*self.story2concept[story][con]
            A += tfidf**2
        B = sum(v**2 for v in self.story2concept[story].values())
        #print cons,inPr,A,B
        cos = inPr/(math.sqrt(A*B)+0.000001)
        #print inPr,A,B,cos
        if cos>0.2:
            #print cos,story
            return story,cos
        return None
    
    def lsh_tfidf(self,doc):
        fopen = open(doc)
        content = fopen.read().lower()
        fopen.close()
        dic_story = {}
        for k in self.concept2story:
            tf = len(re.findall(k.lower(),content))
            if tf > 0:
                for s in self.concept2story[k]:
                    if s not in dic_story:
                        dic_story[s] = tf*self.concept2story[k][s]
                    else:
                        dic_story[s] += tf*self.concept2story[k][s]
        story_list = sorted(dic_story.items(), key=lambda x:x[1], reverse=True)
        if len(story_list)<1:
            #print 'none'
            return None
        #print doc.split('/')[-1]
        #print story_list[:2]
        return story_list[0]


    def link2story_candiates(self,out):
        fo = open(out,'w')
        for news in self.newsset:
            rs = self.lsh(self.newsdir+news)
            if rs is not None:
                fo.write(news+'\t'+rs[0]+'\t'+str(rs[1])+'\n')
        fo.close()
            #self.lsh_tfidf(self.newsdir+news)

    def link2story(self,sd,out):
        """
        link daily updated news to the story base
        """
        dir = r'../data/dailyupdates/'
        textdir = r'../data/newstext/'+sd+os.sep
        gid2url = {}
        gid2url_pkl = r'./gid2url/'+sd+'.pkl'
        print sd
        news_date = date(int(sd[:4]),int(sd[4:6]),int(sd[6:8]))
        if os.path.exists(gid2url_pkl):
            gid2url = cPickle.load(open(gid2url_pkl,'rb'))
        else:
            zf = zipfile.ZipFile(dir + sd + '.export.CSV' + '.zip','r')
            lines = zf.read(sd+'.export.CSV').strip().split('\n')
            for ln in lines:
                id,url = ln.split()[0],ln.split()[-1]
                if id not in gid2url:
                    gid2url[id] = url
            fp = open(gid2url_pkl,'wb')
            cPickle.dump(gid2url,fp)
            fp.close()
        lines = open('./linkedrecords/'+sd+'.linkedrecords.txt').read().strip().split('\n')
        dic_score = {}
        C = 0
        records = []
        url_set = set([])
        for line in lines:
            fname,story,score = line.split('\t')
            if float(score) < 0.5 or (story,score) in dic_score or story not in self.story2date:#filtering by similarity threshold and duplication
                continue
            dic_score[(story,score)] = 1
            gid = fname[:-5]
            date1,date2 = self.story2date[story]
            if news_date-date1 < timedelta(0) or news_date-date2 > timedelta(0):
                #print 'not in time range:'+story+str(date1)+str(date2)+'continue\n'
                continue
            events = self.story2events[story]
            evt_ids = [evt[1] for evt in events if evt[0]==news_date]
            if len(evt_ids)==0:
                continue
            url = gid2url[gid]
            if url in url_set:
                continue
            url_set.add(url)
            title,text = open(textdir+fname).read().strip().split('%%%%%%%%%%')
            news_lns = text.strip().split('\n')
            cands = []
            for ln in news_lns:
                if title.lower().find(ln.lower())!=-1:
                    continue
                words = ln.split()
                if len(words) < 9:
                    continue
                if len(words) < 20 and re.search('[\.\?\!]',words[-1]) is None:
                    continue
                cands.append(ln)
                if len(cands)>=3:
                    break
            description = filter(lambda x: x in string.printable, ' '.join(cands))
            s1 = set(title.split()) | set(description.split())
            for id in evt_ids:
                if id not in self.eventid2titledes:
                    continue
                evt_title,evt_des,evt_url = self.eventid2titledes[id][0]
                if evt_url == url:
                    continue
                s2 = set(evt_title.split()) | set(evt_des.split())
                if len(s1&s2)/(len(s1|s2)+0.0) > 0.3:
                    records.append(sd[:4]+'-'+sd[4:6]+'-'+sd[6:8]+'\t'+title+'\t'+description+'\t'+url+'\t'+str(id))
                    C += 1
            #print story+score+title+'description: '+description
            #print 'url: '+url
        print C
        if C >0:
            fo = open(out,'w')
            fo.write('\n'.join(records))
            fo.close()

if __name__ == '__main__':
    stopwords = open(r'stopwords').read().strip().split('\n')
    inputdir = r'/home/zzw109/project/social/data/newstext/'
    d1 = cPickle.load(open('concept2storyTFIDF.pkl','rb'))
    d2 = cPickle.load(open('conceptDF.pkl','rb'))
    d3 = cPickle.load(open('story2conceptTFIDF.pkl','rb'))
    d4 = cPickle.load(open('story2date.pkl','rb'))
    d5 = cPickle.load(open('story2events.pkl','rb'))
    d6 = cPickle.load(open('eventid2titledes.pkl','rb'))
    for f in os.listdir(inputdir):
        ec = EventClustering(d1,d2,d3,d4,d5,d6,inputdir+f+os.sep)
        ec.link2story(f,'./linkedrecords/'+f+'.wikieventurls.txt')
