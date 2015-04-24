# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from collections import OrderedDict

from django.db import models

from apps.core.models import User, Group

from libs.mixins import NycModel


class AchievementDefinition(object):
    """A class representing an achievment definition
    name - string - title of the achievement
    description - requirements (after achievement)
    description_future - requirements (before achievement)
    badge - path for a static image file
    achieved - a function which takes a user and returns a boolean
    """
    def __init__(self, name, description, description_achieved, badge,
                 achieved, sponsor=None, reward=None):
        assert isinstance(name, basestring)
        assert isinstance(description, basestring)
        assert isinstance(description_achieved, basestring)
        assert isinstance(badge, basestring)
        assert callable(achieved)
        assert sponsor is None or isinstance(sponsor, basestring)
        assert reward is None or isinstance(reward, basestring)

        self.name = name
        self.description = description
        self.description_achieved = description_achieved
        self.badge = badge
        self.achieved = achieved
        self.sponsor = sponsor
        self.reward = reward

    ONLINE_TRAINING = 0
    FOLLOW_GROUPS = 1
    TRAINING_EVENT = 2
    MAPPING_EVENT = 3
    MAP_50 = 4
    MAP_100 = 5
    MAP_200 = 6
    MAP_400 = 7
    MAP_1000 = 8
    MAP_MOST = 9


achievements = OrderedDict([
    (AchievementDefinition.FOLLOW_GROUPS, AchievementDefinition(
        name='In Pursuit of Mappiness',
        description='Follow 5 Groups',
        description_achieved='Followed 5 Groups',
        badge='img/badges/ic_badge_follow.png',
        achieved=lambda user: Follow.objects.filter(user=user).count() >= 5
    )),
    (AchievementDefinition.ONLINE_TRAINING, AchievementDefinition(
        name='Ready, Set, Roll',
        description='Finish Online Training',
        description_achieved='Finished Online Training',
        badge='img/badges/ic_badge_online_training.png',
        achieved=lambda user: user.online_training_complete
    )),
    (AchievementDefinition.TRAINING_EVENT, AchievementDefinition(
        name='Treerifically Trained',
        description='Attend a Training Event',
        description_achieved='Attended a Training Event',
        badge='img/badges/ic_badge_training_event.png',
        achieved=lambda user: user.field_training_complete,
        reward='Receive a Census Gear Pack with a measuring tape, '
        'Tree Species ID Guide, volun<b>treer</b> lanyard and badge, and a '
        'TreesCount safety vest!'
    )),
    (AchievementDefinition.MAPPING_EVENT, AchievementDefinition(
        name='Counter Cultured',
        description='Attend a Mapping Event',
        description_achieved='Attended a Mapping Event',
        badge='img/badges/ic_badge_mapping_event.png',
        achieved=lambda user: user.attended_at_least_two_events()
    )),
    (AchievementDefinition.MAP_50, AchievementDefinition(
        name='Rolling Revolutionary',
        description='Map 50 Block Edges',
        description_achieved='Mapped 50 Block Edges',
        badge='img/badges/ic_badge_map_50.png',
        achieved=lambda user: user.blocks_mapped_count >= 50,
        sponsor='Various sponsors',
        reward='The first 250 volun<b>treers</b> to reach this level will '
        'receive tickets to a NY Liberty Game! All volun<b>treers</b> will '
        'be entered into lotteries to win a personal Tree Care Workshop, '
        'Knicks gift bag and other great prizes, while supplies last.'
    )),
    (AchievementDefinition.MAP_100, AchievementDefinition(
        name='Mapping Machine',
        description='Map 100 Block Edges',
        description_achieved='Mapped 100 Block Edges',
        badge='img/badges/ic_badge_map_100.png',
        achieved=lambda user: user.blocks_mapped_count >= 100,
        sponsor='Sponsored by Whole Foods Market',
        reward='Tree Care Kit that includes gloves, weeder, cultivator, '
        'trowel, a collapsible bucket and other helpful tools.'
    )),
    (AchievementDefinition.MAP_200, AchievementDefinition(
        name='Sprout Mapper',
        description='Map 200 Block Edges',
        description_achieved='Mapped 200 Block Edges',
        badge='img/badges/ic_badge_map_200.png',
        achieved=lambda user: user.blocks_mapped_count >= 200,
        sponsor='Sponsored by Whole Foods Market',
        reward='TreesCount! Tote &amp; Tree Care Kit that includes a limited '
        'edition TreesCount! t-shirt, gloves, weeder, cultivator, trowel, '
        'a collapsible buck and other helpful tools.'
    )),
    (AchievementDefinition.MAP_400, AchievementDefinition(
        name='Seedling Mapper',
        description='Map 400 Block Edges',
        description_achieved='Mapped 400 Block Edges',
        badge='img/badges/ic_badge_map_400.png',
        achieved=lambda user: user.blocks_mapped_count >= 400,
        reward='Picnic Basket for Two'
    )),
    (AchievementDefinition.MAP_1000, AchievementDefinition(
        name='Sapling Mapper',
        description='Map 1000 Block Edges',
        description_achieved='Mapped 1000 Block Edges',
        badge='img/badges/ic_badge_map_1000.png',
        achieved=lambda user: user.blocks_mapped_count >= 1000,
        reward='Details coming soon!'
    )),
    (AchievementDefinition.MAP_MOST, AchievementDefinition(
        name='Mayoral Mapper',
        description='Map the Most Block Edges in NYC',
        description_achieved='Mapped the Most Block Edges in NYC',
        badge='img/badges/ic_badge_top_mapper.png',
        achieved=lambda user: False,  # doesn't need to be live updated
        reward='The volun<b>treer</b> that maps the most trees will earn a '
        'pair of VIP Tickets to the Global Citizen Festival in Central Park '
        'on September 26, 2015.'
    )),
])


achievement_choices = [(key, achievement_def.name)
                       for key, achievement_def in achievements.iteritems()]


def update_achievements(user):
    achieved_ids = set([a.achievement_id
                        for a in user.achievement_set.all()])

    for id, definition in achievements.iteritems():
        if id not in achieved_ids and definition.achieved(user):
            a = Achievement(user=user, achievement_id=id)
            a.save()


class Follow(NycModel, models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.group)


class TrustedMapper(NycModel, models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    is_approved = models.NullBooleanField()

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.group)

    class Meta:
        unique_together = ("user", "group")


class TrainingResult(NycModel, models.Model):
    user = models.ForeignKey(User)
    module_name = models.CharField(max_length=255)
    score = models.IntegerField(null=True)


class Achievement(NycModel, models.Model):
    user = models.ForeignKey(User)
    achievement_id = models.IntegerField(choices=achievement_choices)

    class Meta:
        unique_together = ("user", "achievement_id")
