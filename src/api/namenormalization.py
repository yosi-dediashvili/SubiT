""" 
This module implements the name normalization process as described in SubiT's
specs.

Currently, we're using the normalization both for normalizing the movie title
and episode names for serieses.
"""


__all__ = [
    'normalize_name', 
    'normalize_name_1st_step', 
    'normalize_name_2nd_step',
    'normalize_name_3rd_step',
    'normalize_name_4th_step'
]


import logging
logger = logging.getLogger("subit.api.namenormalization")


def normalize_name(name):
    """
    Normalizes the name according to our specification. Performs all the 4
    steps of normalization, and return a list of them. 

    Note that a normalization step will be inserted to the output list only if
    it returned string different than the one it was given.

    >>> print normalize_name(r"The Godfather: Part II")
    ['The Godfather: Part II', 'the_godfather_part_ii']
    >>> print normalize_name(r"Schindler's List")
    ["Schindler's List", 'schindler_s_list']
    >>> print normalize_name(r"Am?lie")
    ['Am?lie', 'am_lie']
    >>> print normalize_name(r"The Godfather: Part 2")
    ['The Godfather: Part 2', 'the_godfather_part_2', 'the_godfather_part_ii']
    >>> print normalize_name(r"The Third Man")
    ['The Third Man', 'the_third_man']
    >>> print normalize_name(r"The 3rd Man")
    ['The 3rd Man', 'the_3rd_man', 'the_third_man']
    """
    
    logger.debug("Received a name for normalization: %s" % name)

    normalization_steps = [
        normalize_name_1st_step,
        normalize_name_2nd_step,
        normalize_name_3rd_step,
        normalize_name_4th_step]

    normalized_names = [name]
    for normalization_step in normalization_steps:
        previous_name = normalized_names[-1]
        current_name = normalization_step(previous_name)
        if current_name != previous_name:
            normalized_names.append(current_name)

    logger.debug("Normalization result is: %s" % normalized_names)
    return normalized_names

def normalize_name_1st_step(name):
    """ 
    The first step: 
        Simply return the name as-is.

    >>> print normalize_name_1st_step(r"The Godfather: Part II")
    The Godfather: Part II
    >>> print normalize_name_1st_step(r"Schindler's List")
    Schindler's List
    """
    logger.debug("1st normalization step received: %s" % name)
    return name

def normalize_name_2nd_step(name):
    """ 
    The second step:
        1. Apply lower() on the name
        2. Replace any non-alphanumeric (including space) with underscore
        3. Replace any continous underscore with a single one
        4. Remove any leading/trailing underscores

    >>> print normalize_name_2nd_step(r"The Godfather: Part II")
    the_godfather_part_ii
    >>> print normalize_name_2nd_step(r"Schindler's List")
    schindler_s_list
    >>> print normalize_name_2nd_step(r"Am?lie")
    am_lie
    >>> print normalize_name_2nd_step(r"The Godfather: Part 2")
    the_godfather_part_2
    >>> print normalize_name_2nd_step(r" The Third Man  ")
    the_third_man
    """
    logger.debug("2nd normalization step received: %s" % name)
    import re
    name = name.lower()
    name = re.sub("[^A-Za-z0-9]", "_", name)
    name = re.sub("(_){2,}", "_", name)
    name = name.strip("_")
    logger.debug("2nd normalization step returns: %s" % name)
    return name


def normalize_name_3rd_step(name):
    """
    The third step: 
        Convert each Arabic formatted number that is located either at the start 
        or the end of the normalized name (and is followed/preceded by 
        underscore), or is surrounded with two underscores to a lower case Latin 
        one (22 becomes xxii).

    >>> print normalize_name_3rd_step(r"the_godfather_part_2")
    the_godfather_part_ii
    >>> print normalize_name_3rd_step(r"the_10_o_clock_people")
    the_x_o_clock_people
    >>> print normalize_name_3rd_step(r"19")
    xix
    >>> print normalize_name_3rd_step(r"50_first_dates")
    l_first_dates
    """
    logger.debug("3rd normalization step received: %s" % name)
    def _arabic_to_latin(arabic_number):
        LATIN_MAPPING = [('cd', 4 * 'c'),
                         ('xl', 4 * 'x'),
                         ('iv', 4 * 'i'),
                         ('d', 5 * 'c'),
                         ('l', 5 * 'x'),
                         ('v', 5 * 'i'),
                         ('cm', 9 * 'c'),
                         ('xc', 9 * 'x'),
                         ('ix', 9 * 'i')]

        LATIN_BIG_NUMS = [('m', 1000), 
                          ('c', 100), 
                          ('x', 10), 
                          ('i', 1)]
        latin_number = ''

        for (character, word) in LATIN_BIG_NUMS:
            latin_number += (arabic_number / word) * character
            arabic_number %= word

        for (short_ver, long_ver) in reversed(LATIN_MAPPING):
            latin_number = latin_number.replace(long_ver,short_ver)

        return latin_number

    def _replace_group(match):
        the_string = match.group(0)
        the_number = re.findall("\d+", the_string)[0]
        return re.sub("\d+", _arabic_to_latin(int(the_number)), the_string)
    import re
    # Replace standalone number
    name = re.sub("^(\d+)$", _replace_group, name)
    # Replace at the start of the string
    name = re.sub("^(\d+)_", _replace_group, name)
    # Replace at the end of the string
    name = re.sub("_(\d+)$", _replace_group, name)
    # Replace between underscores
    name = re.sub("_(\d+)_", _replace_group, name)
    logger.debug("3rd normalization step returns: %s" % name)
    return name

def normalize_name_4th_step(name):
    """
    The fourth step:
        Convert each Ordinal number to its string alphabet equivalent (1st 
        becomes first). We'll perform the operation up to the number 20 (Past 
        that it gets to complicated to guess how it will be represented).

    >>> print normalize_name_4th_step(r"the_third_man")
    the_third_man
    >>> print normalize_name_4th_step(r"the_3rd_man")
    the_third_man
    >>> print normalize_name_4th_step(r"1st_kind")
    first_kind
    >>> print normalize_name_4th_step(r"i_am_4th")
    i_am_fourth
    >>> print normalize_name_4th_step(r"15th")
    fifteenth
    >>> print normalize_name_4th_step(r"22th_hospital_street")
    22th_hospital_street
    """
    logger.debug("4th normalization step received: %s" % name)
    import inflect
    inflect_engine = inflect.engine()
    ordinals = map(lambda i: inflect_engine.ordinal(i), range(21))
    # As a regular expression
    ordinals_re = "(%s)" % "|".join(ordinals)

    def _replace_group(match):
        the_string  = match.group(0)
        the_ordinal = re.findall(ordinals_re, the_string)[0]
        return re.sub(ordinals_re, 
                      inflect_engine.number_to_words(the_ordinal), 
                      the_string)
    import re
    # Replace standalone ordinal
    name = re.sub("^%s$" % ordinals_re, _replace_group, name)
    # Replace at the start of the string
    name = re.sub("^%s_" % ordinals_re, _replace_group, name)
    # Replace at the end of the string
    name = re.sub("_%s$" % ordinals_re, _replace_group, name)
    # Replace between underscores
    name = re.sub("_%s_" % ordinals_re, _replace_group, name)
    logger.debug("4th normalization step returns: %s" % name)
    return name