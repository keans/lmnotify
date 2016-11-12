lmnotify
========

``lmnotify`` is a package for sending notifications to `LaMetric Time <http://lametric.com/>`_. To achieve this, the package encapsulates the REST API calls to the LaMetric webpage.


Installation
------------

The easiest way for installing ``lmnotify`` is via ``pip``:

::

    pip install lmnotify


Config
------

The LaMetric Time can only be accessed by authorized applications. Therefore, each application that wants to access the LaMetric time needs to be registered at the `LaMetric Developer <https://developer.lametric.com>`_ webpage. Sign Up and login to the developer webpage. Click the **Create** button in the upper right corner, then select **Notification App** and click **Create** again. Enter an app name, a description and a redirect URL. Finally, click **Save** to create the application. For the newly created app you will obtain a **client id** and a **client secret** that is required in the following.

The obtained credentials must be stored in the ``~/.lmconfig`` config file so that ``lmnotify`` can access it.

::

    [lametric]
    client_id = <put the client id here>
    client_secret = <put the client secret here>

This information will be read by ``lmnotify``.

Example
-------

As simple example, let's send a "hellow world" message with an icon to the LaMetric Time.

::

    from lmnotify import LaMetricManager, Model, SimpleFrame

    lmn = LaMetricManager()

    # get devices
    devices = lmn.get_devices()

    # use first device to do some tests
    lmn.set_device(devices[0])

    # obtain all registered devices from the LaMetric cloud
    devices = lmn.get_devices()

    # select the first device for interaction
    lmn.set_device(devices[0])

    # prepare a simple frame with an icon and some text
    sf = SimpleFrame("i210", "Hello World!")

    # prepare the model that will be send as notification
    model = Model(frames=[sf])

    # send the notification the device
    lmn.send_notification(model)


Development
-----------

If you want to contribute in the development, please check out the source code at https://github.com/keans/lmnotify.git .


To get started with the development:

::

    git clone git@github.com:keans/lmnotify.git
    cd lmnotify/
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt


Changelog
---------

.. include:: CHANGELOG.rst

