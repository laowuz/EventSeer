methods = ['bm25','cosine', 'ip']

prec = [[0 for j in xrange(10)] for i in xrange(len(methods))]
cnt = [[0 for j in xrange(10)] for i in xrange(len(methods))]


for i in xrange(len(methods)):
    m = methods[i]
    with open( 'query_label_1.' + m ) as f:
        while 1:
            q = f.readline()
            if not q:
                break
            n = int(f.readline())
            for j in xrange(n):
                label = int(f.readline().strip().split('\t')[1])
                cnt[i][j] += 1
                if label > 0:
                    prec[i][j] += 1

with open('result', 'w') as out:
    for i in xrange(len(methods)):
        out.write(methods[i] + '\n')
        totprec = totcnt = 0
        for j in xrange(10):
            totcnt += cnt[i][j]
            totprec += prec[i][j]
            out.write( str(float(totprec) / totcnt) + '\n')
            

