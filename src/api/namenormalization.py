""" 
This module implements the name normalization process as described in SubiT's
specs.

Currently, we're using the normalization both for normalizing the movie title
and episode names for serieses.
"""

def normalize_name(name):
    """
    Normalizes the name according to our specification. Performs all the 4
    steps of normalization, and return a list of them. 

    Note that a normalization step will be inserted to the output list only if
    it returned string different than the one it was given.

    >>> print normalize_name(r"The Godfather: Part II")
    ['The Godfather: Part II', 'the_godfather_part_ii']
    >>> print normalize_name(r"Schindler's List")
    ['Schindler's List', 'schindler_s_list']
    >>> print normalize_name(r"Am?lie")
    ['Am?lie', 'am_lie']
    >>> print normalize_name(r"The Godfather: Part 2")
    ['The Godfather: Part 2', 'the_godfather_part_2', 'the_godfather_part_ii']
    >>> print normalize_name(r"The Third Man")
    ['The Third Man', 'the_third_man']
    >>> print normalize_name(r"The 3rd Man")
    ['The 3rd Man', 'the_3rd_man', 'the_third_man']
    """
    pass

def normalize_name_1st_step(name):
    """ 
    The first step: 
        Simply return the name as-is.

    >>> print normalize_name_1st_step(r"The Godfather: Part II")
    The Godfather: Part II
    >>> print normalize_name_1st_step(r"Schindler's List")
    Schindler's List
    """
    pass

def normalize_name_2nd_step(name):
    """ 
    The second step:
        1. Apply lower() on the name.
        2. Replace any non-alphanumeric (including space) with underscore
        3. Replace any continous underscore with a single one

    >>> print normalize_name_2nd_step(r"The Godfather: Part II")
    the_godfather_part_ii
    >>> print normalize_name_2nd_step(r"Schindler's List")
    schindler_s_list
    >>> print normalize_name_2nd_step(r"Am?lie")
    am_lie
    >>> print normalize_name_2nd_step(r"The Godfather: Part 2")
    the_godfather_part_2
    >>> print normalize_name_2nd_step(r"The Third Man")
    the_third_man
    """
    pass

def normalize_name_3rd_step(name):
    """
    The third step: 
        Convert each Arabic formatted number that is located either at the 
        start or the end of the normalized name, or is surrounded with two 
        underscores to a lower case Latin one (22 becomes xxii).

    >>> print normalize_name_3rd_step(r"the_godfather_part_2")
    the_godfather_part_ii
    """
    pass

def normalize_name_4th_step(name):
    """
    The fourth step:
        Convert each Ordinal number to its string alphabet equivalent (1st 
        becomes first).

    >>> print normalize_name_3rd_step(r"the_third_man")
    the_third_man
    >>> print normalize_name_3rd_step(r"the_3rd_man")
    the_third_man
    """
    pass