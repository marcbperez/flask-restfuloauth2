flask-restfuloauth2
===================

A Flask REST endpoint protected with OAuth2.

Installation
------------

Start by downloading and building the project when necessary. The
following commands will do the job on most Debian based Linux
distributions.

.. code:: bash

    git clone https://github.com/marcbperez/flask-restfuloauth2
    cd flask-restfuloauth2
    sudo ./gradlew

Usage
-----

To start the service set the environment variables and run flask, it
will be available at ``http://127.0.0.1:5000``.

.. code:: bash

    export FLASK_APP="restfuloauth2"
    export SECRET_KEY="non-production-key"
    sudo -HE flask run

First, access ``http://127.0.0.1:5000`` and create a user and api
client. Then use the client id, username and password to generate a
bearer token.

.. code:: bash

    curl -X POST -d \
    "grant_type=password&client_id=8diLQbKSkseuZ99Q3kwFAWugXjDvImrqTALeM7sd\
    &username=user&password=pass" \
    http://127.0.0.1:5000/v1/oauth/token

The bearer token can now be used to access the user's protected data.

.. code:: bash

    curl -H "Authorization: Bearer nOVFSNUDoP2bC1ScMRuYz8zCXeTY8F" \
    http://127.0.0.1:5000/v1/oauth/check

The example dummy api is protected and will need a valid user, client
and bearer token. To list, add, modify and delete tasks see the script
below.

.. code:: bash

    # GET the dummy list.
    curl -H "Authorization: Bearer yIMqTV5zOGQlRpIMBMpZnyHFMR0QW3" \
    http://127.0.0.1:5000/v1/dummy
    # Paginate and sort de dummy list by ascending (asc) or descending (desc).
    curl -H "Authorization: Bearer yIMqTV5zOGQlRpIMBMpZnyHFMR0QW3" \
    "http://127.0.0.1:5000/v1/dummy?page=1&max_results=5&sort=id-desc"
    # CREATE a new dummy.
    curl -X POST -H "Authorization: Bearer yIMqTV5zOGQlRpIMBMpZnyHFMR0QW3" \
    -d "public=0" \
    http://127.0.0.1:5000/v1/dummy
    # MODIFY a dummy stating its etag.
    curl -X PUT -H "Authorization: Bearer yIMqTV5zOGQlRpIMBMpZnyHFMR0QW3" \
    -d "etag=rz05FPx8qOIYJdmYZNLvcWupzh9qLlSoZnphpBFC\
        &public=1" \
    http://127.0.0.1:5000/v1/dummy/1
    # GET a dummy.
    curl -H "Authorization: Bearer yIMqTV5zOGQlRpIMBMpZnyHFMR0QW3" \
    http://127.0.0.1:5000/v1/dummy/1
    # DELETE a dummy stating its etag.
    curl -X DELETE -H "Authorization: Bearer yIMqTV5zOGQlRpIMBMpZnyHFMR0QW3" \
    -d "etag=DMwVytdmg3CtwDgbm9wWOINjX73Iev2n4NFkRsV7" \
    http://127.0.0.1:5000/v1/dummy/1

A search operation is also available. To use it send an url-encoded JSON
``search`` parameter to an item endpoint such as
``http://127.0.0.1:5000/v1/dummy``. Valid column condition operators are
``and`` and ``or``. As for column operators all ``=``, ``!=``, ``<``,
``<=``, ``>``, ``>=`` and ``like`` are available.

.. code:: json

    {
      "operator": "and",
      "conditions": [
        {
          "column": "id",
          "operator": "=",
          "value": 3
        },
        {
          "operator": "or",
          "conditions": [
            {
              "column": "public",
              "operator": "=",
              "value": 1
            },
            {
              "column": "etag",
              "operator": "!=",
              "value": ""
            }
          ]
        }
      ]
    }

Testing
-------

Test checks are executed automatically every time the project is built.
Builds can be done remotely or continuously on a development context.
For continuous integration and development use docker-compose. This is
recommended to keep the system clean while the project is built every
time the sources change.

.. code:: bash

    sudo docker-compose up

For continuous integration and development without any dependencies use
the Gradle wrapper. This is the best option if the wrapper is available
and the Docker context is not valid. For a full list of tasks, see
``sudo ./gradlew tasks --all``. For a CI cycle use
``sudo ./gradlew --continuous``.

For continuous integration and development without Docker or the project
wrapper use Gradle directly. This will create the wrapper in case it is
not present. Similar to the above, for a CI cycle use
``sudo gradle --continuous``. Gradle 3.4.1 is required for this to work.
Plain Docker is also available for remote integration tasks and alike.
Build the image with ``sudo docker build .`` and run a new container
with it. Information on how to install Docker and docker-compose can be
found in their `official
page <https://docs.docker.com/compose/install/>`__. A similar
installation guide is available `for
Gradle <https://gradle.org/install>`__.

Troubleshooting
---------------

The `issue
tracker <https://github.com/marcbperez/flask-restfuloauth2/issues>`__ intends
to manage and compile bugs, enhancements, proposals and tasks. Reading
through its material or reporting to its contributors via the platform
is strongly recommended.

Contributing
------------

This project adheres to `Semantic Versioning <http://semver.org>`__ and
to certain syntax conventions defined in
`.editorconfig <.editorconfig>`__. To get a list of changes refer to the
`CHANGELOG <CHANGELOG.md>`__. Only branches prefixed by *feature-*,
*hotfix-*, or *release-* will be considered:

-  Fork the project.
-  Create your new branch:
   ``git checkout -b feature-my-feature develop``
-  Commit your changes: ``git commit -am 'Added my new feature.'``
-  Push the branch: ``git push origin feature-my-feature``
-  Submit a pull request.

Credits
-------

This project is created by `marcbperez <https://marcbperez.github.io>`__ and
maintained by its `author <https://marcbperez.github.io>`__ and contributors.

License
-------

This project is licensed under the `Apache License Version
2.0 <LICENSE>`__.
