import SubiT


from SubStages.VersionSubStage import VersionSubStage
from SubStages.MovieSubStage import MovieSubStage
import Utils
WriteDebug = Utils.WriteDebug

from itertools import groupby
from Utils import HttpRequestTypes

from SubProviders.ISubProvider import ISubProvider

class SUBTITLE_LANGUAGES:
    HEBREW  = b'\xd7\xa2\xd7\x91\xd7\xa8\xd7\x99\xd7\xaa'.decode('utf-8')
    ENGLISH = b'\xd7\x90\xd7\xa0\xd7\x92\xd7\x9c\xd7\x99\xd7\xaa'.decode('utf-8')

class SUBTITLE_PAGES:
    DOMAIN              = 'www.subtitle.co.il'
    SEARCH              = '/browse.php?q=%s'
    MOVIE_SUBTITLES     = '/view.php?id=%s&m=subtitles'
    SERIES_SUBTITLES    = '/viewseries.php?id=%s&m=subtitles#'
    SERIES_SEASON       = '/viewseries.php?id=%s&m=subtitles&s=%s'      # SeriesId & SeasonId
    SERIES_EPISODE      = '/viewseries.php?id=%s&m=subtitles&s=%s&e=%s' # SeriesId & SeasonId & EpisodeId
    DOWNLOAD            = '/downloadsubtitle.php?id=%s'
    LANGUAGE            = None
    USER                = "372162"
    PASS                = "CC4F66x00DFB69tt15C150amAC1391xeFDCE875nE6"
    CRED                = "slcoo_user_id=%s; slcoo_user_pass=%s;" % (USER, PASS) # The credentials that should be sent with requests as cookies.

class SUBTITLE_REGEX:
    TV_SERIES_RESULTS_PARSER    = '<div class=\"browse_title_name\" itemprop=\"name\"><a href=\"viewseries.php\?id=(?P<MovieCode>\d+).*?class=\"smtext">(?P<MovieName>.*?)</div>'
    TV_SEASON_PATTERN           = 'seasonlink_(?P<SeasonCode>\d+).*?>(?P<SeasonNum>\d+)</a>'
    TV_EPISODE_PATTERN          = 'episodelink_(?P<EpisodeCode>\d+).*?>(?P<EpisodeNum>\d+)</a>'
    MOVIE_RESULTS_PARSER        = '<div class=\"browse_title_name\" itemprop=\"name\"><a href=\"view.php\?id=(?P<MovieCode>\d+).*?class=\"smtext">(?P<MovieName>.*?)</div>'
    SUBTITLE_LIST_PARSER        = 'downloadsubtitle\.php\?id=(?P<VerCode>\d*).*?subt_lang.*?title=\"(?P<Language>.*?)\".*?subtitle_title.*?title=\"(?P<VerSum>.*?)\"'
    VER_SUM_PARSER              = '<td class=\"FamilySubtitlesVerisons\"><a name="f\d"></a>(.*?)</td>'


class ISubtitleProvider(ISubProvider):
    PROVIDER_NAME = 'Base - www.subtitle.co.il'
    PROVIDER_PNG  = 'icon-subprovider-subtitle.png'

    #Method to check if the search result gave us a movie or series
    @staticmethod
    def isSeries(search_content):
        return bool(Utils.getregexresults(SUBTITLE_REGEX.TV_SERIES_RESULTS_PARSER, search_content))
    
    @staticmethod
    def getSeasonsList(series_code):
        WriteDebug('Working on series: %s' % series_code)
        series_page = Utils.PerformRequest( SUBTITLE_PAGES.DOMAIN,
                                            SUBTITLE_PAGES.SERIES_SUBTITLES % series_code,
                                            more_headers = {"Cookie" : SUBTITLE_PAGES.CRED})
        WriteDebug('Got series page')
        total_seasons = Utils.getregexresults(SUBTITLE_REGEX.TV_SEASON_PATTERN, series_page, True)
        WriteDebug('Got total of %s seasons' % len(total_seasons))
        return total_seasons
    
    @staticmethod
    def getEpisodesList(series_code, season_code):
        WriteDebug('Working on season: %s' % season_code)
        season_page = Utils.PerformRequest( SUBTITLE_PAGES.DOMAIN,
                                            SUBTITLE_PAGES.SERIES_SEASON % (series_code, season_code),
                                            more_headers = {"Cookie" : SUBTITLE_PAGES.CRED})
        WriteDebug('Got season page')
        total_episodes = Utils.getregexresults(SUBTITLE_REGEX.TV_EPISODE_PATTERN, season_page, True)
        WriteDebug('Got total of %s episodes' % len(total_episodes))
        return total_episodes

    @staticmethod
    def getVersionsList(page_content):
        results = Utils.getregexresults(SUBTITLE_REGEX.SUBTITLE_LIST_PARSER, page_content, True)
        WriteDebug('Got %s versions' % len(results))
        return results

    #====================================================================================#
    # Interface Functions area                                                  
    #====================================================================================#
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findMovieSubStageList(cls, query_sub_stage):
        moviename       = query_sub_stage.query
        searchresult    = Utils.PerformRequest(
                                               SUBTITLE_PAGES.DOMAIN, 
                                               SUBTITLE_PAGES.SEARCH % moviename.replace(' ', '+'),
                                               more_headers = {"Cookies" : SUBTITLE_PAGES.CRED})

        #extract movies from the page
        movie_results = list(map(lambda r: {'content': r, 'type': 'movie'}, Utils.getregexresults(SUBTITLE_REGEX.MOVIE_RESULTS_PARSER, 
                                                                                             searchresult, True)))
        #If we got series in the result, extract it too
        if ISubtitleProvider.isSeries(searchresult):
            for series in Utils.getregexresults(SUBTITLE_REGEX.TV_SERIES_RESULTS_PARSER, searchresult, True):
                WriteDebug('Got series result also: %s' % series['MovieName'])
                movie_results.append({'content': series, 'type': 'series'})
        
        _movie_sub_stages = []
        default_versum = 'Sub types are not supported in this provider'
        for type, results in groupby(movie_results, lambda i: i['type']):
            #=============================================================================
            #Handle movies results
            if type == 'movie':
                WriteDebug('Working on type: %s' % type)
                for result in results:
                    moviecode = result['content']['MovieCode']
                    moviename = result['content']['MovieName']

                    WriteDebug('Working on movie: %s' % moviename)
                    page_content = Utils.PerformRequest(
                                                        SUBTITLE_PAGES.DOMAIN, 
                                                        SUBTITLE_PAGES.MOVIE_SUBTITLES % moviecode,
                                                        more_headers = {"Cookie" : SUBTITLE_PAGES.CRED})
                    versum = ' / '.join(Utils.getregexresults(SUBTITLE_REGEX.VER_SUM_PARSER, page_content))
                    all_vers = ISubtitleProvider.getVersionsList(page_content)

                    #Append result to the subMovies List
                    _movie_sub_stages.append(MovieSubStage\
                        (cls.PROVIDER_NAME, moviename, moviecode, versum, all_vers))

            #=============================================================================
            #Handle serieses results
            elif type == 'series':
                WriteDebug('Working on type: %s' % type)
                for result in results:
                    seriescode          = result['content']['MovieCode']
                    seriesname          = result['content']['MovieName']
                    total_seasons       = ISubtitleProvider.getSeasonsList(seriescode)
                    
                    #Iterate through all relevant seasons
                    for season in total_seasons:
                        seasoncode = season['SeasonCode']
                        seasonnum  = season['SeasonNum']
                        
                        total_episodes = ISubtitleProvider.getEpisodesList(seriescode, seasoncode)
                        for episode in total_episodes:
                            #Formatted version of the episode number. ie. S03E14...
                            formated_episode = 'S%sE%s' % (seasonnum.rjust(2, '0'), episode['EpisodeNum'].rjust(2, '0'))
                            #Insert the episode to the list
                            _movie_sub_stages.append(MovieSubStage\
                                (cls.PROVIDER_NAME, '%s %s' % (seriesname, formated_episode), 
                                 episode['EpisodeCode'], default_versum, 
                                 {'series_code' : seriescode, 'season_code' : seasoncode}))
                        
        return _movie_sub_stages


    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findVersionSubStageList(cls, movie_sub_stage):
        moviecode   = movie_sub_stage.movie_code
        extra_info  = movie_sub_stage.extra
        _version_sub_stages = []

        #If the info is list, it means we got only the sub_versions items
        if type(extra_info) is list:
            #Using own implementation of the filter function.
            #We filter out any subtitle from different language and his VerSum value is null
            _version_sub_stages =  Utils.myfilter(lambda r: r['Language'] == SUBTITLE_PAGES.LANGUAGE and r['VerSum'] != '', extra_info, 
                                                  #Create SubVersion object from each item
                                                  lambda i: VersionSubStage(cls.PROVIDER_NAME, i['VerSum'], i['VerCode'], moviecode))
        #Otherwise, it's dict -> will be for season's episode
        else:
            series_code  = extra_info['series_code']
            season_code  = extra_info['season_code']
            episode_code = moviecode
                        
            WriteDebug('Working on episode: %s' % episode_code)
            episode_page = Utils.PerformRequest(SUBTITLE_PAGES.DOMAIN,
                                                SUBTITLE_PAGES.SERIES_EPISODE % (series_code, season_code, episode_code),
                                                more_headers = {"Cookie" : SUBTITLE_PAGES.CRED})
            WriteDebug('Got episode page')
            versions_list = ISubtitleProvider.getVersionsList(episode_page)
            filter_func = lambda v: (v['Language'] == 
                                     SUBTITLE_PAGES.LANGUAGE and v['VerSum'] != '')
            for episode_ver in list(filter(filter_func, versions_list)):
                #Add version to the list
                _version_sub_stages.append(VersionSubStage\
                    (cls.PROVIDER_NAME, episode_ver['VerSum'], 
                     episode_ver['VerCode'], moviecode))

        return _version_sub_stages

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def getSubtitleContent(cls, version_sub_stage):
        return Utils.DownloadSubAsBytesIO(
            SUBTITLE_PAGES.DOMAIN, 
            SUBTITLE_PAGES.DOWNLOAD % version_sub_stage.version_code,
            SUBTITLE_PAGES.DOMAIN,
            SUBTITLE_PAGES.CRED)