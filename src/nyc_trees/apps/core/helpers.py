
def user_is_census_admin(user):
    return user.is_authenticated() and user.is_census_admin


def user_is_group_admin(user, group):
    return user.is_authenticated() and (user.is_census_admin
                                        or group.admin == user)


def user_has_online_training(user):
    return user.is_authenticated() and user.online_training_complete


def user_has_field_training(user):
    return user.is_authenticated() and user.field_training_complete


def user_is_individual_mapper(user):
    return user.is_authenticated() and user.individual_mapper
