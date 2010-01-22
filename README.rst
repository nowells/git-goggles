#######################
 git-goggles Readme
#######################

git-goggles is a git management utilities that allows you to manage your source code as
it evolves through its development lifecycle.

Overview
========

This project accomplishes two things:

* Manage the code review state of your branches
* Gives a snapshot of the where your local branches are vs origin in terms of being ahead / behind on commits

There is a nice blog post describing the features along with screenshots at http://bit.ly/git-goggles

Field Reference
===============

In the table outputted by git-goggles, each row corresponds to a branch, with the following fields:

* Status: the current status of your branch

    * new: this is a branch that has never been through the review process
    * review: this branch has code that needs to be reviewed
    * merge: everything has been reviewed, but needs to be merged into parent (same as done for being ahead)
    * done: reviewed and merged (doens't matter if you're behind but you can't be ahead)

* Branch: the branch name

* Review: how many commits have taken place since the last review

* Ahead: how many commits are in your local branch that are not in origin

* Behind: how many commits are in origin that are not in your local branch

* Pull & Push: whether your branches need to be pushed or pulled to track origin

    * green checkbox: you don't need to pull
    * red cross: you need to pull
    * question mark: you either don't have a checked out copy of this branch or you need to prune your local tree

* Modified: the last time that HEAD was modified (NOT the last time the review happened)

Installation
============

To install from PyPi you should run one of the following commands. (If you use pip for your package installation, you should take a look!)

::

  pip install git-goggles

or

::

  easy_install git-goggles

Checkout the project from github http://github.com/nowells/git-goggles

::

  git clone git://github.com/nowells/git-goggles.git

Run setup.py as root

::

  cd git-goggles
  sudo python setup.py install

**Documentation**:
With `Sphinx <http://sphinx.pocoo.org/>`_ docs deployment: in the docs/ directory, type:

::

  make html

Then open ``docs/_build/index.html``

Usage
=====

Viewing the status of your branches:

::

  git goggles

Starting your review process (shows an origin diff):

::

  git goggles codereview

Complete your review process (automatically pushes up):

::

  git goggles codereview complete

Configuration
=============

You can set a few configuration variables to alter to way git-goggles works out of the box.

Disable automatic fetching from all remote servers.

::

  git config --global gitgoggles.fetch false

Disable colorized output

::

  git config --global gitgoggles.colors false

Alter the symbols used to display success, failure, unknown states

::

  git config --global gitgoggles.icons.success "OK"
  git config --global gitgoggles.icons.failure "FAIL"
  git config --global gitgoggles.icons.unknown "N/A"

Alter the colors of branch states. The available colors are [grey, red, green, yellow, blue, magenta, cyan, white]

::

  git config --global gitgoggles.colors.local cyan
  git config --global gitgoggles.colors.new red
  git config --global gitgoggles.colors.review red
  git config --global gitgoggles.colors.merge yellow
  git config --global gitgoggles.colors.done green

Alter the width of branch column to turn on wordwrap.

::

  git config --global gitgoggles.table.branch-width 15

Alter the table cell padding (defaults to 0)

::

  git config --global gitgoggles.table.left-padding 1
  git config --global gitgoggles.table.right-padding 1

Alter the display of horizontal rule between rows of table (default false)

::

  git config --global gitgoggles.table.horizontal-rule true

Internals
=========

git-goggles works by creating and managing special tags called
'codereview-<branch_name>' and tracking them against HEAD.

The first time a codereview is completed, the tag is created. Subsequent
reviews delete and re-create the tag so that it awlays accurately tracks HEAD.