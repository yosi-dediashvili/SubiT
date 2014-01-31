from SubProviders.ISubProvider import ISubProvider
from SubStages.QuerySubStage import QuerySubStage
from SubStages.VersionSubStage import VersionSubStage
from SubStages.MovieSubStage import MovieSubStage

import Utils
WriteDebug = Utils.WriteDebug

class SUBSCENE_LANGUAGES:
    HEBREW  = '22'
    ENGLISH = '23'

class SUBSCENE_PAGES:
    DOMAIN = 'www.subscene.com'
    SEARCH = '/subtitles/title?q=%s&l='

class SUBSCENE_CONSTS:
    TV_SERIES_SECTION = 'TV-Series'
    TV_SERIES_SEASON = 'Season'
    # Dictionary to convert from Subscene's season numbering (simple ordinal
    # strings) to the convenient coding.
    TV_SERIES_SEASONS = {
        'First'   : 'S01', 'Second' : 'S02', 'Third' : 'S03', 
        'Fourth'  : 'S04', 'Fifth'  : 'S05', 'Sixth' : 'S06', 
        'Seventh' : 'S07', 'Eighth' : 'S08', 'Ninth' : 'S09', 
        'Tenth'   : 'S10', 
        'Eleventh'    : 'S11', 'Twelfth'    : 'S12', 'Thirteenth' : 'S13', 
        'Fourteenth'  : 'S14', 'Fifteenth'  : 'S15', 'Sixteenth'  : 'S16', 
        'Seventeenth' : 'S17', 'Eighteenth' : 'S18', 'Nineteenth' : 'S19', 
        'Twentieth'   : 'S20'}


class SUBSCENE_REGEX:
    """
    The regex parser for Subscene's pages. The parser assumes that all the TABs
    i.e. "\t" chars was removed from the content.
    """
    # Extracs all the sections of the subtitles returned from SUBSCENE_PAGES-
    # .SEARCH. For example, a section will be given a type "tv-series", and 
    # under it will be several results. The result of this regex is two groups
    # for each result. A Type, and a string containing the html inside that 
    # section.
    SECTIONS_PARSER = \
        '\<h2 class\=\".*?\"\>(?P<Type>.*?)' \
        '\<\/h2\>(?P<Content>\<ul\>.*?\<\/ul\>)'

    # Parses the results located inside each section. For each match, the 
    # returned value is a MovieCode and a MovieName.
    MOVIES_PARSER = \
        '(?<=\<div class\=\"title\"\>\<a href\=\")(?P<MovieCode>.*?)' \
        '\"\>(?P<MovieName>.*?)\<\/a\>\<\/div\>'

    # Parses the results returned from entering a specific result from the
    # MOVIES_PARSER.
    VERSIONS_PARSER = \
        '(?<=\<td class=\"a1\"\>\<a href\=\")(?P<VersionCode>.*?)\"\>'  \
        '\<div class\=\"visited\"\>\<span.*?\<\/span\>\<span\>'         \
        '(?P<VersionSum>.*?) \<\/span\>\<\/div\>\<\/a\>'

    # Parses the url to the subtitle file in the version's page.
    SUBTITLE_URL_PARSER = \
        '(?<=\<div class\=\"download\"\>\<a href\=\")(.*?)(?=\" rel)'

    # Removes the year from a string. The year format is (YYYY).
    YEAR_REMOVER = '(.*?)\(\d{4}\)'


class ISubsceneProvider(ISubProvider):
    """
    Provider for www.subscene.com. The site does NOT provide an API.
    """
    PROVIDER_NAME = 'Base - www.subscene.com'
    PROVIDER_PNG  = 'icon-subprovider-subscene.png'
    SELECTED_LANGUAGE = None

    @classmethod
    def _get_cookie(cls, referer):
        """
        Retreive our generic cookie for Subscene. This cookie defines which
        subtitle's language will be returned to us.
        """
        return {"Cookie" :  "LanguageFilter=" + cls.SELECTED_LANGUAGE + "; "
                            "ShowSubtitleDetails=true; " + 
                            "ShowSubtitlePreview=false;",
                "Referer" : referer}

    @classmethod
    def _build_referer(cls, page):
        """
        Build a referer URL for Subscene. page should start with a single slash,
        i.e. "/".
        """
        return "http://" + SUBSCENE_PAGES.DOMAIN + page

    @classmethod
    def _my_perform_request(cls, page, remove_tabs = True):
        """
        Perform a simple request, but adds the cookies needed for Subscene. If
        remove_tabs is true, the function removes all the "\t"s in the returned
        content.
        """
        referer = cls._build_referer(page)
        cookie = cls._get_cookie(referer)
        content = Utils.PerformRequest(
            # Subscene's server will return 301 code (Redirection) when we 
            # request pages with the HOST set to www.subscene.com, so we 
            # replace it with simply subscene.com.
            SUBSCENE_PAGES.DOMAIN.replace('www.', ''), 
            page,
            '',
            Utils.HttpRequestTypes.GET,
            cookie)

        if remove_tabs:
            content = content.replace("\t", "")

        return content

    @classmethod
    def _extract_season_number(cls, movie_name):
        """
        Will try to locate the the sersies number string in the movie name and
        extract it. returning the movie name without it. And also, a represen-
        tation of the season number in the format of "SXX"
        """
        # The regex will return the season string. We'll remove it from the
        # movie_name.
        for season, code in SUBSCENE_CONSTS.TV_SERIES_SEASONS.iteritems():
            # Concatenate the "Season" to the number.
            season = ' '.join([season, SUBSCENE_CONSTS.TV_SERIES_SEASON])
            if season in movie_name:
                movie_name = movie_name.replace(season, code)

        return movie_name

    @classmethod
    def _remove_year(cls, movie_name):
        """ 
        Removes the year from the movie name. The year is located inside
        parentheses. Returns None on failure.
        """
        result = Utils.getregexresults(
            SUBSCENE_REGEX.YEAR_REMOVER, 
            movie_name, 
            False)
        if not result: 
            return None
        return result[0]

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findMovieSubStageList(cls, query_sub_stage):
        """
        Send a simple query to the site. The function will return a list 
        containing all the results that the query returned. If the site lists
        some results twice or more, they will be united.
        """
        query = query_sub_stage.query.replace(' ', '+')
        WriteDebug('Sending query for: %s' % query)

        # Prepare the parameters.
        page = SUBSCENE_PAGES.SEARCH % query
        query_data = cls._my_perform_request(page)
        
        # Extract the sections.
        sections = Utils.getregexresults(
            SUBSCENE_REGEX.SECTIONS_PARSER, 
            query_data, 
            False)

        # Subscene does not provide versions summary in the movie results, so
        # we place this default value.
        default_versum = 'Sub types are not supported in this provider'

        # The MovieSubStage the we created.
        movie_sub_stages = []

        def _add_movie(movie):
            """
            Adds a single movie to the list as a MovieSubStage. Removes the 
            season numbering and the year from the movie_name field.
            """
            movie_name = movie['MovieName']
            movie_code = movie['MovieCode']

            # Try to extract the season numbering (it might be a season result).
            movie_name = cls._extract_season_number(movie_name)
            # Remove the year.
            movie_name = cls._remove_year(movie_name)
            # And convert to global format.
            movie_name = Utils.FormatMovieName(movie_name, False)

            stage = MovieSubStage(
                cls.PROVIDER_NAME, 
                movie_name, 
                movie_code, 
                default_versum)

            # There might be duplication in the results.
            if stage not in movie_sub_stages:
                movie_sub_stages.append(stage)

        for type, content in sections:
            # Extract the movies from the content.
            movies = Utils.getregexresults(
                SUBSCENE_REGEX.MOVIES_PARSER, 
                content, 
                True)

            for movie in movies: _add_movie(movie)
            
        return movie_sub_stages

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def findVersionSubStageList(cls, movie_sub_stage):
        """
        Extracts all the versions under the given movie. 
        """

        query_data = cls._my_perform_request(movie_sub_stage.movie_code)
        
        # Extract the results.
        re_results = Utils.getregexresults(
            SUBSCENE_REGEX.VERSIONS_PARSER, query_data, True)

        # The VersionSubStages the we created.
        version_sub_stages = []

        # Convert each regex result to a VersionSubStage, and insert the result
        # to the list.
        for version in re_results:
            stage = VersionSubStage(
                cls.PROVIDER_NAME, 
                version['VersionSum'], 
                version['VersionCode'], 
                movie_sub_stage.movie_code)

            # There might be duplication in the results.
            if stage not in version_sub_stages:
                version_sub_stages.append(stage)

        return version_sub_stages

    @classmethod
    @ISubProvider.SubProviderMethodWrapper
    def getSubtitleContent(cls, version_sub_stage):
        """
        Retrieve the content of the subtitle download.
        """

        url = version_sub_stage.version_code
        subtitle_page = cls._my_perform_request(url)
        subtitle_url = Utils.getregexresults(
            SUBSCENE_REGEX.SUBTITLE_URL_PARSER, 
            subtitle_page)

        # If for some reason we failed.
        if not subtitle_url:
            WriteDebug("Failed getting the subtitle url in page: %s" % url)
            return None
        
        # regex results returned by Utils.getregexresults are returned as list.
        subtitle_url = subtitle_url[0]
        return Utils.DownloadSubAsBytesIO(
            SUBSCENE_PAGES.DOMAIN.replace('www.', ''), 
            subtitle_url,
            cls._build_referer(url))