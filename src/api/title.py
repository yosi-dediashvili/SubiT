""" 
Implementation of the Title classes. This package is not responsible for 
resolving the Title from arbitrary string input and such. It simply the 
implementation of Titles.

Users of this package will implement the methods for extracting the required 
info for the Title.
"""

__all__ = ['MovieTitle', 'SeriesTitle']

import logging
logger = logging.getLogger("subit.api.title")
from abc import ABCMeta, abstractmethod

from exceptions import InvalidTitleName
from exceptions import InvalidSeasonNumber
from exceptions import InvalidEpisodeNumber


class Title(object):
    """ The base Title object. """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, name, year = 0, imdb_id = ""):
        """
        A Title is initialized with at least a name. And it cannot be an empty
        string.

        >>> MovieTitle("", 1991, "")
        Traceback (most recent call last):
            ...
        InvalidTitleName: Title's name cannot be empty.
        """
        if not name:
            raise InvalidTitleName("Title's name cannot be empty.")

        self.name       = name
        self.year       = year
        self.imdb_id    = imdb_id
        from namenormalization import normalize_name
        self.normalized_names = normalize_name(self.name)

    @property
    def normalized_names_set(self):
        return self._normalized_names_set

    @property
    def normalized_names(self):
        return self._normalized_names

    @normalized_names.setter
    def normalized_names(self, value):
        self._normalized_names = value
        self._normalized_names_set = set(self.normalized_names)

    def __eq__(self, other):
        """
        Base equality check for titles.

        >>> title_a = MovieTitle("The Matrix", 1999, "tt0133093")
        >>> title_b = MovieTitle("The Matrix", 0, "tt0133093")
        >>> title_a == title_b
        True
        >>> title_b = MovieTitle("The  Matrix", 0, "")
        >>> title_a == title_b
        True
        >>> title_b = MovieTitle("The Metrix", 0, "")
        >>> title_a == title_b
        False
        >>> title_a = MovieTitle("The Matrix", 0, "")
        >>> title_b = MovieTitle("The Matrix", 0, "")
        >>> title_a == title_b
        True
        """
        logger.debug("Checking Title equality: %s and %s" % (self, other))
        # When imdb_id is not empty, and equals.
        if self.imdb_id and self.imdb_id == other.imdb_id:
            return True
        # Year equals or empty in at least one.
        elif (not self.year or not other.year) or self.year == other.year:
            intersection = self.normalized_names_set.intersection(
                other.normalized_names_set)
            return bool(intersection)
        return False

    def __str__(self):
        return repr(self)

class MovieTitle(Title):
    """ Title object for movies. """
    def __init__(self, name, year = 0, imdb_id = ""):
        Title.__init__(self, name, year, imdb_id)
        logger.debug("Created MovieTitle instance: %s" % self)

    def __repr__(self):
        """
        >>> print MovieTitle("The Matrix", 1999, "tt0133093")
        <MovieTitle name='The Matrix', year=1999, imdb_id='tt0133093'>
        >>> print MovieTitle("The Matrix", 1999)
        <MovieTitle name='The Matrix', year=1999, imdb_id=''>
        >>> print MovieTitle("The Matrix")
        <MovieTitle name='The Matrix', year=0, imdb_id=''>
        """
        return (
            "<MovieTitle name='%(name)s', "
            "year=%(year)d, "
            "imdb_id='%(imdb_id)s'>"
            % self.__dict__)

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

        logger.debug("Created SeriesTitle instance: %s" % self)

    @property
    def episode_normalized_names_set(self):
        return self._episode_normalized_names_set

    @property
    def episode_normalized_names(self):
        return self._episode_normalized_names

    @episode_normalized_names.setter
    def episode_normalized_names(self, value):
        self._episode_normalized_names = value
        self._episode_normalized_names_set = set(self.episode_normalized_names)

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
        >>> title_a = SeriesTitle("Lost", 1, 2, "He's Our You")
        >>> title_b = SeriesTitle("Lost", 2, 4, "He_s_Our_You")
        >>> title_a == title_b
        False
        """
        if not Title.__eq__(self, other):
            return False

        logger.debug("Checking SeriesTitle equality: %s and %s" % (self, other))
        # First, make sure that their not empty.
        if (self.season_number and other.episode_number and 
            self.episode_number and other.episode_number):

            if (self.season_number == other.season_number and 
                self.episode_number == other.episode_number):
                return True
        # Only if we're lacking episode\season number, check the name.
        else:
            return bool(self.episode_normalized_names_set.intersection(
                other.episode_normalized_names_set))
        return False

    def __repr__(self):
        """
        >>> print SeriesTitle("Lost", 1, 3, "Tabula Rasa", 2004, "tt0411008")
        <SeriesTitle name='Lost', season_number=1, episode_number=3, \
        episode_name='Tabula Rasa', year=2004, imdb_id='tt0411008'>
        >>> print SeriesTitle("Lost", 1, 3, "Tabula Rasa", 2004)
        <SeriesTitle name='Lost', season_number=1, episode_number=3, \
        episode_name='Tabula Rasa', year=2004, imdb_id=''>
        >>> print SeriesTitle("Lost", 1, 3, "Tabula Rasa")
        <SeriesTitle name='Lost', season_number=1, episode_number=3, \
        episode_name='Tabula Rasa', year=0, imdb_id=''>
        >>> print SeriesTitle("Lost", 1, 3)
        <SeriesTitle name='Lost', season_number=1, episode_number=3, \
        episode_name='', year=0, imdb_id=''>
        """
        return (
            "<SeriesTitle name='%(name)s', "
            "season_number=%(season_number)d, "
            "episode_number=%(episode_number)d, "
            "episode_name='%(episode_name)s', "
            "year=%(year)d, "
            "imdb_id='%(imdb_id)s'>" 
            % self.__dict__)
                