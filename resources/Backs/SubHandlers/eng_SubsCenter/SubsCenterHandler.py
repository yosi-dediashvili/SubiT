import json

import SubiT
import SubResult
import Utils

from Utils import HttpRequestTypes

from SubHandlers.ISubHandler import ISubHandler

class SUBSCENTER_PAGES:
    DOMAIN      = r'www.subscenter.org'
    SEARCH      = r'/he/subtitle/search/?q=%s'
    MOVIE       = r'/he/subtitle/movie/%s/'
    DOWN_PAGE   = r'/he/subtitle/download/en/%s/?v=%s&key=%s'

class SUBSCENTER_REGEX:
    NAME_IN_SITE_PARSER     = r'<h3>(.*?)\s*?</h3>'
    #SEARCH_RESULTS_PARSER   = r'\<a href\=\"\/he\/subtitle\/movie\/([A-Za-z0-9\-]*?)\/\">([^>]*?)</a>'
    SEARCH_RESULTS_PARSER   = r'\<a href\=\"\/he\/subtitle\/movie\/([A-Za-z0-9\-]*?)\/\">[^>]*?</a>'
    #SUB_VERSIONS_PARSER     = r'"id": (?P<moviecode>[0-9]*), .*? \"key\": \"(?P<vercode>[0-9a-f]*?)\", "notes": .*?\", \"subtitle_version\": \"(?P<versum>.*?)\",'
    #ENG_CONTENT_EXT         = r'"en": ({.*?}}}})'
    #HEB_CONTENT_EXT         = r'"he": ({.*?}}})}'
    VERSIONS_VAR            = r'var subtitles_groups = (.*?}}}}})'
    LANG                    = r'en'

class SubsCenterHandler(ISubHandler):
    HANDLER_NAME = 'English - www.subscenter.org'

    @staticmethod
    def findmovieslist( subSearch ):
        moviename = subSearch.Query
        searchresult = Utils.performrequest(SUBSCENTER_PAGES.DOMAIN, 
                                            SUBSCENTER_PAGES.SEARCH % moviename.replace(' ', '+'), 
                                            '', 
                                            HttpRequestTypes.GET, 
                                            '' )

        movies_codes = Utils.getregexresults(SUBSCENTER_REGEX.SEARCH_RESULTS_PARSER, searchresult)
        subMovies = []

        for movie_code in movies_codes:
            movie_page = Utils.performrequest(  SUBSCENTER_PAGES.DOMAIN, 
                                                SUBSCENTER_PAGES.MOVIE % movie_code, 
                                                '', 
                                                HttpRequestTypes.GET, 
                                                '')
            #Dict of the versions
            versions_area_content = Utils.getregexresults(SUBSCENTER_REGEX.VERSIONS_VAR, movie_page)
            #If it's some series (won't be handled right now)
            if not len(versions_area_content):
                Utils.WriteDebug('No Match for Versions Var MovieCode: %s' % movie_code)
                continue
            else:
                jsoned_movie_page_dict = json.loads(versions_area_content[0])

                lang = SUBSCENTER_REGEX.LANG
                #If it's some series (won't be handled right now)
                if not lang in jsoned_movie_page_dict:
                    Utils.WriteDebug('No Lang MovieCode: %s' % movie_code)
                    continue
                else:
                    total_providers = jsoned_movie_page_dict[lang].keys()
                    total_ver_types = []
                    all_versions    = []
                    for provider in total_providers:
                        for ver_type in jsoned_movie_page_dict[lang][provider]:
                            if not ver_type in total_ver_types:
                                if ver_type != 'ALL':
                                    total_ver_types.append(ver_type)
                                for ver in jsoned_movie_page_dict[lang][provider][ver_type]:
                                    all_versions.append({'moviecode':jsoned_movie_page_dict[lang][provider][ver_type][ver]['id'],
                                                         'vercode'  :jsoned_movie_page_dict[lang][provider][ver_type][ver]['key'],
                                                         'versum'   :jsoned_movie_page_dict[lang][provider][ver_type][ver]['subtitle_version']})
            
                    ver_sum = ' / '.join(total_ver_types)

                    movie_name = Utils.getregexresults(SUBSCENTER_REGEX.NAME_IN_SITE_PARSER, movie_page)[0]
            
                    #List of {MovieCode, VerCode, VerSum} of SubVersion
                    #all_versions = Utils.getregexresults(SUBSCENTER_REGEX.SUB_VERSIONS_PARSER, movie_page_rel_content, True)

                    subMovies.append(SubResult.SubMovie(movie_code, movie_name, ver_sum, all_versions))
                    Utils.WriteDebug('Added MovieCode: %s' % movie_code)
        
        return subMovies

    @staticmethod
    def findversionslist( subMovie ):
        return map(lambda e: SubResult.SubVersion(**e) ,subMovie.Extra)
    
    @staticmethod
    def getsuburl( subVersion ):
        return(SUBSCENTER_PAGES.DOMAIN,
               SUBSCENTER_PAGES.DOWN_PAGE % ( subVersion.MovieCode, subVersion.VerSum, subVersion.VerCode))
