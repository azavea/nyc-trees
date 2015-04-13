# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

_perceptions_of_tree_health = """
<a href="/training/pure/tree_data/#perceptions-of-tree-health"
   target="_blank">Perceptions of Tree Health.</a>
"""
_mapping_tree_away_from_the_curb = """
<a href="/training/pure/the_mapping_method/#mapping-trees-away-from-the-curb"
   target="_blank">Mapping Trees Away From the Curb.</a>
"""

_what_if_there_arent_any_trees = """
<a href="/training/pure/the_mapping_method/#what-if-there-arent-any-trees"
   target="_blank">What If There Aren’t Any Trees?</a>
"""

_tree_stump_size = """
<a href="/training/pure/tree_data/#tree-stump-size"
   target="_blank">Tree Stump Size.</a>
"""

_tree_trunk_size = """
<a href="/training/pure/tree_data/#tree-trunk-size"
   target="_blank">Tree Trunk Size.</a>
"""

_mapping_to_the_end_point = """
<a href="/training/pure/the_mapping_method/#mapping-to-the-end-point"
   target="_blank">Mapping to the End Point.</a>
"""

_orientation = """
<a href="/training/pure/getting_started/#orientation"
   target="_blank">Orientation.</a>
"""


class QuizStrings(object):

    ##############################################################
    # QUESTION 1                                                 #
    ##############################################################

    q1_text = """
    Which of the following are signs of a tree in GOOD HEALTH.
    Select all that apply.
    """
    q1_c1 = "Dense canopy of leaves."
    q1_c2 = "Most leaves have the same color."
    q1_c3 = "Little or no damage to the tree bark."
    q1_c4 = "Branches without leaves."

    q1_correct_markup = """
    Correct: A dense canopy of leaves, most leaves having the same color,
    and little or no damage to the tree bark are all signs of good health.
    See: %s
    """ % _perceptions_of_tree_health

    q1_incorrect_markup = """
    Incorrect:  Review %s
    """ % _perceptions_of_tree_health

    ##############################################################
    # QUESTION 2                                                 #
    ##############################################################

    q2_text = """
    How do you map a street tree that is offset from the curb
    in an alternating pattern? Select all that apply.
    """

    q2_c1 = "Find the tree center and record the distance."
    q2_c2 = "Log the tree as offset."
    q2_c3 = "Map both trees near and far from the curb on the same block."

    q2_correct_markup = """
    Correct: Find the tree center, record the distance, log it as offset.
    Be sure to map trees near and far from the curb on the same block.
    See: %s
    """ % _mapping_tree_away_from_the_curb

    q2_incorrect_markup = """
    Incorrect.  Review %s
    """ % _mapping_tree_away_from_the_curb

    ##############################################################
    # QUESTION 3                                                 #
    ##############################################################

    q3_text = "Should a street block without trees be recorded?"

    q3_c1 = "Yes"
    q3_c2 = "No"

    q3_correct_markup = """
    Correct: Knowing that blocks do not have trees is
    still valuable information.
    See: %s
    """ % _what_if_there_arent_any_trees

    q3_incorrect_markup = """
    Incorrect. Review %s
    """ % _what_if_there_arent_any_trees

    ##############################################################
    # QUESTION 4                                                 #
    ##############################################################

    q4_text = "What is the diameter of a tree stump?"

    q4_c1 = "The distance from the center of the tree to the bark."
    q4_c2 = "Half the distance around the trunk of the tree."
    q4_c3 = "The distance around the trunk of the tree."
    q4_c4 = """
    The straight line starting from the bark,
    passing through the center of the stump to other side of the bark.
    """

    q4_correct_markup = """
    Correct: You may also think about the diameter of the tree stump
    as the longest line which goes across the tree stump. See: %s
    """ % _tree_stump_size

    q4_incorrect_markup = """
    Incorrect. Review %s
    """ % _tree_stump_size

    ##############################################################
    # QUESTION 5                                                 #
    ##############################################################

    q5_text = "Where do you measure the circumference of the tree?"

    q5_c1 = "2.5 feet (30 inches)"
    q5_c2 = "3.5 feet (42 inches)"
    q5_c3 = "4.5 feet (54 inches)"
    q5_c4 = "5.5 feet (66 inches)"

    q5_correct_markup = """
    Correct: Measure of the circumference of the tree
    4.5 feet (54 inches) off the ground. See: %s
    """ % _tree_trunk_size

    q5_incorrect_markup = """
    Incorrect. Review %s
    """ % _tree_trunk_size

    ##############################################################
    # QUESTION 6                                                 #
    ##############################################################

    q6_text = """
    Do you need to map from the last tree on
    the block to the end point of the block?
    """
    q6_c1 = "Yes"
    q6_c2 = "No"

    q6_correct_markup = """
    Correct: If you don’t measure to the end, you can’t submit the block edge.
    See: %s
    """ % _mapping_to_the_end_point

    q6_incorrect_markup = """
    Incorrect. %s
    """ % _mapping_to_the_end_point

    ##############################################################
    # QUESTION 7                                                 #
    ##############################################################

    q7_text = "How will you know which block to map at a mapping event?"

    q7_c1 = """
    A Group leader or Parks Event Staff person will assign you a block.
    """
    q7_c2 = "You can pick any block at random."
    q7_c3 = "You can pick a block on the website before the event."

    q7_correct_markup = """
    Correct: A Group leader or Parks Event Staff
    person assigns blocks at events. See: %s
    """ % _orientation

    q7_incorrect_markup = """
    Incorrect. Review %s
    """ % _orientation
