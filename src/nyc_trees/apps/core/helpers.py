from apps.event.models import EventRegistration


def user_is_census_admin(user):
    return user.is_authenticated() and user.is_census_admin


def user_is_group_admin(user, group):
    return user.is_authenticated() and (user.is_census_admin
                                        or group.admin == user)


def user_has_online_training(user):
    return user.is_authenticated() and user.online_training_complete


def user_has_field_training(user):
    return user.is_authenticated() and EventRegistration.objects.filter(
        user=user, did_attend=True, event__includes_training=True)


def user_is_individual_mapper(user):
    return user.is_authenticated() and user.individual_mapper
