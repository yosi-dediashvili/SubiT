import json
import re

import SubiT
from SubStages.MovieSubStage import MovieSubStage
from SubStages.VersionSubStage import VersionSubStage
import Utils
WriteDebug = Utils.WriteDebug

from Utils import HttpRequestTypes

from SubProviders.ISubProvider import ISubProvider

class SUBSCENTER_LANGUAGES:
    ENGLISH = 'en'
    HEBREW  = 'he'

class SUBSCENTER_PAGES:
    DOMAIN      = r'www.subscenter.org'
    SEARCH      = r'/he/subtitle/search/?q=%s'
    MOVIE       = r'/he/subtitle/movie/%s/'
    SERIES      = r'/he/subtitle/series/%s/'
    DOWN_PAGE   = r'/he/subtitle/download/%s/%s/?v=%s&key=%s' #lang, code, version, key
    LANGUAGE    = None

class SUBSCENTER_REGEX:
    NAME_IN_SITE_PARSER     = r'<h3>(.*?)\s*?</h3>'
    SEARCH_RESULTS_PARSER   = r'\<a href\=\"\/he\/subtitle\/(?P<Type>movie|series)\/(?P<Code>[A-Za-z0-9\-]*?)\/\">[^>]*?</a>'
    URL_RESULT_PARSER       = r'/he\/subtitle\/(?P<Type>movie|series)\/(?P<Code>[A-Za-z0-9\-]*?)\/'
    VERSIONS_VAR            = r'subtitles_groups = (.*?}}}}})'
    SERIES_VAR              = r'var episodes_group = (.*?}}})'


def getJson(content):
    def asciirepl(match):
        return '\\u00' + match.group()[2:]

    p = re.compile(r'\\x(\w{2})')
    content = p.sub(asciirepl, content)
    return json.loads(content)


class ISubsCenterProvider(ISubProvider):
    PROVIDER_NAME = 'Base - www.subscenter.org'
    PROVIDER_PNG  = 'icon-subprovider-subscenter.png'

    #This function will get the series page, and return all the episodes inside this page
    #Return value will be List<season_id, episode_id>
    @staticmethod
    def getEpisodesList(series_area_content):
        all_episodes = []
        try:
            jsoned_series_page_dict = getJson(series_area_content[0])
            #jsoned_series_page_dict = json.loads(series_area_content[0].replace('\'', '"'))#.replace('\\\\', '\\'))
            total_seasons = jsoned_series_page_dict.keys()
        
            for season in total_seasons:
                total_episodes = jsoned_series_page_dict[season].keys()
                for episode in total_episodes:
                    all_episodes.append({'season_id' : jsoned_series_page_dict[season][episode]['season_id'],
                                         'episode_id': jsoned_series_page_dict[season][episode]['episode_id']})
        except Exception as eX:
            WriteDebug('Failed: getEpisodesList->%s' % eX)

        return all_episodes

    #This function will get the versions page of the movie/series and return a formettd list of:
    #List<movie_code, ver_code, ver_sum>
    @staticmethod
    def getVersionsList(versions_area_content):
        all_versions    = []
        ver_sum         = ''

        try:
            jsoned_movie_page_dict = getJson(versions_area_content[0])
            #jsoned_movie_page_dict = json.loads(versions_area_content[0].replace('\'', '"').replace('\\\\', '\\'))
            lang = SUBSCENTER_PAGES.LANGUAGE
        
            total_providers = jsoned_movie_page_dict[lang].keys()
            total_ver_types = []
            all_versions    = []
            for provider in total_providers:
                for ver_type in jsoned_movie_page_dict[lang][provider]:
                    #If the version type is not ALL, we insert it to the list of the versions type, in order to show it in the subMovie.VerSum
                    if ver_type != 'ALL' and not ver_type in total_ver_types:
                        total_ver_types.append(ver_type)
                    for ver in jsoned_movie_page_dict[lang][provider][ver_type]:
                        moviecode   = jsoned_movie_page_dict[lang][provider][ver_type][ver]['id']
                        vercode     = jsoned_movie_page_dict[lang][provider][ver_type][ver]['key']
                        versum      = jsoned_movie_page_dict[lang][provider][ver_type][ver]['subtitle_version']

                        WriteDebug('moviecode: %s | vercode: %s | versum: %s' % (moviecode, vercode, versum))

                        all_versions.append({'moviecode' : moviecode,
                                                'vercode'   : vercode,
                                                'versum'    : versum})
            
            ver_sum = ' / '.join(total_ver_types)
        except Exception as eX:
            WriteDebug('Failed: getVersionsList->%s' % eX)

        return (ver_sum, all_versions)


    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findMovieSubStageList(cls, query_sub_stage):
        moviename   = query_sub_stage.query.lower()
        movies_info = []
        _movie_sub_stages = []
        searchresult = Utils.PerformRequest(SUBSCENTER_PAGES.DOMAIN, 
                                            SUBSCENTER_PAGES.SEARCH % moviename.replace(' ', '+'))
        #Search results
        movies_info = Utils.getregexresults(SUBSCENTER_REGEX.SEARCH_RESULTS_PARSER, searchresult, True)


        for movie_info in movies_info:
            movie_code = movie_info['Code']
            movie_type = movie_info['Type']

            WriteDebug('Working on %s' % movie_type)
            #===================================================================
            #If the result is movie
            if movie_type == 'movie':
                movie_page = Utils.PerformRequest(  SUBSCENTER_PAGES.DOMAIN, 
                                                    SUBSCENTER_PAGES.MOVIE % movie_code)
                #Dict of the versions
                versions_area_content   = Utils.getregexresults(SUBSCENTER_REGEX.VERSIONS_VAR, movie_page)            
                (ver_sum, all_versions) = ISubsCenterProvider.getVersionsList(versions_area_content)
                movie_name              = Utils.getregexresults(SUBSCENTER_REGEX.NAME_IN_SITE_PARSER, movie_page)[0]
            
                _movie_sub_stages.append(MovieSubStage\
                    (cls.PROVIDER_NAME, movie_name, movie_code, ver_sum, 
                     {'type' : 'movie', 'all_versions' : all_versions}))
                WriteDebug('Added MovieCode: %s' % movie_code)
            #===================================================================
            #If the result is series
            else:
                series_page         = Utils.PerformRequest(SUBSCENTER_PAGES.DOMAIN, SUBSCENTER_PAGES.SERIES % movie_code)
                series_area_content = Utils.getregexresults(SUBSCENTER_REGEX.SERIES_VAR, series_page)
                all_episodes        = ISubsCenterProvider.getEpisodesList(series_area_content)
                series_name         = Utils.getregexresults(SUBSCENTER_REGEX.NAME_IN_SITE_PARSER, series_page)[0]
                # Default version summary for series (otherwise we'll have to query all 
                # the avaliable episodes pages
                default_versum      = 'Sub types are not supported in this provider' 

                for episode in all_episodes:
                    #json returns the ids as number, so conversion to str is needed
                    season_id   = str(episode['season_id'])
                    episode_id  = str(episode['episode_id'])
                    # We put fomratted version of the episode in order to match the file name format. 
                    # for example: The.Big.Bang.Theory.S05E16.720p.HDTV.X264-DIMENSION
                    # The rjust function is used in order to create 2 digit wide number.
                    fotmatted_episode = 'S%sE%s' % (season_id.rjust(2, '0'), episode_id.rjust(2, '0'))
                    _movie_sub_stages.append(MovieSubStage\
                        (cls.PROVIDER_NAME, '%s %s' % (series_name, fotmatted_episode),
                         '%s/%s/%s' % (movie_code, season_id, episode_id), default_versum,
                         {'type' : 'series'}))

        return _movie_sub_stages

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findVersionSubStageList(cls, movie_sub_stage):
        _version_sub_stages = []
        #If it's a movie, the results are already inside the Extra param
        if movie_sub_stage.extra['type'] == 'movie':
            _version_sub_stages = movie_sub_stage.extra['all_versions']
        #Else, on series, we still got work to do
        else:
            versions_page = Utils.PerformRequest(SUBSCENTER_PAGES.DOMAIN, SUBSCENTER_PAGES.SERIES % movie_sub_stage.movie_code)
            #Dict of the versions
            versions_area_content   = Utils.getregexresults(SUBSCENTER_REGEX.VERSIONS_VAR, versions_page)            
            (ver_sum, _version_sub_stages) = ISubsCenterProvider.getVersionsList(versions_area_content)            

        return map(lambda e: VersionSubStage\
            (cls.PROVIDER_NAME, e['versum'], e['vercode'], e['moviecode']), _version_sub_stages)

    
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def getSubtitleContent(cls, version_sub_stage):
        download_page = SUBSCENTER_PAGES.DOWN_PAGE % (
            SUBSCENTER_PAGES.LANGUAGE, 
            version_sub_stage.movie_code, 
            # Replace spaces with their code
            version_sub_stage.version_sum.replace(' ', '%20'), 
            version_sub_stage.version_code)

        return Utils.DownloadSubAsBytesIO(SUBSCENTER_PAGES.DOMAIN,
                                          download_page,
                                          SUBSCENTER_PAGES.DOMAIN,
                                          None)
