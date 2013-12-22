import json

import SubiT
import SubResult
import Utils

from Utils import HttpRequestTypes

from SubHandlers.ISubHandler import ISubHandler

class SUBSCENTER_LANGUAGES:
    ENGLISH = 'en'
    HEBREW  = 'he'

class SUBSCENTER_PAGES:
    DOMAIN      = r'www.subscenter.org'
    SEARCH      = r'/he/subtitle/search/?q=%s'
    MOVIE       = r'/he/subtitle/movie/%s/'
    SERIES      = r'/he/subtitle/series/%s/'
    DOWN_PAGE   = r'/he/subtitle/download/%s/%s/?v=%s&key=%s' #lang, code, version, key
    LANG = SUBSCENTER_LANGUAGES.HEBREW

class SUBSCENTER_REGEX:
    NAME_IN_SITE_PARSER     = r'<h3>(.*?)\s*?</h3>'
    SEARCH_RESULTS_PARSER   = r'\<a href\=\"\/he\/subtitle\/(?P<Type>movie|series)\/(?P<Code>[A-Za-z0-9\-]*?)\/\">[^>]*?</a>'
    URL_RESULT_PARSER       = r'/he\/subtitle\/(?P<Type>movie|series)\/(?P<Code>[A-Za-z0-9\-]*?)\/'
    VERSIONS_VAR            = r'subtitles_groups = (.*?}}}}})'
    SERIES_VAR              = r'var episodes_group = (.*?}}})'


class SubsCenterHandler(ISubHandler):
    HANDLER_NAME = 'Hebrew - www.subscenter.org'

    #This function will get the series page, and return all the episodes inside this page
    #Return value will be List<season_id, episode_id>
    @staticmethod
    def getEpisodesList(series_area_content):
        all_episodes = []
        try:
            jsoned_series_page_dict = json.loads(series_area_content[0])
            total_seasons = jsoned_series_page_dict.keys()
        
            for season in total_seasons:
                total_episodes = jsoned_series_page_dict[season].keys()
                for episode in total_episodes:
                    all_episodes.append({'season_id' : jsoned_series_page_dict[season][episode]['season_id'],
                                         'episode_id': jsoned_series_page_dict[season][episode]['episode_id']})
        except Exception as eX:
            Utils.WriteDebug('Failed: getEpisodesList->%s' % eX.message)

        return all_episodes

    #This function will get the versions page of the movie/series and return a formettd list of:
    #List<movie_code, ver_code, ver_sum>
    @staticmethod
    def getVersionsList(versions_area_content):
        all_versions    = []
        ver_sum         = ''

        try:
            jsoned_movie_page_dict = json.loads(versions_area_content[0])
            lang = SUBSCENTER_PAGES.LANG
        
            total_providers = jsoned_movie_page_dict[lang].keys()
            total_ver_types = []
            all_versions    = []
            for provider in total_providers:
                for ver_type in jsoned_movie_page_dict[lang][provider]:
                    if not ver_type in total_ver_types:
                        #If the version type is not ALL, we insert it to the list of the versions type, in order to show it in the subMovie.VerSum
                        if ver_type != 'ALL':
                            total_ver_types.append(ver_type)
                        for ver in jsoned_movie_page_dict[lang][provider][ver_type]:
                            all_versions.append({'moviecode':jsoned_movie_page_dict[lang][provider][ver_type][ver]['id'],
                                                 'vercode'  :jsoned_movie_page_dict[lang][provider][ver_type][ver]['key'],
                                                 'versum'   :jsoned_movie_page_dict[lang][provider][ver_type][ver]['subtitle_version']})
            
            ver_sum = ' / '.join(total_ver_types)
        except Exception as eX:
            Utils.WriteDebug('Failed: getVersionsList->%s' % eX.message)

        return (ver_sum, all_versions)


    @staticmethod
    def findmovieslist( subSearch ):
        moviename   = subSearch.Query.lower()
        movies_info = []
        subMovies   = []
        searchresult = Utils.performrequest(SUBSCENTER_PAGES.DOMAIN, 
                                            SUBSCENTER_PAGES.SEARCH % moviename.replace(' ', '+'))
        #Search results
        movies_info = Utils.getregexresults(SUBSCENTER_REGEX.SEARCH_RESULTS_PARSER, searchresult, True)


        for movie_info in movies_info:
            movie_code = movie_info['Code']
            movie_type = movie_info['Type']

            Utils.WriteDebug('Working on %s' % movie_type)
            #===================================================================
            #If the result is movie
            if movie_type == 'movie':
                movie_page = Utils.performrequest(  SUBSCENTER_PAGES.DOMAIN, 
                                                    SUBSCENTER_PAGES.MOVIE % movie_code)
                #Dict of the versions
                versions_area_content   = Utils.getregexresults(SUBSCENTER_REGEX.VERSIONS_VAR, movie_page)            
                (ver_sum, all_versions) = SubsCenterHandler.getVersionsList(versions_area_content)
                movie_name              = Utils.getregexresults(SUBSCENTER_REGEX.NAME_IN_SITE_PARSER, movie_page)[0]
            
                subMovies.append(SubResult.SubMovie(movie_code, movie_name, ver_sum, {'type' : 'movie', 'all_versions' : all_versions}))
                Utils.WriteDebug('Added MovieCode: %s' % movie_code)
            #===================================================================
            #If the result is series
            else:
                series_page         = Utils.performrequest(SUBSCENTER_PAGES.DOMAIN, SUBSCENTER_PAGES.SERIES % movie_code)
                series_area_content = Utils.getregexresults(SUBSCENTER_REGEX.SERIES_VAR, series_page)
                all_episodes        = SubsCenterHandler.getEpisodesList(series_area_content)
                series_name         = Utils.getregexresults(SUBSCENTER_REGEX.NAME_IN_SITE_PARSER, series_page)[0]
                default_versum      = 'Sub types are not supported in this handler' #Default version summary for series (otherwise we'll have to query all the avaliable episodes pages

                for episode in all_episodes:
                    #json returns the ids as number, so conversion to str is needed
                    season_id   = str(episode['season_id'])
                    episode_id  = str(episode['episode_id'])
                    #We put fomratted version of the episode in order to match the file name format. for example: The.Big.Bang.Theory.S05E16.720p.HDTV.X264-DIMENSION
                    #The rjust function is used in order to create 2 digit wide number.
                    fotmatted_episode = 'S%sE%s' % (season_id.rjust(2, '0'), episode_id.rjust(2, '0'))
                    subMovies.append(SubResult.SubMovie('%s/%s/%s' % (movie_code, season_id, episode_id), 
                                                        '%s %s' % (series_name, fotmatted_episode), default_versum, {'type' : 'series'}))
        
        return subMovies

    @staticmethod
    def findversionslist( subMovie ):
        sub_versions = []
        #If it's a movie, the results are already inside the Extra param
        if subMovie.Extra['type'] == 'movie':
            sub_versions = subMovie.Extra['all_versions']
        #Else, on series, we still got work to do
        else:
            versions_page = Utils.performrequest(SUBSCENTER_PAGES.DOMAIN, SUBSCENTER_PAGES.SERIES % subMovie.MovieCode)
            #Dict of the versions
            versions_area_content   = Utils.getregexresults(SUBSCENTER_REGEX.VERSIONS_VAR, versions_page)            
            (ver_sum, sub_versions) = SubsCenterHandler.getVersionsList(versions_area_content)            

        return map(lambda e: SubResult.SubVersion(**e) ,sub_versions)

    
    @staticmethod
    def getsuburl( subVersion ):
        return(SUBSCENTER_PAGES.DOMAIN,
               SUBSCENTER_PAGES.DOWN_PAGE % (SUBSCENTER_PAGES.LANG, 
                                             subVersion.MovieCode, 
                                             subVersion.VerSum.replace(' ', '%20'), #Replace spaces with their code
                                             subVersion.VerCode))
