from . import oauth
from flask import render_template, request
from models import Client, User, Token
from . import provider


@oauth.route('/token', methods=['POST'])
@provider.token_handler
def access_token(*args, **kwargs):
    """Creates a token given a user name, password and client id."""
    return None


@oauth.route('/check', methods=['GET'])
@provider.require_oauth()
def check():
    """Shows who the authorized user is."""
    access_token = request.oauth.headers.get('Authorization').split(' ')[1]
    token = Token.find(access_token)
    return 'Authorized as {}'.format(token.user.username)


@oauth.route('/', methods=['GET', 'POST'])
def management():
    """Provides a quick management screen for users, clients and tokens."""
    if request.method == 'POST' and request.form['submit'] == 'Add User':
        # Create a new user if the 'Add User' form has been sent.
        User.save(request.form['username'], request.form['password'])
    if request.method == 'POST' and request.form['submit'] == 'Add Client':
        # Create a new client if the 'Add Client' form has been sent.
        Client.generate()
    # Show the management page.
    return render_template(
        'management.html',
        users=User.all(),
        clients=Client.all(),
        tokens=Token.all()
    )
