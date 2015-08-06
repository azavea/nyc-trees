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
        # NOTE: using hard-coded URL here because it's too early for reverse()
        description_achieved="""Finished Online Training
            <div><a class="h6 color--secondary" href="/event/">
                Register for an event today</a>!</div>""",
        badge='img/badges/ic_badge_online_training.png',
        achieved=lambda user: user.online_training_complete
    )),
    (AchievementDefinition.TRAINING_EVENT, AchievementDefinition(
        name='Treerifically Trained',
        description='Attend a Training Event',
        # NOTE: using hard-coded URLs here because it's too early for reverse()
        description_achieved='Attended a Training Event',
        badge='img/badges/ic_badge_training_event.png',
        achieved=lambda user: user.field_training_complete,
        reward="""Join us at a training event, and you will receive
            a Census Gear Pack with your very own
            portable Tree Species ID Guide, so you can
            identify every tree in NYC! You'll also get all the
            tools you need to keep mapping all summer: a
            TreesCount! performance baseball cap,
            safety vest, Metrocard holder, measuring tape
            and volun<b>treer</b> badge to check out equipment
            at future events or from loaning hubs."""
    )),
    (AchievementDefinition.MAPPING_EVENT, AchievementDefinition(
        name='Counter Cultured',
        description='Attend a Mapping Event',
        # NOTE: using hard-coded URLs here because it's too early for reverse()
        description_achieved="""Attended a Mapping Event
            <div><a class="h6 color--secondary" href="/blockedge/reserve/">
                Reserve blocks today</a> to map on your own!</div>
            <div>
                Need a wheel? Visit one of our nearby
                <a class="h6 color--secondary"
        href="http://www.nycgovparks.org/trees/treescount/independent-mapping">
                    loaning hubs</a>
                or check one out at your next NYC Parks
                <a class="h6 color--secondary" href="/event/">
                    mapping event</a>!</div>""",
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
        reward="""The first 250 volun<b>treer</b>s to reach this level by
            August 28, 2015 will receive tickets to a NY
            Liberty Game! How many 1, 2, tree pointers
            will you see?"""
    )),
    (AchievementDefinition.MAP_100, AchievementDefinition(
        name='Mapping Machine',
        description='Map 100 Block Edges',
        description_achieved='Mapped 100 Block Edges',
        badge='img/badges/ic_badge_map_100.png',
        achieved=lambda user: user.blocks_mapped_count >= 100,
        sponsor='Sponsored by Whole Foods Market',
        reward="""When you reach this level, you'll receive a Tree
            Care Kit, which includes high quality gloves,
            weeder, cultivator, trowel, a collapsible
            watering bucket and more! With this kit, you'll
            have everything you need to take care of your
            newly counted trees!"""
    )),
    (AchievementDefinition.MAP_200, AchievementDefinition(
        name='Sprout Mapper',
        description='Map 200 Block Edges',
        description_achieved='Mapped 200 Block Edges',
        badge='img/badges/ic_badge_map_200.png',
        achieved=lambda user: user.blocks_mapped_count >= 200,
        sponsor='Sponsored by Whole Foods Market',
        reward="""Show your NYC pride and travel the city in style
            with your new Tree-rrific tote and limited
            edition TreesCount! t-shirt."""
    )),
    (AchievementDefinition.MAP_400, AchievementDefinition(
        name='Seedling Mapper',
        description='Map 400 Block Edges',
        description_achieved='Mapped 400 Block Edges',
        badge='img/badges/ic_badge_map_400.png',
        achieved=lambda user: user.blocks_mapped_count >= 400,
        reward="""Replace those worn-out shoes with a brand
            new pair of Timberland boots! The first 5
            volun<b>treer</b>s to reach this level will receive a gift
            card for some new kicks.  A special TreesCount!
            picnic basket for two will be awarded to other
            Seedling Mappers."""
    )),
    (AchievementDefinition.MAP_1000, AchievementDefinition(
        name='Sapling Mapper',
        description='Map 1000 Block Edges',
        description_achieved='Mapped 1000 Block Edges',
        badge='img/badges/ic_badge_map_1000.png',
        achieved=lambda user: user.blocks_mapped_count >= 1000,
        reward="""Celebrate your civic contribution at the Global
            Citizen Festival in Central Park on September
            26, 2015! <i>Limited number of general admission
            tickets available.</i>"""
    )),
    (AchievementDefinition.MAP_MOST, AchievementDefinition(
        name='Mayoral Mapper',
        description='Map the Most Block Edges in NYC',
        description_achieved='Mapped the Most Block Edges in NYC',
        badge='img/badges/ic_badge_top_mapper.png',
        achieved=lambda user: False,  # doesn't need to be live updated
        reward="""Map the most blocks in the city by September
            22nd and get a free pair of tickets to check out
            Pearl Jam, Beyonce, Ed Sheeran and Coldplay
            from the <b>VIP</b> seats at the Global Citizen Festival
            in Central Park on September 26, 2015."""
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
    user = models.ForeignKey(User, help_text='ID of user following group')
    group = models.ForeignKey(Group, help_text='ID of group being followed')

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.group)


class TrustedMapper(NycModel, models.Model):
    user = models.ForeignKey(
        User,
        help_text="ID of user requesting mapping permission")
    group = models.ForeignKey(
        Group,
        help_text='ID of group granting mapping permission')
    is_approved = models.NullBooleanField(
        help_text='Has mapping permission been granted?')

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.group)

    class Meta:
        unique_together = ("user", "group")


class TrainingResult(NycModel, models.Model):
    user = models.ForeignKey(
        User,
        help_text='ID of user answering quiz questions')
    module_name = models.CharField(
        max_length=255,
        help_text='Name of quiz')
    score = models.IntegerField(
        null=True,
        help_text='Number of questions answered correctly')


def achievement_help_text():
    help_items = ['%s - %s - %s' % (i, adef.name, adef.description)
                  for i, adef in achievements.iteritems()]
    help_items.sort()
    return '<br/>'.join(help_items)


class Achievement(NycModel, models.Model):
    user = models.ForeignKey(
        User,
        help_text='ID of user who achieved the achievement')
    achievement_id = models.IntegerField(
        choices=achievement_choices,
        help_text=achievement_help_text)

    class Meta:
        unique_together = ("user", "achievement_id")
