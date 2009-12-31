###################
 Django-Pluggables
###################
Django-Pluggables provides a design pattern for making reusable apps "pluggable" so that apps can exist at multiple URL locations and be presented by other apps or models.

Overview
========
Django-Pluggables is a design pattern that endows reusable applications with a few additional features:

#. Applications can exist at multiple URL locations (e.g. http://example.com/foo/app/ and http://example.com/bar/app/).
#. Applications can be "parented" to other applications or objects which can then deliver specialized context information.
#. Posting form data and error handling can happen in locations that make sense to the user, as opposed to the common practice of using templatetags and standalone error or preview pages for form data processing.
#. Views and templates remain generic and reusable.

Installation
============

Django-Pluggables can be added to your Django project like any other reusable app. To see the examples in action, fun the following commands:

First off, the native Mac implementation of sed is not as robust as we expect. Therefore install `Super Sed <http://sed.sourceforge.net/grabbag/ssed/>`_  Then run ::

   $ easy_install Fabric==0.1.1 pip virtualenv
   $ fab bootstrap
   $ ./examples/sillywalks/manage.py runserver

Voila! You now have a fully functional site running at http://127.0.0.1:8000/

Usage
=====

To utilize Django-Pluggables, you will need to do a little bit of configuration. First you must have a two applications:

#. A reusable app that will be made Pluggable.
#. An app that will expose an instance of the Pluggable app in its URL hierarchy (this app does not need to be reusable).

Installation and development of these two apps can begin normally. The individual functions of the apps should be standalone. The Django-Pluggables pattern delivers needed context and parameters to the app that is being made Pluggable when it is called from the URL hierarchy of the other app.

To set up the relationship between these two apps, it is necessary to define two items:

#. The URLconf that defines the URLs that will invoke the Pluggable app instance.
#. The pluggable definition that will supply the Pluggable app with its required context and parameters.

.. note::

    In the following examples we will use two imaginary apps: ``sillywalks`` and ``complaints``. These would be imported in your modules like so::

        from sillywalks.models import Walk
        from complaints.models import Complaint

    In the examples we discuss below, the ``sillywalks`` app lives at the URL::

        http://example.com/sillywalks/

    The ``sillywalks`` app utilizes the ``complaints`` app to field complaints about various types of walk. To provide an excellent user experience, the ``complaints`` forms and functionality should be presented at a URL beneath the ``sillywalks`` URL::

        http://example.com/sillywalks/<walk_name>/complaints/

    Also, the presentation of ``complaints`` functionality beneath the ``sillywalks`` app should adhere to the ``sillywalks`` templates pattern, including various walk-specific information that must be supplied through additional, non- ``complaints`` app context.

Defining the URLconf
--------------------
In order to make the ``complaints`` app pluggable, we first must define a pluggable URLs file for it::

    class ComplaintsPluggable(PluggableApp):
        urlpatterns = patterns('',
            url(r'^$', 'complaints.views.view_complaint', name='complaints_view_complaint'),
            url(r'^activity_feed/$', 'complaints.views.submit_complaint', name='complaints_submit_complaint'),

    ...

.. note::

    Only one pluggable URLs file is required for an app that you wish to make pluggable. This URLconf may be subclassed for additional flexibility when using the pluggable app in conjunction with other apps, but it is likely that one definition of pluggable URLs will be sufficient for most use cases.

Defining the Pluggable Config and Context
-----------------------------------------

Once the ``complaints`` app has been set up with the pluggable URLs, it is necessary to define the context that will be delivered to the ``complaints`` app and add these URLs to the URLconf for the ``sillywalks`` app::

    from complaints.urls import ComplaintsPluggable

    class SillyWalkComplaints(ComplaintsPluggable):
        def pluggable_view_context(self, request, complaint_id):
            return dict(complaint_id=complaint_id)

        def pluggable_template_context(self, request, slug):
            return dict(silly_walk=SillyWalk.objects.get(slug=slug))

        def pluggable_config(self):
            return dict(base_template='sillywalks/base.html')

    urlpatterns = SillyWalkComplaints('sillywalk')

More
====

The primary repository for Django-Pluggables is located at:

`http://github.com/nowells/django-pluggables/ <http://github.com/nowells/django-pluggables/>`_

Django-Pluggables was created by Nowell Strite.
