from SubProviders.ISubProvider import ISubProvider
from SubStages.MovieSubStage import MovieSubStage
from SubStages.VersionSubStage import VersionSubStage

import Utils
WriteDebug = Utils.WriteDebug

class ADDIC7ED_LANGUAGES:
    HEBREW      = '23'
    ENGLISH     = '1'
    NORWEGIAN   = '29'
    RUSSIAN     = '19'
    SPANISH     = '4'
    TURKISH     = '16'
    SLOVAK      = '25'
    CZECH       = '14'
    GLOBAL      = '0'

class ADDIC7ED_PAGES:
    DOMAIN      = 'www.addic7ed.com'
    SEARCH      = '/search.php?search=%s&Submit=Search'
    LANGUAGE    = None

class ADDIC7ED_REGEX:
    SEARCH_RESULTS_PARSER = ('(?<=<td><a href=\")(?P<MovieCode>.*?)(?:\" debug' +
                             '=\"\d+\">)(?P<MovieName>.*?)(?=</a>)')
    REDIRECT_PAGE_PARSER = (
        '(?<=\<span class\=\"titulo\"\>)' +
        '(?P<MovieName>.*?)(?: \<small\>Subtitle\<\/small\>.*?)' +
        # Catches http://www.addic7ed.com
        '(?<=http\:\/\/www\.addic7ed\.com)' +
        # Catches /serie/The_Big_Bang_Theory/3/4/The_Pirate_Solution
        '(?P<MovieCode>\/serie\/[^\/]*\/\d*\/\d*\/[^\/]*?)' +
        # Catched "
        '(?=\" layout\=\"standard\")')
    RESULT_PAGE_PARSER    = ('(?<=Version )(?P<VerSum>.*?)(?:, .*?javascript\:' +
                             'saveFavorite\(\d+,)(?P<Language>\d+)(?:,\d+\).*?' +
                             '<a class=\"buttonDownload\" href=\")(?P<VerCode>' +
                             '.*?)(?=\">)')

class IAddic7edProvider(ISubProvider):
    PROVIDER_NAME = 'Base - www.addic7ed.com'
    PROVIDER_PNG  = 'icon-subprovider-addic7ed.png'

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findMovieSubStageList(cls, query_sub_stage):

        is_series = Utils.IsSeries(query_sub_stage.query)
        query = query_sub_stage.query.replace(' ', '+')

        WriteDebug('Sending query for [%s]: %s' % (is_series, query))
        # Send the query to the server. Notice that Addic7ed may redirect us to
        # the episode's page (in case of a series query) if it find an exact 
        # match to our query.
        query_data = Utils.PerformRequest(ADDIC7ED_PAGES.DOMAIN, 
                                          ADDIC7ED_PAGES.SEARCH % query)
        re_results = Utils.getregexresults(ADDIC7ED_REGEX.SEARCH_RESULTS_PARSER, 
                                           query_data, True)
        
        WriteDebug('Query for %s returned %s results' % (query, len(re_results)))
        _movie_sub_stages = []

        # If we didn't find any result, and this is a series, it might be a 
        # redirection, so we'll try to extract the episode info.
        if not re_results and is_series:
            WriteDebug("Suspecting it's a redirection, checking series.")
            re_results = Utils.getregexresults(
                ADDIC7ED_REGEX.REDIRECT_PAGE_PARSER, query_data, True)
            if re_results:
                WriteDebug("It's indeed a redirection.")
                movie_name = re_results[0]['MovieName']
                movie_name = movie_name.strip()
                movie_sub_stage = MovieSubStage(
                    cls.PROVIDER_NAME,
                    movie_name,
                    re_results[0]['MovieCode'],
                    '')
                _movie_sub_stages.append(movie_sub_stage)
                return _movie_sub_stages
            else:
                WriteDebug("Series check returned no results.")


        # The upper limit for the language check
        check_lang_in_stage = (len(re_results) <= 10)

        for result in re_results:
            # Take the type of the result (either movie or serie)
            result_type = result['MovieCode'].split('/', 1)
            # Make sure we're not crashing (because of invalid index).
            result_type = result_type[0] if result_type else 'unknown'

            # If the type does not match, skip the result.
            if result_type == 'movie' and is_series:
                continue
            elif result_type == 'serie' and not is_series:
                continue
            elif result_type == 'unknown':
                continue
            
            movie_sub_stage = MovieSubStage(
                cls.PROVIDER_NAME, 
                result['MovieName'], 
                result['MovieCode'], 
                '')

            WriteDebug('Adding MovieSubStage. Details: %s' % movie_sub_stage.info())

            # Because addi7ed doesnt say anything about the language if it's
            # missing, we need to check for each movie_sub_stage we get.
            # We also check if we should check the language, because we might
            # end up checking it for 1000 resuls, which might take some time...
            if check_lang_in_stage and not movie_sub_stage.getVersionSubStages():
                continue

            # If we got here, we wither don't need to check for the versions,
            # or we got versions.
            _movie_sub_stages.append(movie_sub_stage)

        return _movie_sub_stages

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findVersionSubStageList(cls, movie_sub_stage):
        # We need to deliver the url with slash at the start in order to join
        # the domain and the url correctly
        version_url = '/' + movie_sub_stage.movie_code

        version_data = Utils.PerformRequest(ADDIC7ED_PAGES.DOMAIN, version_url)
        re_results = Utils.getregexresults(ADDIC7ED_REGEX.RESULT_PAGE_PARSER,
                                           version_data, True)
        WriteDebug('%s: returned %s results' % (version_url, len(re_results)))
        # Take only results from the selected language
        WriteDebug('Filtering languages of code: %s' % ADDIC7ED_PAGES.LANGUAGE)
        re_results = Utils.myfilter\
            (lambda r: (r['Language'] == ADDIC7ED_PAGES.LANGUAGE), re_results)
        WriteDebug('Left with %s results after filtering' % len(re_results))

        _version_sub_stages = []
        for result in re_results:
            version_sub_stage = VersionSubStage(cls.PROVIDER_NAME,
                result['VerSum'], result['VerCode'], movie_sub_stage.movie_code)
            WriteDebug('Adding VersionSubStage. Details: %s' % version_sub_stage.info())
            _version_sub_stages.append(version_sub_stage)

        return _version_sub_stages
    
    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def getSubtitleContent(cls, version_sub_stage):
        referer = '/'.join(
            [ADDIC7ED_PAGES.DOMAIN, version_sub_stage.movie_code])
        referer = 'http://' + referer

        WriteDebug('Setting the referer to be: %s' % referer)
        # In order to download the subtitle we need to set the movie page to be
        # the referer. The site has a download limit of 20 subtitles per day. 
        # Currently, we're not trying to bypass this limit.
        return Utils.DownloadSubAsBytesIO(
                                          ADDIC7ED_PAGES.DOMAIN, 
                                          version_sub_stage.version_code,
                                          referer)