# flask-restful-oauth2

A Flask service to export PDF and XML reports.

## Installation

This projects uses Gradle (at least version 3.3) as its build system along with
a Docker and docker-compose wrapper for continuous development. On Debian Linux
distributions Gradle can be installed with the following commands:

```bash
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:cwchien/gradle
sudo apt-get update
sudo apt-get install default-jdk gradle=3.4-0ubuntu1
```

If you prefer to install Docker and docker-compose (highly recommended) refer to
the [official instructions][install-docker-compose].

## Usage

To start the service get the project and install its dependencies, set the
environment variables and run flask. The service will be available at
`http://localhost:5000`.

```bash
git clone https://github.com/marcbperez/flask-restful-oauth2
cd flask-restful-oauth2
export FLASK_APP="restfuloauth2"
export SECRET_KEY="non-production-key"
sudo -HE gradle
sudo -HE flask run
```

First, access `http://127.0.0.1:5000` and create a user and api client. Then use
the client id, username and password to generate a bearer token.

```bash
curl -X POST -d \
"grant_type=password&client_id=8diLQbKSkseuZ99Q3kwFAWugXjDvImrqTALeM7sd\
&username=user&password=pass" \
http://127.0.0.1:5000/oauth/token
```

The bearer token can now be used to access the user's protected data.

```bash
curl -H "Authorization: Bearer nOVFSNUDoP2bC1ScMRuYz8zCXeTY8F" \
http://127.0.0.1:5000/oauth/check
```

The example todo api is protected and will need a valid user, client and bearer
token. To list, add, modify and delete tasks see the script below.

```bash
# GET the todo list
curl -H "Authorization: Bearer nOVFSNUDoP2bC1ScMRuYz8zCXeTY8F" \
http://127.0.0.1:5000/todo
# CREATE a new todo
curl -X POST -H "Authorization: Bearer nOVFSNUDoP2bC1ScMRuYz8zCXeTY8F" \
-d "description=Remember the bread" \
http://127.0.0.1:5000/todo
# MODIFY a todo
curl -X PUT -H "Authorization: Bearer nOVFSNUDoP2bC1ScMRuYz8zCXeTY8F" \
-d "description=Remember the butter" \
http://127.0.0.1:5000/todo/1
# GET a todo
curl -H "Authorization: Bearer nOVFSNUDoP2bC1ScMRuYz8zCXeTY8F" \
http://127.0.0.1:5000/todo/1
# DELETE a todo
curl -X DELETE -H "Authorization: Bearer nOVFSNUDoP2bC1ScMRuYz8zCXeTY8F" \
http://127.0.0.1:5000/todo/1
```

## Testing

Tests will be executed by default every time the project is built. To run them
manually start a new build or use Gradle's test task. For a complete list of
tasks check `gradle tasks --all`.

```bash
export FLASK_APP="restfuloauth2"
export SECRET_KEY="non-production-key"
sudo -HE gradle test
```

A continuous build cycle can be executed with `gradle --continuous` inside a
virtual environment, or with Docker.

```
sudo docker-compose up
```

## Troubleshooting

The [issue tracker][issue-tracker] intends to manage and compile bugs,
enhancements, proposals and tasks. Reading through its material or reporting to
its contributors via the platform is strongly recommended.

## Contributing

This project adheres to [Semantic Versioning][semver] and to certain syntax
conventions defined in [.editorconfig][editorconfig]. To get a list of changes
refer to the [CHANGELOG][changelog]. Only branches prefixed by *feature-*,
*hotfix-*, or *release-* will be considered:

  - Fork the project.
  - Create your new branch: `git checkout -b feature-my-feature develop`
  - Commit your changes: `git commit -am 'Added my new feature.'`
  - Push the branch: `git push origin feature-my-feature`
  - Submit a pull request.

## Credits

This project is created by [marcbperez][author] and maintained by its
[author][author] and contributors.

## License

This project is licensed under the [Apache License Version 2.0][license].

[author]: https://marcbperez.github.io
[issue-tracker]: https://github.com/marcbperez/flask-restful-oauth2/issues
[editorconfig]: .editorconfig
[changelog]: CHANGELOG.md
[license]: LICENSE
[semver]: http://semver.org
[install-docker-compose]: https://docs.docker.com/compose/install/
