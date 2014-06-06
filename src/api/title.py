from exceptions import InvalidTitleName
from exceptions import InvalidSeasonNumber
from exceptions import InvalidEpisodeNumber

class Title(object):
    """ The base Title object. """
    def __init__(self, name, year = 0, imdb_id = ""):
        """
        A Title is initialized with at least a name. And it cannot be an empty
        string.
        """
        if not name:
            raise InvalidTitleName("Title's name cannot be empty.")

        self.name       = name
        self.year       = year
        self.imdb_id    = imdb_id
        from namenormalization import normalize_name
        self.normalized_names = normalize_name(self.name)
        self.normalized_names_set = set(self.normalized_names)

    def __eq__(self, other):
        """
        Base equality check for titles.

        >>> title_a = Title("The Matrix", 1999, "tt0133093")
        >>> title_b = Title("The Matrix", 0, "tt0133093")
        >>> title_a == title_b
        True
        >>> title_b = Title("The  Matrix", 0, "")
        >>> title_a == title_b
        True
        >>> title_b = Title("The Metrix", 0, "")
        >>> title_a == title_b
        False
        >>> title_a = Title("The Matrix", 0, "")
        >>> title_b = Title("The Matrix", 0, "")
        >>> title_a == title_b
        True
        """
        # When imdb_id is not empty, and equals.
        if self.imdb_id and self.imdb_id == other.imdb_id:
            return True
        # Year equals or empty in at least one.
        elif (not self.year or not other.year) or self.year == other.year:
            intersection = self.normalized_names_set.intersection(
                other.normalized_names_set)
            return bool(intersection)
        return False
        
class MovieTitle(Title):
    """ Title object for movies. """
    def __init__(self, name, year = 0, imdb_id = ""):
        Title.__init__(self, name, year, imdb_id)

class SeriesTitle(Title):
    """ 
    Title object for series. A series instance defines a single episode in
    the series.
    """
    def __init__(self, name, season_number = 0, episode_number = 0, 
                 episode_name = "", year = 0, imdb_id = ""):
        """
        The Series title is initialized with at least a name and either (season 
        + episode numbers) or episode_name. 
        """
        Title.__init__(self, name, year, imdb_id)
        if not season_number and not episode_name:
            raise InvalidSeasonNumber(
                "season_number cannot be empty along with episode_name.")
        if not episode_number and not episode_name:
            raise InvalidEpisodeNumber(
                "episode_number cannot be empty along with episode_name.")

        self.episode_name   = episode_name
        self.season_number  = season_number
        self.episode_number = episode_number
        if episode_name:
            from namenormalization import normalize_name
            self.episode_normalized_names = normalize_name(self.episode_name)
        else:
            self.episode_normalized_names = []
        self.episode_normalized_names_set   = set(self.episode_normalized_names)

    def __eq__(self, other):
        """
        SeriesTitle equlity check.

        >>> SeriesTitle("Lost", 5, 3) == SeriesTitle("Lost", 5, 4)
        False
        >>> SeriesTitle("Losts", 5, 3) == SeriesTitle("Lost", 5, 3)
        False
        >>> SeriesTitle("Lost ", 6, 4) == SeriesTitle("Lost", 6, 4)
        True
        >>> title_a = SeriesTitle("Lost", episode_name = "He's Our You")
        >>> title_b = SeriesTitle("Lost", episode_name = "He_s_Our_You")
        >>> title_a == title_b
        True
        """
        if not Title.__eq__(self, other):
            return False

        # season and episode numbers cannot be empty/0.
        if (self.season_number == other.season_number) and (
            self.episode_number == other.episode_number):
            return True
        else:
            return bool(self.episode_normalized_names_set.intersection(
                other.episode_normalized_names_set))
        return False