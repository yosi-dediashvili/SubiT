import SubiT
import SubResult
import Utils

from itertools import groupby
from Utils import HttpRequestTypes

from SubHandlers.ISubHandler import ISubHandler

class SRATIM_LANGUAGES:
    HEBREW  = '\xd7\xa2\xd7\x91\xd7\xa8\xd7\x99\xd7\xaa'
    ENGLISH = '\xd7\x90\xd7\xa0\xd7\x92\xd7\x9c\xd7\x99\xd7\xaa'

class SRATIM_PAGES:
    DOMAIN              = 'www.sratim.co.il'
    SEARCH              = '/browse.php?q=%s'
    MOVIE_SUBTITLES     = '/view.php?id=%s&m=subtitles#'
    SERIES_SUBTITLES    = '/viewseries.php?id=%s&m=subtitles#'
    SERIES_SEASON       = '/viewseries.php?id=%s&m=subtitles&s=%s'      # SeriesId & SeasonId
    SERIES_EPISODE      = '/viewseries.php?id=%s&m=subtitles&s=%s&e=%s' # SeriesId & SeasonId & EpisodeId
    DOWNLOAD            = '/downloadsubtitle.php?id=%s'
    LANGUAGE            = SRATIM_LANGUAGES.HEBREW

class SRATIM_REGEX:
    TV_SERIES_RESULTS_PARSER    = '<div style=\"\"><a href=\"viewseries.php\?id=(?P<MovieCode>\d+).*?class=\"smtext">(?P<MovieName>.*?)</div>'
    TV_SEASON_PATTERN           = 'seasonlink_(?P<SeasonCode>\d+).*?>(?P<SeasonNum>\d+)</a>'
    TV_EPISODE_PATTERN          = 'episodelink_(?P<EpisodeCode>\d+).*?>(?P<EpisodeNum>\d+)</a>'
    MOVIE_RESULTS_PARSER        = '<div style=\"\"><a href=\"view.php\?id=(?P<MovieCode>\d+).*?class=\"smtext">(?P<MovieName>.*?)</div>'
    SUBTITLE_LIST_PARSER        = 'downloadsubtitle\.php\?id=(?P<VerCode>\d*).*?subt_lang.*?title=\"(?P<Language>.*?)\".*?subtitle_title.*?title=\"(?P<VerSum>.*?)\"'
    VER_SUM_PARSER              = '<td class=\"FamilySubtitlesVerisons\"><a name="f\d"></a>(.*?)</td>'


class ISratimHandler(ISubHandler):
    HANDLER_NAME = 'Base - www.sratim.co.il'

    #Method to check if the search result gave us a movie or series
    @staticmethod
    def isSeries(search_content):
        return bool(Utils.getregexresults(SRATIM_REGEX.TV_SERIES_RESULTS_PARSER, search_content))
    
    @staticmethod
    def getSeasonsList(series_code):
        Utils.WriteDebug('Working on series: %s' % series_code)
        series_page = Utils.performrequest( SRATIM_PAGES.DOMAIN,
                                            SRATIM_PAGES.SERIES_SUBTITLES % series_code)
        Utils.WriteDebug('Got series page')
        total_seasons = Utils.getregexresults(SRATIM_REGEX.TV_SEASON_PATTERN, series_page, True)
        Utils.WriteDebug('Got total of %s seasons' % len(total_seasons))
        return total_seasons
    
    @staticmethod
    def getEpisodesList(series_code, season_code):
        Utils.WriteDebug('Working on season: %s' % season_code)
        season_page = Utils.performrequest( SRATIM_PAGES.DOMAIN,
                                            SRATIM_PAGES.SERIES_SEASON % (series_code, season_code))
        Utils.WriteDebug('Got season page')
        total_episodes = Utils.getregexresults(SRATIM_REGEX.TV_EPISODE_PATTERN, season_page, True)
        Utils.WriteDebug('Got total of %s episodes' % len(total_episodes))
        return total_episodes

    @staticmethod
    def getVersionsList(page_content):
        results = Utils.getregexresults(SRATIM_REGEX.SUBTITLE_LIST_PARSER, page_content, True)
        Utils.WriteDebug('Got %s versions' % len(results))
        return results

    #====================================================================================#
    # Interface Functions area                                                  
    #====================================================================================#
    @staticmethod
    def findmovieslist( subSearch ):
        moviename       = subSearch.Query
        searchresult    = Utils.performrequest(SRATIM_PAGES.DOMAIN, SRATIM_PAGES.SEARCH % moviename.replace(' ', '+'))

        #extract movies from the page
        movie_results = map(lambda r: {'content': r, 'type': 'movie'}, Utils.getregexresults(SRATIM_REGEX.MOVIE_RESULTS_PARSER, 
                                                                                             searchresult, True))
        #If we got series in the result, extract it too
        if ISratimHandler.isSeries(searchresult):
            for series in Utils.getregexresults(SRATIM_REGEX.TV_SERIES_RESULTS_PARSER, searchresult, True):
                Utils.WriteDebug('Got series result also: %s' % series['MovieName'])
                movie_results.append({'content': series, 'type': 'series'})
        
        subMovies = []
        default_versum = 'Sub types are not supported in this handler'
        for type, results in groupby(movie_results, lambda i: i['type']):
            #=============================================================================
            #Handle movies results
            if type == 'movie':
                Utils.WriteDebug('Working on type: %s' % type)
                for result in results:
                    moviecode = result['content']['MovieCode']
                    moviename = result['content']['MovieName']

                    Utils.WriteDebug('Working on movie: %s' % moviename)
                    page_content = Utils.performrequest(SRATIM_PAGES.DOMAIN, SRATIM_PAGES.MOVIE_SUBTITLES % moviecode)
                    versum = ' / '.join(Utils.getregexresults(SRATIM_REGEX.VER_SUM_PARSER, page_content))
                    all_vers = ISratimHandler.getVersionsList(page_content)

                    #Append result to the subMovies List
                    subMovies.append(SubResult.SubMovie(moviecode, moviename, versum, all_vers))

            #=============================================================================
            #Handle serieses results
            elif type == 'series':
                Utils.WriteDebug('Working on type: %s' % type)
                for result in results:
                    seriescode          = result['content']['MovieCode']
                    seriesname          = result['content']['MovieName']
                    total_seasons       = ISratimHandler.getSeasonsList(seriescode)
                    
                    #Iterate through all relevant seasons
                    for season in total_seasons:
                        seasoncode = season['SeasonCode']
                        seasonnum  = season['SeasonNum']
                        
                        total_episodes = ISratimHandler.getEpisodesList(seriescode, seasoncode)
                        for episode in total_episodes:
                            #Formatted version of the episode number. ie. S03E14...
                            formated_episode = 'S%sE%s' % (seasonnum.rjust(2, '0'), episode['EpisodeNum'].rjust(2, '0'))
                            #Insert the episode to the list
                            subMovies.append(SubResult.SubMovie(episode['EpisodeCode'], '%s %s' % (seriesname, formated_episode), 
                                                                default_versum, {'series_code' : seriescode, 'season_code' : seasoncode}))
                        
        return subMovies


    @staticmethod
    def findversionslist( subMovie ):
        moviecode   = subMovie.MovieCode
        extra_info  = subMovie.Extra
        vers_results = []

        #If the info is list, it means we got only the sub_versions items
        if type(extra_info) is list:
            #Using own implementation of the filter function.
            #We filter out any subtitle from different language and his VerSum value is null
            vers_results =  Utils.myfilter( lambda r: r['Language'] == SRATIM_PAGES.LANGUAGE and r['VerSum'] != '', extra_info, 
                                            #Create SubVersion object from each item
                                            lambda i: SubResult.SubVersion(i['VerCode'], i['VerSum'], moviecode))
        #Otherwise, it's dict -> will be for season's episode
        else:
            series_code  = extra_info['series_code']
            season_code  = extra_info['season_code']
            episode_code = moviecode
                        
            Utils.WriteDebug('Working on episode: %s' % episode_code)
            episode_page = Utils.performrequest(SRATIM_PAGES.DOMAIN,
                                                SRATIM_PAGES.SERIES_EPISODE % (series_code, season_code, episode_code))
            Utils.WriteDebug('Got episode page')
            ISratimHandler.getVersionsList(episode_page)
            for episode_ver in filter(lambda f: f['Language'] == SRATIM_PAGES.LANGUAGE and f['VerSum'] != '', ISratimHandler.getVersionsList(episode_page)):
                #Add version to the list
                vers_results.append(SubResult.SubVersion(episode_ver['VerCode'], episode_ver['VerSum'], moviecode))

        return vers_results

    @staticmethod
    def getsuburl( subVersion ):
        return (SRATIM_PAGES.DOMAIN, 
                SRATIM_PAGES.DOWNLOAD % subVersion.VerCode)