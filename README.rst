``pulp_rpm`` Plugin
===================

This is the ``pulp_rpm`` Plugin for `Pulp Project
3.0+ <https://pypi.python.org/pypi/pulpcore/>`__. This plugin provides support for RPM family content
types, similar to the ``pulp_rpm`` plugin for Pulp 2.

All REST API examples bellow use `httpie <https://httpie.org/doc>`__ to perform the requests.
The ``httpie`` commands below assume that the user executing the commands has a ``.netrc`` file
in the home directory. The ``.netrc`` should have the following configuration:

.. code-block::

    machine localhost
    login admin
    password admin

If you configured the ``admin`` user with a different password, adjust the configuration
accordingly. If you prefer to specify the username and password with each request, please see
``httpie`` documentation on how to do that.

This documentation makes use of the `jq library <https://stedolan.github.io/jq/>`_
to parse the json received from requests, in order to get the unique urls generated
when objects are created. To follow this documentation as-is please install the jq
library with:

``$ sudo dnf install jq``

Install ``pulpcore``
--------------------

Follow the `installation
instructions <https://docs.pulpproject.org/en/3.0/nightly/installation/instructions.html>`__
provided with pulpcore.

Install ``pulp-rpm`` from source
--------------------------------

.. code-block:: bash

   sudo -u pulp -i
   source ~/pulpvenv/bin/activate
   git clone https://github.com/pulp/pulp_rpm.git
   cd pulp_rpm
   pip install -e .

Install ``pulp-rpm`` From PyPI
------------------------------

.. code-block:: bash

   sudo -u pulp -i
   source ~/pulpvenv/bin/activate
   pip install pulp-rpm

Make and Run Migrations
-----------------------

.. code-block:: bash

   pulp-manager makemigrations pulp_rpm
   pulp-manager migrate pulp_rpm

Run Services
------------

.. code-block:: bash

   pulp-manager runserver
   sudo systemctl restart pulp_resource_manager
   sudo systemctl restart pulp_worker@1
   sudo systemctl restart pulp_worker@2

Create a repository ``foo``
---------------------------

``$ http POST http://localhost:8000/pulp/api/v3/repositories/ name=foo``

.. code:: json

    {
        "_href": "http://localhost:8000/pulp/api/v3/repositories/8d7cd67a-9421-461f-9106-2df8e4854f5f/",
        ...
    }

``$ export REPO_HREF=$(http :8000/pulp/api/v3/repositories/ | jq -r '.results[] | select(.name == "foo") | ._href')``

Create a new remote ``bar``
-----------------------------

``$ http POST http://localhost:8000/pulp/api/v3/remotes/rpm/ name='bar' url='https://repos.fedorapeople.org/pulp/pulp/fixtures/rpm-unsigned/'``

.. code:: json

    {
        "_href": "http://localhost:8000/pulp/api/v3/remotes/rpm/13ac2d63-7b7b-401d-b71b-9a5af05aab3c/",
        ...
    }

``$ export REMOTE_HREF=$(http :8000/pulp/api/v3/remotes/rpm/ | jq -r '.results[] | select(.name ==
"bar") | ._href')``

Sync repository ``foo`` using remote ``bar``
----------------------------------------------

``$ http POST $remote_HREF'sync/' repository=$REPO_HREF``

Look at the new Repository Version created
------------------------------------------

``$ http GET $REPO_HREF'versions/1/'``

.. code:: json

    {
        "_added_href": "http://localhost:8000/pulp/api/v3/repositories/b787e6ad-d6b6-4e3d-ab12-73eba19b42fb/versions/1/added_content/",
        "_content_href": "http://localhost:8000/pulp/api/v3/repositories/b787e6ad-d6b6-4e3d-ab12-73eba19b42fb/versions/1/content/",
        "_href": "http://localhost:8000/pulp/api/v3/repositories/b787e6ad-d6b6-4e3d-ab12-73eba19b42fb/versions/1/",
        "_removed_href": "http://localhost:8000/pulp/api/v3/repositories/b787e6ad-d6b6-4e3d-ab12-73eba19b42fb/versions/1/removed_content/",
        "content_summary": {
            "rpm": 14
        },
        "created": "2018-02-23T20:29:54.499055Z",
        "number": 1
    }


Upload ``foo.rpm`` to Pulp
-----------------------------

Create an Artifact by uploading the file to Pulp.

``$ http --form POST http://localhost:8000/pulp/api/v3/artifacts/ file@./foo.rpm``

.. code:: json

    {
        "_href": "http://localhost:8000/pulp/api/v3/artifacts/7d39e3f6-535a-4b6e-81e9-c83aa56aa19e/",
        ...
    }

Create ``rpm`` content from an Artifact
-------------------------------------------

Create a content unit and point it to your artifact

``$ http POST http://localhost:8000/pulp/api/v3/content/rpm/ relative_path=foo.rpm
artifact="http://localhost:8000/pulp/api/v3/artifacts/7d39e3f6-535a-4b6e-81e9-c83aa56aa19e/"``

.. code:: json

    {
        "_href": "http://localhost:8000/pulp/api/v3/content/rpm/a9578a5f-c59f-4920-9497-8d1699c112ff/",
        "artifact": "http://localhost:8000/pulp/api/v3/artifacts/7d39e3f6-535a-4b6e-81e9-c83aa56aa19e/",
        "relative_path": "foo.rpm",
        "type": "rpm"
    }

``$ export CONTENT_HREF=$(http :8000/pulp/api/v3/content/rpm/ | jq -r '.results[] | select(
.relative_path == "foo.rpm") | ._href')``


Add content to repository ``foo``
---------------------------------

``$ http POST $REPO_HREF'versions/' add_content_units:="[\"$CONTENT_HREF\"]"``


Create a ``rpm`` Publisher
---------------------------

``$ http POST http://localhost:8000/pulp/api/v3/publishers/rpm/ name=bar``

.. code:: json

    {
        "_href": "http://localhost:8000/pulp/api/v3/publishers/rpm/fd4cbecd-6c6a-4197-9cbe
        -4e45b0516309/",
        ...
    }

``$ export PUBLISHER_HREF=$(http :8000/pulp/api/v3/publishers/rpm/ | jq -r '.results[] | select(.name ==
 "bar") | ._href')``


Use the ``bar`` Publisher to create a Publication
-------------------------------------------------

``$ http POST $PUBLISHER_HREF'publish/' repository=$REPO_HREF``

.. code:: json

    [
        {
            "_href": "http://localhost:8000/pulp/api/v3/tasks/fd4cbecd-6c6a-4197-9cbe-4e45b0516309/",
            "task_id": "fd4cbecd-6c6a-4197-9cbe-4e45b0516309"
        }
    ]

``$ export PUBLICATION_HREF=$(http :8000/pulp/api/v3/publications/ | jq -r --arg PUBLISHER_HREF "$PUBLISHER_HREF" '.results[] | select(.publisher==$PUBLISHER_HREF) | ._href')``

Create a Distribution for the Publication
---------------------------------------

``$ http POST http://localhost:8000/pulp/api/v3/distributions/ name='baz' base_path='foo' publication=$PUBLICATION_HREF``


.. code:: json

    {
        "_href": "http://localhost:8000/pulp/api/v3/distributions/9b29f1b2-6726-40a2-988a-273d3f009a41/",
       ...
    }


Download ``foo.rpm`` from Pulp
---------------------------------

``$ http GET http://localhost:8000/pulp/content/foo/foo.rpm``
