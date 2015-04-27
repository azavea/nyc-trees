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

_evidence_of_stewardship = """
<a href="/training/pure/tree_surroundings/#evidence-of-stewardship"
   target="_blank">Evidence of Stewardship.</a>
"""

_what_if_im_not_sure = """
<a href="/training/pure/tree_data/#what-if-im-not-sure"
   target="_blank">What if I'm not sure?</a>
"""


class QuizStrings(object):

    ##############################################################
    # QUESTION 1                                                 #
    ##############################################################

    q1_text = """
    Which of the following are signs of a tree in GOOD HEALTH.
    <strong>Select all that apply.</strong>
    """
    q1_c1 = "Dense canopy of leaves"
    q1_c2 = "Most leaves have the same color"
    q1_c3 = "Little or no damage to the tree bark"
    q1_c4 = "Branches without leaves"

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
    in an alternating pattern? <strong>Select all that apply.</strong>
    <img src="/static/img/training/Stagger-Offset/stagger-offset.png"/>
    """

    q2_c1 = """
    Find the approximate tree center and
    record the distance from the previous tree
    """
    q2_c2 = "Log the tree as offset"
    q2_c3 = "Map both trees near and far from the curb"

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

    q4_text = """
    What is the diameter of a tree stump?
    <img src="/static/img/training/Stump/stump.png"/>
    """

    q4_c1 = "The distance from the center of the tree to the bark"
    q4_c2 = "Half the distance around the trunk of the tree"
    q4_c3 = "The distance around the trunk of the tree"
    q4_c4 = """
    The straight line starting from the bark,
    passing through the center of the stump to other side of the bark
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

    ##############################################################
    # QUESTION 8                                                 #
    ##############################################################

    q8_text = """
    <img src="/static/img/training/Poor-health-one/poor-health-one.png"/>
    One reason we can tell this tree is in poor health is:
    """

    q8_c1 = "The branches are not broken."
    q8_c2 = "It is short."
    q8_c3 = "The canopy is very sparse."

    q8_correct_markup = """
    Correct: Leaves with brown spots and holes, broken branches,
    and significant damage to the trunk and bark are signs of a
    tree in poor health. See: %s
    """ % _perceptions_of_tree_health

    q8_incorrect_markup = """
    Incorrect. Review %s
    """ % _perceptions_of_tree_health

    ##############################################################
    # QUESTION 9                                                 #
    ##############################################################

    q9_text = "Which Tree Steward signs should be counted?"

    q9_c1 = "Curb your dog signs"
    q9_c2 = "Parking signs"
    q9_c3 = "Signs stapled to the tree"
    q9_c4 = "Business flyers"

    q9_correct_markup = """
    Correct: Signs that explain the care or importance of street trees
    are evidence of Stewardship. Signs placed by a business or the city
    and signs attached directed onto the tree are not. See: %s
    """ % _evidence_of_stewardship

    q9_incorrect_markup = """
    Incorrect. Review %s
    """ % _evidence_of_stewardship

    ##############################################################
    # QUESTION 10                                                 #
    ##############################################################

    q10_text = """
    What do you do when you are uncertain of the tree species you have chosen?
    """

    q10_c1 = "Take your best guess."
    q10_c2 = """
    Take your best guess and select “No”
    to indicate you are not confident in your answer.
    """
    q10_c3 = """
    Take your best guess and select “Yes”
    to indicate you are confident in your answer.
    """

    q10_correct_markup = """
    Correct: If you are confident you can select Yes when you ID the tree.
    However, when you have doubt in your choice, it is important and perfectly
    acceptable to select Maybe or even No if you are really unsure.
    See: %s
    """ % _what_if_im_not_sure

    q10_incorrect_markup = """
    Incorrect. Review %s
    """ % _what_if_im_not_sure
