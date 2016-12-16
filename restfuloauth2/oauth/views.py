from . import oauth
from flask import render_template, request
from models import Client, User
from . import provider


@oauth.route('/token', methods=['POST'])
@provider.token_handler
def access_token(*args, **kwargs):
    return None


@oauth.route('/revoke', methods=['POST'])
@provider.revoke_handler
def revoke_token():
    pass


@oauth.route('/check')
@provider.require_oauth()
def protected():
    return 'Authenticated.'


@oauth.route('/', methods=['GET', 'POST'])
def management():
    if request.method == 'POST' and request.form['submit'] == 'Add User':
        User.save(request.form['username'], request.form['password'])
    if request.method == 'POST' and request.form['submit'] == 'Add Client':
        Client.generate()
    return render_template('management.html', users=User.all(),
        clients=Client.all())
