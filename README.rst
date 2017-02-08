lmnotify
========

``lmnotify`` is a package for sending notifications to `LaMetric Time <http://lametric.com/>`_. To achieve this, the package encapsulates the REST API calls to the LaMetric webpage.


Installation
------------

The easiest way for installing ``lmnotify`` is via ``pip``:

::

    pip install lmnotify

or clone/download this repository and

::

    python3 setup.py install

or

::

    python setup.py install


Config
------

The LaMetric Time can only be accessed by authorized applications. Therefore, each application that wants to access the LaMetric time needs to be registered at the `LaMetric Developer <https://developer.lametric.com>`_ webpage. Sign Up and login to the developer webpage. Click the **Create** button in the upper right corner, then select **Notification App** and click **Create** again. Enter an app name, a description and a redirect URL. Finally, click **Save** to create the application. For the newly created app you will obtain a **client id** and a **client secret** that is required in the following.

There are three different ways to provide the LaMetric API credentials to the module: by constructor, by environment variables, by config file.

By constructor
~~~~~~~~~~~~~~

Just provide the ``client_id`` and ``client_secret`` in the constructor of the ``LaMetricManager`` class, e.g.:

::

    CLIENT_ID = "<my_client_id>"
    CLIENT_SECRET = "<my_client_secret>"

    lmn = LaMetricManager(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

By environment variables
~~~~~~~~~~~~~~~~~~~~~~~~

Just set the ``LAMETRIC_CLIENT_ID`` and the ``LAMETRIC_CLIENT_SECRET`` environment variable, e.g. in bash:

::

    export LAMETRIC_CLIENT_ID="<my_client_id>"
    export LAMETRIC_CLIENT_SECRET="<my_client_secret>"

When not providing the ``client_id`` and ``client_secret`` in the constructor, the environment variables will be used instead.


By config file
~~~~~~~~~~~~~~

The default config file is set to ``~/.lmconfig``. When initializing the ``LaMetricManager`` class without parameters an empty config file will be created that looks like:

::

    [lametric]
    client_id = <put the client id here>
    client_secret = <put the client secret here>

Just provide the corresponding LaMetric credentials and on next start the config file will be read automatically, when neither ``client_id`` and ``client_secret`` are set in the constructor nor the ``LAMETRIC_CLIENT_ID`` and the ``LAMETRIC_CLIENT_SECRET`` environment variables are set.


Example
-------

As simple example, let's send a "hellow world" message with an icon to the LaMetric Time.

::

    from lmnotify import LaMetricManager, Model, SimpleFrame

    # set your LaMetric API credentials here!
    CLIENT_ID = "<my_client_id>"
    CLIENT_SECRET = "<my_client_secret>"

    # create an instance of the LaMetricManager
    lmn = LaMetricManager(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

    # get the LaMetric devices
    devices = lmn.get_devices()

    # use the first device to do some tests
    lmn.set_device(devices[0])

    # prepare a simple frame with an icon and some text
    sf = SimpleFrame("i210", "Hello World!")

    # prepare the model that will be send as notification
    model = Model(frames=[sf])

    # send the notification the device
    lmn.send_notification(model)

For more examples see https://github.com/keans/lmnotify/tree/master/examples .


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

