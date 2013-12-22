import urllib
import re

domain = 'http://www.subscenter.org'
search = '/he/subtitle/search/?q=%s'
sub_down = '/he/subtitle/download/he/%s/?v=%s&key=%s'  #id,subtitle_version,key
filters = ['DVDrip','R5','BDRip','BRRip','BluRay','WEB-DL','720P','1080P','1080i','PPVRIP']
filters_low = map(str.lower, filters)

def performrequest(url):
    return urllib.urlopen(domain+url).read()

whole_matches =  re.findall('\<a href\=\"(\/he\/subtitle\/movie\/[A-Za-z0-9\-]*?\/)\">(.*?)</a>',
                            performrequest(search % 'the+matrix'))
for match in whole_matches:
    movie_url   = match[0]
    movie_name  = match[1].split(' / ')[1]

    #Extract versions from the site
    in_content = performrequest(movie_url)
    
    #English: pattern = '"en": .*? "id": ([0-9]*), .*? \"key\": \"([0-9a-f]*?)\", "notes": .*?\", \"subtitle_version\": \"(.*?)\",'
    en_content = '{"en": {(.*?)}}}}, '
    he_content = '"he": {(.*?)}}}}}'
    content = re.findall(he_content, in_content)[0]
    
    pattern = '"id": ([0-9]*), .*? \"key\": \"([0-9a-f]*?)\", "notes": .*?\", \"subtitle_version\": \"(.*?)\",'
    #Filter matches using filters_low
    #versions_match = filter(lambda v: len(filter(lambda f: f in v[2].lower(),filters_low)), re.findall(pattern, in_content))
    versions_match = re.findall(pattern, content)

    for version in versions_match:
        print '%s,%s=>%s' % version

    print 'page length: %d' % len(in_content)
    print 'url: %s' % movie_url
    print 'name: %s' % movie_name
    req = sub_down % (versions_match[3][0], versions_match[3][2], versions_match[3][1])
    print req
    
    con = performrequest(req)
    if len(con) > 10:
        print '------===========SUCCESS===========-------'
    else:
        print '==========-------FAILURE-------==========='
