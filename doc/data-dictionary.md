# Trees Count! 2015 Data Dictionary

## user

column                         | type               | required                   | detail
-------------------------------|--------------------|----------------------------|----------
id                              |number              |required                    |unique,pk
username                        |30 characters       |required                    |unique
email                           |valid email address |required                    |unique
first_name                      |30 characters       |required, defaults to empty |
last_name                       |30 characters       |required, defaults to empty |
online_training_complete        |t/f                 |required, defaults to f     |
individual_mapper               |t/f                 |required, defaults to f     |
requested_individual_mapping_at |date and time       |optional                    |
is_flagged                      |t/f                 |required, defaults to f     |
is_banned                       |t/f                 |required, defaults to f     |
is_census_admin                 |t/f                 |required, defaults to f     |
is_ambassador                   |t/f                 |required, defaults to f     |
created_at                      |date and time       |required                    |
updated_at                      |date and time       |required                    |

## group

column                        | type                     | required                   | detail
------------------------------|--------------------------|----------------------------|----------
id                            |number                    |required                    |unique,pk
name                          |255 characters            |required                    |unique
description                   |text                      |required, defaults to empty |
contact_info                  |text                      |required, defaults to empty |
contact_email                 |valid email address       |optional                    |
contact_url                   |valid URL                 |optional                    |
admin_id                      |id of user                |required                    |
image                         |text image file reference |optional                    |
is_active                     |t/f                       |required, defaults to t     |
created_at                    |date and time             |required                    |
updated_at                    |date and time             |required                    |

## event

column                         | type                     | required                   | detail
-------------------------------|--------------------------|----------------------------|----------
id                             |number                    |required                    |unique,pk
group_id                       |id of group               |required                    |
description                    |text                      |required, defaults to empty |
contact_email                  |valid email address       |optional                    |
contact_info                   |text                      |required, defaults to empty |
begins_at                      |date and time             |required                    |
ends_at                        |date and time             |required                    |
the_geom_webmercator           |Point geometry EPSG:3857  |required                    |
max_attendees                  |number                    |required                    |
includes_training              |t/f                       |required, defaults to f     |
is_canceled                    |t/f                       |required, defaults to f     |
is_private                     |t/f                       |required, defaults to f     |
url_name                       |32 characters             |required                    |unique
created_at                     |date and time             |required                    |
updated_at                     |date and time             |required                    |

## blockface

column                         | type                               | required                   | detail
-------------------------------|------------------------------------|----------------------------|-----------
|id                            |number                              |required                    |unique,pk
|uvm_id                        |255 characters                      |required                    |unique
|the_geom_webmercator          |LineString geometry EPSG:3857       |required                    |
|is_available                  |t/f                                 |required, defaults to t     |
|created_at                    |date and time                       |required                    |
|updated_at                    |date and time                       |required                    |

## territory

column                         | type                     | required                   | detail
-------------------------------|--------------------------|----------------------------|-----------
id                             |number                    |required                    |unique,pk
group_id                       |id of a group             |required                    |
blockface_id                   |id of blockface           |required                    |
created_at                     |date and time             |required                    |
updated_at                     |date and time             |required                    |

## follow

column                        | type                     | required                   | detail
------------------------------|--------------------------|----------------------------|-----------
id                            |number                    |required                    |unique,pk
user_id                       |id of a user              |required                    |
group_id                      |id of a group             |required                    |
created_at                    |date and time             |required                    |
updated_at                    |date and time             |required                    |

## trustedmapper

column                        | type                     | required                   | detail
------------------------------|--------------------------|----------------------------|-----------
id                            |number                    |required                    |unique,pk
user_id                       |id of a user              |required                    |
group_id                      |id of a group             |required                    |
created_at                    |date and time             |required                    |
updated_at                    |date and time             |required                    |

## trainingresult

column                        | type                     | required                   | detail
------------------------------|--------------------------|----------------------------|-----------
id                            |number                    |required                    |unique,pk
user_id                       |id of a user              |required                    |
module_name                   |255 characters            |required                    |
score                         |number                    |optional                    |
created_at                    |date and time             |required                    |
updated_at                    |date and time             |required                    |

## tree

column                        | type                     | required                   | detail
------------------------------|--------------------------|----------------------------|-----------
id                            |number                    |required                    |unique,pk
survey_id                     |id of a survey            |required                    |
tree_number                   |number                    |required                    |
distance                      |number                    |required                    |
length                        |number                    |required                    |
circumference                 |number                    |required                    |
width                         |number                    |required                    |
position                      |10 characters             |required                    |
fastigate                     |t/f                       |required                    |
status                        |10 characters             |required                    |
house_number                  |number                    |required                    |
genus                         |50 characters             |required                    |
species                       |50 characters             |required                    |
species_confirmed             |number                    |required                    |
end_distance                  |number                    |required                    |
order_on_street               |number                    |required                    |
street                        |50 characters             |required                    |
curb_offset                   |number                    |required                    |
created_at                    |date and time             |required                    |
updated_at                    |date and time             |required                    |

## survey

column                        | type                     | required                   | detail
------------------------------|--------------------------|----------------------------|-----------
id                            |number                    |required                    |unique,pk
user_id                       |id of a user              |required                    |
teammate_id                   |id of a user              |optional                    |
blockface_id                  |id of a blockface         |required                    |
is_flagged                    |t/f                       |required                    |
created_at                    |date and time             |required                    |
updated_at                    |date and time             |required                    |

## eventregistration

column                        | type                     | required                   | detail
------------------------------|--------------------------|----------------------------|-----------
id                            |number                    |required                    |unique,pk
event_id                      |id of an event            |required                    |
did_attend                    |t/f                       |required                    |
created_at                    |date and time             |required                    |
updated_at                    |date and time             |required                    |

## achievementdefinition

column                        | type                     | required                   | detail
------------------------------|--------------------------|----------------------------|-----------
id                            |number                    |required                    |unique,pk
name                          |255 characters            |required                    |
description                   |text                      |required, defaults to empty |
badge_image                   |text image file reference |optional                    |
created_at                    |date and time             |required                    |
updated_at                    |date and time             |required                    |

## achievement

column                        | type                          | required                   | detail
------------------------------|-------------------------------|----------------------------|-----------
id                            |number                         |required                    |unique,pk
user_id                       |id of a user                   |required                    |
achievementdefinition_id      |id of an achievementdefinition |required                    |
created_at                    |date and time                  |required                    |
updated_at                    |date and time                  |required                    |

## blockfacereservation

column                        | type               | required                   | detail
------------------------------|--------------------|----------------------------|-----------
id                            |number              |required                    |unique,pk
user_id                       |id of a user        |required                    |
blockface_id                  |id of a blockface   |required                    |
is_mapping_with_paper         |t/f                 |required                    |
expires_at                    |date and time       |required                    |
canceled_at                   |date and time       |optional                    |
created_at                    |date and time       |required                    |
updated_at                    |date and time       |required                    |
