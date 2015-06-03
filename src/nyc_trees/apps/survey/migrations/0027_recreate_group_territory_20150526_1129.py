# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import now


def forwards(apps, schema_editor):
    Territory = apps.get_model('survey', 'Territory')
    BlockfaceReservation = apps.get_model('survey', 'BlockfaceReservation')
    Blockface = apps.get_model('survey', 'Blockface')
    Group = apps.get_model('core', 'Group')

    possible_groups = Group.objects.filter(border__isnull=False)

    nyc_parks = Group.objects.filter(slug='nyc-parks')
    nyc_parks = nyc_parks[0] if nyc_parks else None

    reserved_ids = BlockfaceReservation.objects.values_list('blockface_id', flat=True)

    orphaned_blocks = Blockface.objects \
        .filter(is_available=False) \
        .filter(territory=None) \
        .filter(expert_required=False) \
        .exclude(id__in=reserved_ids)

    not_in_group_borders = set(orphaned_blocks.values_list('id', flat=True))

    def add_to_group(group, group_blocks):
        print("Found %s orphaned blocks to add to %s group" %
              (len(group_blocks), group.name))

        new_territory = [Territory(group=group, blockface=block)
                         for block in group_blocks]
        Territory.objects.bulk_create(new_territory)

        # Record the current time on the group so we can use that as a
        # cache buster when making tile requests for the territory table
        group.territory_updated_at = now()
        group.save()

    for group in possible_groups:
        group_blocks = orphaned_blocks.filter(geom__within=group.border)

        if group_blocks:
            add_to_group(group, group_blocks)

            not_in_group_borders = not_in_group_borders - {b.id for b in group_blocks}

    if not_in_group_borders and nyc_parks:
        add_to_group(nyc_parks, Blockface.objects.filter(id__in=not_in_group_borders))

    orphaned_blocks = Blockface.objects \
        .filter(is_available=False) \
        .filter(territory=None) \
        .exclude(id__in=reserved_ids)

    print("And there are %s orphaned blocks remaining" % len(orphaned_blocks))


def backwards():
    pass  # Do nothing


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0026_auto_20150514_1005'),
        ('core', '0031_auto_20150513_1536'),
    ]
    operations = [
        migrations.RunPython(code=forwards, reverse_code=backwards)
    ]
