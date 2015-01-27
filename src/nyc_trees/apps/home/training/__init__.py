# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.home.training.types import TrainingStep, TrainingGateway
from apps.home.training import routes as r

# This package attempts to keep all the particulars of training encapsulated,
# such that you can modify how things are wired together in this file without
# digging into the implementation. There are some key exceptions to this:
# * apps.home.urls - imports from this file, gets url params
# * apps.core.models
#   - the user class does a delayed import for a convenience method
#   - the user class has carefully named booleans corresponding
#     to training steps. modify with care.

getting_started = TrainingStep('getting_started',
                               'Getting Started', '20 minutes')
the_mapping_method = TrainingStep('the_mapping_method',
                                  'The Mapping Method', '20 minutes')
tree_data = TrainingStep('tree_data',
                         'Tree Data', '20 minutes')
tree_surroundings = TrainingStep('tree_surroundings',
                                 'Tree Surroundings', '40 minutes')
groups_to_follow = TrainingStep('groups_to_follow',
                                'Groups To Follow', '5 minutes',
                                r.groups_to_follow)

training_summary = TrainingGateway('training_summary',
                                   r.training_list_page,
                                   [getting_started,
                                    the_mapping_method,
                                    tree_data,
                                    tree_surroundings,
                                    groups_to_follow])
