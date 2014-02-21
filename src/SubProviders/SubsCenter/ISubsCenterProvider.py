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
    DOMAIN      = r'subscenter.cinemast.com'
    SEARCH      = r'/he/subtitle/search/?q=%s'
    MOVIE_JSON  = r'/he/cinemast/data/movie/sb/%s/'
    SERIES      = r'/he/subtitle/series/%s/'
    SERIES_JSON = r'/he/cinemast/data/series/sb/%s/%s/%s/' # series, season, episode
    DOWN_PAGE   = r'/subtitle/download/%s/%s/?v=%s&key=%s' # lang, code, version, key
    LANGUAGE    = None

class SUBSCENTER_REGEX:
    SEARCH_RESULTS_PARSER   = \
        r'\<a href\=\"http\:\/\/subscenter.cinemast.com\/he\/subtitle\/' \
        '(?P<Type>movie|series)\/(?P<Code>[A-Za-z0-9\-]*?)\/\">' \
        '(?P<MovieName>[^>]*?)</a>'
    SERIES_VAR  = r'var episodes_group = (.*?}}})'


def getJson(content):
    def asciirepl(match):
        return '\\u00' + match.group()[2:]

    p = re.compile(r'\\x(\w{2})')
    content = p.sub(asciirepl, content)
    return json.loads(content)


class ISubsCenterProvider(ISubProvider):
    PROVIDER_NAME = 'Base - www.subscenter.org'
    PROVIDER_PNG  = 'icon-subprovider-subscenter.png'

    @staticmethod
    def getEpisodesList(series_area_content):
        """
            This function will get the series page, and return all the episodes 
            inside this page return value will be List<season_id, episode_id>.
        """
        all_episodes = []
        try:
            jsoned_series_page_dict = getJson(series_area_content[0])
            total_seasons = jsoned_series_page_dict.keys()
        
            for season in total_seasons:
                total_episodes = jsoned_series_page_dict[season].keys()
                for episode in total_episodes:
                    all_episodes.append({
                        'season_id' : 
                        jsoned_series_page_dict[season][episode]['season_id'],
                        
                        'episode_id': 
                        jsoned_series_page_dict[season][episode]['episode_id']})

        except Exception as eX:
            WriteDebug('Failed: getEpisodesList->%s' % eX)

        return all_episodes

    @staticmethod
    def getVersionsList(versions_json):
        """
            This function will get the versions page of the movie/series and 
            return a tuple of vesrions summary and a formatted dictionary where 
            each key is the version_sum and the values are movie_code, 
            version_code and downloads count.
        """
        
        # A dictionary where the keys are the version_sum, and the values are
        # dicts of movie_code, version_code and downloads.
        all_versions    = {}
        ver_sum         = ''

        try:
            jsoned_movie_page_dict = getJson(versions_json)
            current_language_providers = \
                jsoned_movie_page_dict[SUBSCENTER_PAGES.LANGUAGE]

            total_qualities = []

            # Extract the qualities from each provider.
            for qualities in current_language_providers.values():
                for quality, versions in qualities.iteritems():
                    # Insert to the VerSum if not generic quality (ALL), or 
                    # alreadt in the list.
                    if quality != 'ALL' and not quality in total_qualities:
                        total_qualities.append(quality)        

                    for version in versions.values():
                        # Normalize the version sum.
                        version_sum = version['subtitle_version'].lower()
                        downloads = int(version['downloaded'])
                        
                        version_in_dict = all_versions.get(version_sum)
                        # If not in the dict, or the one in the dict has less
                        # downloads, put the new one in the dict.
                        if not version_in_dict or \
                            version_in_dict['downloads'] <= downloads:

                            all_versions[version_sum] = {
                                "movie_code"    : version['id'],
                                "version_code"  : version['key'],
                                'downloads'     : downloads
                            }
                        
                            WriteDebug('Subscenter version: %s' % all_versions[version_sum])
                        
            ver_sum = ' / '.join(total_qualities)
        except Exception as eX:
            WriteDebug('Failed: getVersionsList->%s' % eX)

        return (ver_sum, all_versions)

    @classmethod
    def _getMovieSubStageForMovie(cls, movie_name, movie_code):
        versions_json = Utils.PerformRequest(
            SUBSCENTER_PAGES.DOMAIN, 
            SUBSCENTER_PAGES.MOVIE_JSON % movie_code)

        (ver_sum, all_versions) = \
            ISubsCenterProvider.getVersionsList(versions_json)
               
        return MovieSubStage(
            cls.PROVIDER_NAME, 
            movie_name, 
            movie_code, 
            ver_sum, 
            # Add special info.
            {'type' : 'movie', 'all_versions' : all_versions})


    @classmethod
    def _getMovieSubStagesForSeries(cls, series_name, movie_code):
        series_page = Utils.PerformRequest(
            SUBSCENTER_PAGES.DOMAIN, 
            SUBSCENTER_PAGES.SERIES % movie_code)
        series_area_content = Utils.getregexresults(
            SUBSCENTER_REGEX.SERIES_VAR, 
            series_page)
        all_episodes = \
            ISubsCenterProvider.getEpisodesList(series_area_content)

        # Default version summary for series (otherwise we'll have to 
        # query all the avaliable episodes pages
        default_versum = 'Sub types are not supported in this provider' 

        for episode in all_episodes:
            # json returns the ids as number, so conversion to str is 
            # needed.
            season_id   = str(episode['season_id'])
            episode_id  = str(episode['episode_id'])
            # We put fomratted version of the episode in order to match 
            # the file name format. for example: 
            # The.Big.Bang.Theory.S05E16.720p.HDTV.X264-DIMENSION
            # The rjust function is used in order to create 2 digit 
            # wide number.
            fotmatted_episode = 'S%sE%s' % \
                (season_id.rjust(2, '0'), episode_id.rjust(2, '0'))
            yield MovieSubStage(
                cls.PROVIDER_NAME, 
                '%s %s' % (series_name, fotmatted_episode),
                '%s/%s/%s' % (movie_code, season_id, episode_id), 
                default_versum,
                {'type' : 'series'})

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findMovieSubStageList(cls, query_sub_stage):
        moviename   = query_sub_stage.query.lower()
        movies_info = []
        _movie_sub_stages = []

        result_page = Utils.PerformRequest(
            SUBSCENTER_PAGES.DOMAIN, 
            SUBSCENTER_PAGES.SEARCH % moviename.replace(' ', '+'))

        movies_info = Utils.getregexresults(
            SUBSCENTER_REGEX.SEARCH_RESULTS_PARSER, result_page, True)

        for movie_info in movies_info:
            movie_code = movie_info['Code']
            movie_type = movie_info['Type']
            movie_name = movie_info['MovieName']

            try:
                # Left side is the hebrew name, the right is english.
                movie_name = movie_name.split(' / ')[1]
            except:
                # If failed, keep the original name.
                movie_name = movie_info['MovieName']

            WriteDebug('Working on %s' % movie_type)
            
            if movie_type == 'movie':
                _movie_sub_stages.append(
                    cls._getMovieSubStageForMovie(movie_name, movie_code))
            
            elif movie_type == 'series':
                for stage in \
                    cls._getMovieSubStagesForSeries(movie_name, movie_code):
                    _movie_sub_stages.append(stage)

        return _movie_sub_stages

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findVersionSubStageList(cls, movie_sub_stage):

        # A dictionary where keys are the version_sum and the values are dicts 
        # with movie_code and version_code.
        all_versions = {}

        # If it's a movie, the results are already inside the extra param.
        if movie_sub_stage.extra['type'] == 'movie':
            all_versions = movie_sub_stage.extra['all_versions']
        # Else, on series, we still got work to do
        else:
            series_code = movie_sub_stage.movie_code
               
            versions_json = Utils.PerformRequest(
                SUBSCENTER_PAGES.DOMAIN, 
                SUBSCENTER_PAGES.SERIES_JSON % tuple(series_code.split("/")))
            (ver_sum, all_versions) = \
                ISubsCenterProvider.getVersionsList(versions_json)            

        version_sub_stages = []
        for version_sum, item in all_versions.iteritems():
            version_sub_stages.append(
                VersionSubStage(
                    cls.PROVIDER_NAME,
                    version_sum,
                    item['version_code'],
                    item['movie_code']))

        return version_sub_stages

    
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
