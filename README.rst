flask-restful-oauth2
====================

A Flask REST endpoint protected by OAuth2.

Installation
------------

This projects uses Gradle (at least version 3.3) as its build system
along with a Docker and docker-compose wrapper for continuous
development. On Debian Linux distributions Gradle can be installed with
the following commands:

.. code:: bash

    sudo apt-get install software-properties-common
    sudo add-apt-repository ppa:cwchien/gradle
    sudo apt-get update
    sudo apt-get install default-jdk gradle=3.4-0ubuntu1

If you prefer to install Docker and docker-compose (highly recommended)
refer to the `official
instructions <https://docs.docker.com/compose/install/>`__.

Usage
-----

To start the service get the project and install its dependencies, set
the environment variables and run flask. The service will be available
at ``http://localhost:5000``.

.. code:: bash

    git clone https://github.com/marcbperez/flask-restful-oauth2
    cd flask-restful-oauth2
    export FLASK_APP="restfuloauth2"
    export SECRET_KEY="non-production-key"
    sudo -HE gradle
    sudo -HE flask run

Reports can be exported to PDF and XML. There are also service actions
to get a list of available reports in HTML and XML format.

-  ``http://localhost:5000/`` and ``http://localhost:5000/report`` show
   a list of the reports and its links.
-  ``http://localhost:5000/report/list.xml`` offers the same list in XML
   format.
-  ``http://localhost:5000/report/<report_id>`` shows the report in
   HTML.
-  ``http://localhost:5000/report/<report_id>.pdf`` shows the report in
   PDF.
-  ``http://localhost:5000/report/<report_id>.xml`` shows the report in
   XML.

Testing
-------

Tests will be executed by default every time the project is built. To
run them manually start a new build or use Gradle's test task. For a
complete list of tasks check ``gradle tasks --all``.

.. code:: bash

    export FLASK_APP="restfuloauth2"
    export SECRET_KEY="non-production-key"
    sudo -HE gradle test

A continuous build cycle can be executed with ``gradle --continuous``
inside a virtual environment, or with Docker.

::

    sudo docker-compose up

Troubleshooting
---------------

The `issue
tracker <https://github.com/marcbperez/flask-restful-oauth2/issues>`__
intends to manage and compile bugs, enhancements, proposals and tasks.
Reading through its material or reporting to its contributors via the
platform is strongly recommended.

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
