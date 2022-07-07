=======================================
TFProtocol Client implemented in python
=======================================

https://img.shields.io/pypi/v/tfprotocol_client?style=plastic
https://img.shields.io/github/repo-size/lagcleaner/tfprotocol_client_py?style=plastic

----------------------
Introduction
----------------------

The especifications for the *Transference Protocol* is available in this `repository
<https://github.com/GoDjango-Development/TFProtocol/blob/main/doc/>`_.


----------------------
How to install?
----------------------
The package is available at `pypi <https://pypi.org>`_, to be installed from **pip** with the
next command:

.. code-block:: bash

    pip install tfprotocol_client

----------------------
How to use?
----------------------

To use the *Transference Protocol* through this library, you must create an instance of
*TfProtocol* with the specified parameters and have an online server to connect to.

.. code-block:: python

    from tfprotocol_client.misc.constants import RESPONSE_LOGGER
    from tfprotocol_client.tfprotocol import TfProtocol

    ADDRESS = 'tfproto.expresscuba.com'
    PORT = 10345
    clienthash = '<clienthash>'
    publickey = '<publickey>'

    proto = TfProtocol('0.0', publickey, clienthash, ADDRESS, PORT)
    proto.connect()
    proto.echo_command('Hello World', response_handler=RESPONSE_LOGGER)
    proto.disconnect()


----------------------
For Contributors
----------------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
How to install dev environment?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To set up the development environment, all you need as a prerequisite is to have python Python
2.7  or 3.5+ and `poetry <https://python-poetry.org/>`_ installed. If you need to install poetry
follow `these steps <https://python-poetry.org/docs/#installation>`_ and come back. 

With this in mind, to install the necessary dependencies and create a python environment for
this project, proceed to run the following command in the root directory of the project.

.. code-block:: bash

    poetry install


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
How is structured?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This library is made up of 4 folders and the particular implementations of the ``TfProtocolSuper``
class, the folders are structured as follows:

- **connection**: where all socket and low-level communication is located.
- **models** where the complex objects used all over the package are defined.
- **security** where is implemented the methods and classes to encrypt and decrypt the messages for communication and also the utils for do the hashing stuff where is needed.
- **misc** folder to hold all utils and not related to any other folder concept.

Here the visual schema for all the classes and his relations with others:

.. image:: https://raw.githubusercontent.com/lagcleaner/tfprotocol_client_py/master/doc/static/classes.png
   :alt: class relations
   :align: center

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
How is publish the package?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To publish the package you need to run the following command in the root directory of the package:

.. code-block:: bash

    poetry publish

