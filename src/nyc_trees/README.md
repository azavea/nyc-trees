# Django 1.7 Template

## Overview
This is a modified and repurposed version of this project [https://github.com/dereknutile/django-1.6-template](https://github.com/dereknutile/django-1.6-template).

The goal is to have a standardized baseline Django 1.7 application skeleton to build web applications from.

## Requirements
The documentation below assumes you're using [virtualenv](http://www.virtualenv.org/ "Virtualenv") and [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/ "Virtualenvwrapper") to manage versions and dependencies within different development environments.  In order to properly develop this application you should have the following installed:

* [Virtualenv](http://www.virtualenv.org/ "Virtualenv")
* [Virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/ "Virtualenvwrapper")

## Setup

* [Create a Virtual Environment](#create-virtualenv)
* [Clone the Template](#clone-template)
* [Install Dependencies](#install-dependencies)
* [Run Server](#run-server)

### [Create a Virtual Environment](id:anchor-create-a-virtual-environment)

In a terminal, create your virtual environment using virtualenvwrapper commands.  Here we'll name it ```django17```, but you may want to change it to something that makes more sense for your this environment.

    $ mkvirtualenv django17

You should see something similar to the following:

    New python executable in django17/bin/python
    Installing Setuptools ...done.
    Installing Pip ...done.

…and your prompt should now look something like this:

    (django17)$

Note: See the [Virtualenvwrapper Docs](http://virtualenvwrapper.readthedocs.org/en/latest/command_ref.html "Virtualenvwrapper Docs") for more commands.

### [Clone the Template](id:anchor-clone-the-template)

To create a project using this template, open a terminal and navigate to the place where you want to keep your project, let's say it's **~/projects/**.

    (django17)$ cd ~/projects

Assuming you are still in the context of the django17 virtual environment, let's clone the project into a directory called **projectName**:

    (django17)$ git clone https://github.com/dereknutile/django-1.7-template.git projectName

### [Install Dependencies](id:anchor-install-dependencies)

First, make sure you are in the directory for the project you just made:

    (django17)$ cd projectName

You should now be in the ~/projects/**projectName** directory.


Installing dependencies is done using PIP and is relative to your environment.  The environment requirements are listed within requirements directory with a file name like _{environment}.txt_.

To install requirements on your development system, use PIP to reference the development configuration file:

    (django17)$ pip install -r requirements/development.txt

Optional Step: If you have Bower installed, you can update the asset dependencies now.
    
    (django17)$ bower install


### [Run Server](id:anchor-run-server)

First, initialize the SQLITE database.  *Note: you may be asked to define the superuser/admin*.

    (django17)$ python project/manage.py syncdb

Run the server ...

    (django17)$ python project/manage.py runserver

Test it out: [http://127.0.0.1:8000](127.0.0.1:8000).

## Best Practices

### Apps
There's a directory to drop your apps into: ```project/apps/```.  To keep the directory structure clean, organized, and re-usable, place your existing apps right in that directory or use django-admin.py to generate them in that directory like this:

    (django17)$ cd project/apps/
    (django17)$ django-admin.py startapp newapp

Once you've got your app in the right place, call it from the right environmental settings file.  If this app can be used in any environment, then open ```project/project/settings/base.txt``` and find the **LOCAL_APPS()** tuple.  In the example above, the LOCAL_APP tuple would look like this (don't forget to include the *apps* prefix):

    # Apps specific for this project go here.
    LOCAL_APPS = (
        'apps.newapp',
    )
