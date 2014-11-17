#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Default to development settings if there is nothing in the environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "nyc_trees.settings.development")

    # We *always* want to use the test settings for test commands,
    # regardless of what is in the environment
    if 'test' in sys.argv or 'selenium' in sys.argv:
        os.environ["DJANGO_SETTINGS_MODULE"] = "nyc_trees.settings.test"

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
