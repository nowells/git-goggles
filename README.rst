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

Checkout the project from github XXXaddurlonceitexistsXXX:

::

  git clone XXXgiturlXXX

Add to your .bashrc or .profile:

::

  export PATH=$PATH:/<path_to_git-goggles>/bin

**Documentation**:
With `Sphinx <http://sphinx.pocoo.org/>`_ doc deployment: in the doc/ directory, type:

::

  make html

Then open ``doc/_build/index.html``

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

Internals
=========

git-goggles works by creating and managing special tags called
'codereview-<branch_name>' and tracking them against HEAD.

The first time a codereview is completed, the tag is created. Subsequent
reviews delete and re-create the tag so that it awlays accurately tracks HEAD.