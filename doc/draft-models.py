# This file is a draft of the Django models we will use in the
# application. The intention is to move them out of this file into the
# proper Django applications within the project

class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=30, default='', blank=True)
    last_name = models.CharField(
        max_length=30, default='', blank=True)
    online_training_complete = models.BooleanField(default=False)
    individual_mapper = models.BooleanField(default=False)
    requested_individual_mapping_at = models.DateTimeField(null=True)
    is_flagged = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_census_admin = models.BooleanField(default=False)
    is_ambassador = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default='', blank=True)
    contact_info = models.TextField(default='', blank=True)
    contact_email = models.EmailField(null=True)
    contact_url = models.URLField(null=True)
    # Deleting a user should not cascade delete the group of which
    # they are an admin. A new admin should be set before a user
    # delete is allowed.
    admin = models.ForeignKey(User, on_delete=models.PROTECT)
    image = models.ImageField(null=True)
    is_active = models.BooleanField(defaut=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Event(models.Model):
    # Once a group has events, we can't just delete the group, because
    # people could have registered to attend the group's events.
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    description = models.TextField(default='', blank=True)
    contact_email = models.EmailField(null=True)
    contact_info = models.TextField(default='', blank=True)
    begins_at =  models.DateTimeField()
    ends_at =  models.DateTimeField()
    location = models.PointField(srid=3857,
                                 db_column='the_geom_webmercator')
    max_attendees = models.IntegerField()
    includes_training = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    url_name = Models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Blockface(models.Model):
    geom = models.LineStringField(srid=3857,
                                  db_column='the_geom_webmercator')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Territory(models.Model):
    group = model.ForeignKey(Group)
    blockface = model.ForeignKey(Blockface)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Follow(models.Model):
    user = model.ForeignKey(User)
    group = models.ForeignKey(group)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TrustedMapper(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TrainingResult(models.Model):
    user = models.ForeignKey(User)
    module_name = models.CharField(max_length=255)
    score = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tree(models.Model):
    survey = models.ForeignKey(Survey)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Survey(models.Model):
    # We do not anticipate deleting a Blockface, but we definitely
    # should not allow it to be deleted if there is a related Survey
    blockface = model.ForeignKey(Blockface, on_delete=models.PROTECT)
    # We do not want to loose survey data by allowing the deletion of
    # a User object to automatically cascade and delete the Survey
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    teammate = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EventRegistration(models.Model):
    user = models.ForeignKey(User)
    # If users have registered for an event, we do not want to allow
    # the event to be deleted. If we do, the registration will
    # disappear from the User's profile page and they may show up to
    # an event on the day, not knowing it was canceled
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    did_attend = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AchievementDefinition(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default='', blank=True)
    badge_image = models.ImageField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Achievement(models.Model):
    user = model.ForeignKey(User)
    achievement_definition = model.ForeignKey(AchievementDefinition)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BlockfaceReservation(models.Model):
    user = model.ForeignKey(User)
    # We do not plan on Blockface records being deleted, but we should
    # make sure that a Blockface that has been reserved cannot be
    # deleted out from under a User who had planned to map it.
    blockface = model.ForeignKey(Blockface, on_delete=models.PROTECT)
    is_mapping_with_paper = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    canceled_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
