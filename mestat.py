from time import time
from os import environ
from cgi import parse_qs, FieldStorage as FormPost
import google.appengine.api.labs.taskqueue as tq
from google.appengine.api.memcache import get as mget, set as mset, get_multi as mmget, delete as mdel, flush_all
import google.appengine.api.memcache as m

NS = 'MESTAT-DATA'

def stat():
    """Save current stats"""
    s = m.get_stats()
    t = int(time())
    m.set(str(t), s, namespace=NS)

    # XXX Possible race if task scheduler messes up, but we don't care.
    sts = m.get('sample-times', namespace=NS)
    if sts == None:
        sts = []
    sts.insert(0, t)
    sts = sts[:60*24*5] # Keep ~5 days of data
    m.set('sample-times', sts, namespace=NS)


# PyLie
def _mmax(l):
    m = max(vals)
    if m == 0:
        return 1
    return m

def mnvals(vals, range):
    m = _mmax(l)
    mn = min(l)
    return ([range*v/m for v in vals], m, mn)
   
def mvals(vals, range):
    m = _mmax(vals)
    return ([range*v/m for v in vals], m)

def churl(vals, opts):
    """Generates a chart url using vals, and opts, opts can be a dictionary or a string"""



def main():

    args = parse_qs(environ['QUERY_STRING'])
    form = FormPost()
    if form.has_key('FLUSH'):
        flush_all()

    if 'update' in args:
        stat()
        return
    
    ats = ['items', 'bytes', 'oldest_item_age', 'hits', 'byte_hits', 'misses']
    s = mmget([str(i) for i in mget('sample-times', namespace=NS)], namespace=NS)
    #  
    a = dict([(k, [int(s[d][k]) for d in s]) for k in ats]) # attr -> vals
    a = dict([(k, (max(a[k]), min(a[k]), a[k])) for k in a]) # attrs -> (max, min, vals)
    #a = dict([(k, [62*(v+1-a[k][1])/(a[k][0]+1-a[k][1]) for v in a[k][2]]) for k in a]) # attrs -> norml-vals
    a = dict([(k, [62*v/(a[k][0]+1) for v in a[k][2]]) for k in a]) # attrs -> norml-vals
    print "Content-type: text/html"
    print ""
    #l = ["rend('"+k+"', %s);"%str([int(s[d][k]) for d in s]) for k in ats]
    #l = ["rend('"+k+"', %s);"%str([int(d) for d in a[k]]) for k in a]
    f = "rend('Memcached stats', %s);"%str([[int(d) for d in a[k]] for k in a])
    #f='\n'.join(l)
    print """<html><head><script type="text/javascript" src="http://www.solutoire.com/download/gchart/gchart-0.2alpha_uncompressed.js"></script>
<script>
// Using: http://solutoire.com/gchart/
// d = """+repr(s)+"""
// x = """+repr(a)+"""
function rend(t, d) {
GChart.render({'renderTo': document.body, 'size': '800x200', colors: 'FF0000,00FF00,0000FF,FFFF00,00FFFF,FF00FF', legend:'"""+'|'.join([k for k in a])+"""',  title: t, 'data': d});
}
function main() {
"""+f+"""
}
</script>
</head><body onload="main();">
<h1>Memcache Stats</a>
<form action="" method="POST"><form input="submit" name="flush" value="Flush Memcache!" />
<div id="items"></div>

</body></html>
"""


if __name__ == '__main__':
    main()




