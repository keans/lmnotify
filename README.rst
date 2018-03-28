lmnotify
========

``lmnotify`` is a package for sending notifications to
`LaMetric Time <http://lametric.com/>`_. To achieve this, the package
encapsulates the REST API calls that are sent to the LaMetric device.


Module Installation
-------------------

The easiest way to install the ``lmnotify`` module is via ``pip``:

::

    pip install lmnotify

or clone/download this repository and install it:

::

    python3 setup.py install

or

::

    python setup.py install


Basic Setup
-----------

The LaMetric Time can only be accessed by authorized applications. Therefore,
each application that wants to access the device needs to be registered
at the `LaMetric Developer <https://developer.lametric.com>`_ webpage.


Creating a Custom Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following steps are required to register the ``lmnotify`` python module
as new LaMetric application at their webpage:

1) Sign Up and login to the developer webpage https://developer.lametric.com
2) Click the **Create** button in the upper right corner, then select
   **Notification App** and click **Create** again.
3) Enter an app name, a description and a redirect URL
4) Finally, click **Save** to create the application.

For the newly created app you will obtain credentials i.e. the **client id**
and a **client secret**. Both are required in the following to to setup the
python module.


Background
~~~~~~~~~~

Although, the ``lmnotify`` python module must be registered with the LaMetric
cloud, on the long run, there is only a very limited interaction with the cloud
necessary. The main functions of the cloud-related RESTful API deal with user
information stored at the cloud as well as the registered LaMetric devices.
Particularly, the latter is of great paramount since the list of devices
contains an API key for each device that can be used to communicate with the
device in the local network without connecting to the cloud.

For that reason, the default configuration of the module will receive all
LaMetric devices from the cloud on the first call of ``get_devices`` and store
them in the ``~/.lmdevices`` file. All further calls of ``get_devices`` will
simply read this file and return the devices without any interaction with the
LaMetric cloud.


Configuration of the Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are three different ways to provide the LaMetric API credentials to the
module: by constructor, by environment variables or by config file.

1. **By constructor**: Just provide the ``client_id`` and ``client_secret`` in
the constructor of the ``LaMetricManager`` class, e.g.:

::

    CLIENT_ID = "<my_client_id>"
    CLIENT_SECRET = "<my_client_secret>"

    lmn = LaMetricManager(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

2. **By environment variables**: Just set the ``LAMETRIC_CLIENT_ID`` and the
``LAMETRIC_CLIENT_SECRET`` environment variable, e.g. in bash:

::

    export LAMETRIC_CLIENT_ID="<my_client_id>"
    export LAMETRIC_CLIENT_SECRET="<my_client_secret>"

When not providing the ``client_id`` and ``client_secret`` in the constructor,
the environment variables will be used instead.

3. **By config file**: The default config file is set to ``~/.lmconfig``. When
initializing the ``LaMetricManager`` class without parameters the config file
will be loaded, if it is already existing. Otherwise you can set the
``auto_create_config`` parameter in the constructor to True, to create an empty
configuration file. Simply fill your credentials in the config file:

::

    [lametric]
    client_id = <put the client id here>
    client_secret = <put the client secret here>

On the next start, the config file will be read automatically, when neither
``client_id`` and ``client_secret`` are set in the constructor nor the
``LAMETRIC_CLIENT_ID`` and the ``LAMETRIC_CLIENT_SECRET`` environment variables
are set.

As stated above in the background section, after the devices have been obtained
from the LaMetric cloud once, all further interaction can be done locally
without any interaction with the LaMetric cloud.


Example
-------

As simple example, let's send a "hello world" message with an icon to the
LaMetric Time. It is assumed that you have provided the application credentials
using the environment variables or the config file so that no parameters are
set in the constructor of the LaMetricManager.

::

    from lmnotify import LaMetricManager, Model, SimpleFrame

    # create an instance of the LaMetricManager
    lmn = LaMetricManager()

    # get devices
    devices = lmn.get_devices()

    # use first device to do some tests
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

If you want to contribute in the development, please check out the source code
at https://github.com/keans/lmnotify.git .


To get started with the development:

::

    git clone git@github.com:keans/lmnotify.git
    cd lmnotify/
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt


For verbose debug output simply set the logging level to debug:

::

    import logging
    logging.basicConfig(level=logging.DEBUG)
