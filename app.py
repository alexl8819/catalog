""" Main application """
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, session, request, jsonify, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

from .models.category import Base, Category, CategoryItem
from .forms import CreateForm, EditForm, DeleteForm

# pylint: disable=fixme, invalid-name, unused-argument, no-member

# TODO: Test for SQL Injection
# TODO: session should be stored in SQLAlchemy
# TODO: use a cache like memcached

# Load configuration
app = Flask(__name__, static_url_path='', static_folder='./public')
app.config.from_pyfile('./catalog.dev.cfg')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = app.config.get('SECRET_KEY') or 'MAKE_THIS_SECRET'

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
# Initialize extensions used
db = SQLAlchemy(app)
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email'
    }
)

def login_required(f):
    """ Decorator to check if page is restricted """
    @wraps(f)
    def authenticate(*args, **kwargs):
        """ Check session contains access token """
        authenticated = session.get('access_token') is not None

        if not authenticated:
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return authenticate


@app.before_first_request
def setup():
    """ Sets up the application"""
    # Clear and invalidate existing sessions
    session.clear()
    # Set session timeout for 1 minute
    app.permanent_session_lifetime = timedelta(
        minutes=app.config.get('EXPIRE_AFTER_MIN'))
    # Prepare db as new for demo
    Base.query = db.session.query_property()
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)

    categories = app.config.get('DEMO_CATEGORIES').split(',')

    for name in categories:
        db.session.add(Category(name=name))

    items = app.config.get('DEMO_CATEGORY_ITEMS').split(',')

    for item in [_item.split(':') for _item in items]:
        title = item[0]
        category_id = item[1]

        db.session.add(CategoryItem(title=title, category_id=category_id,
                                    created=datetime.now()))

    db.session.commit()


@app.errorhandler(404)
def handle_page_not_found(error=None):
    """ Handle 404 pages manually """
    return render_template('404.html'), 404


@app.teardown_appcontext
def shutdown_session(exception=None):
    """ Tear down db session when closed """
    db.session.remove()


# Catalog Resource API
@app.route('/catalog/<category>/Items', methods=['GET'])
def get_catalog_items(category):
    """ Returns a list of items for a category"""
    authenticated = session.get('access_token') is not None
    categories = [_category.name for _category in Category.query.order_by(
        Category.id.asc()).all()]

    if category not in categories:
        return redirect(url_for('index'))

    items = [item.title for item in CategoryItem.query.join(Category)
             .filter(Category.name == category)
             .order_by(CategoryItem.created.desc())
             .all()]

    return render_template('items.html', category=category,
                           categories=categories,
                           items=items,
                           authenticated=authenticated)


@app.route('/catalog/<category>/<item>', methods=['GET'])
def get_catalog_item(category, item):
    """ Returns a specific item in a category """
    authenticated = session.get('access_token') is not None
    categories = [_category.name for _category in Category.query.order_by(
        Category.id.asc()).all()]

    if category not in categories:
        return redirect(url_for('index'))

    item = CategoryItem.query.join(Category).filter(
        Category.name == category).filter(CategoryItem.title == item).first()

    if not item:
        return redirect(url_for('index'))

    return render_template('item.html', category=category,
                           item=item,
                           authenticated=authenticated)


@app.route('/catalog/item/create', methods=['GET', 'POST'])
@login_required
def create_category_item():
    """ Creates new category item """
    authenticated = session.get('access_token') is not None
    categories = Category.query.order_by(Category.id.asc()).all()

    form = CreateForm()
    form.category.choices = [(category.id, category.name)
                             for category in categories]

    if request.method == 'POST' and form.validate_on_submit():
        title = form.title.data
        description = form.description.data or None
        category = form.category.data

        db.session.add(CategoryItem(title=title,
                                    description=description,
                                    category_id=category,
                                    created=datetime.now()))
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html', categories=categories,
                           form=form,
                           authenticated=authenticated)


# TODO: Should ideally use PUT verb
@app.route('/catalog/<item>/edit', methods=['GET', 'POST'])
@login_required
def edit_category_item(item):
    """ Edits existing category item """
    authenticated = session.get('access_token') is not None
    categories = Category.query.order_by(Category.id.asc()).all()
    item = CategoryItem.query.filter(CategoryItem.title == item).first()

    if not item:
        return redirect(url_for('index'))

    form = EditForm()
    form.title.default = item.title
    form.description.default = item.description or ''
    form.category.choices = [(category.id, category.name)
                             for category in categories]
    form.category.default = item.category.id

    if request.method == 'PUT' and form.validate_on_submit():
        item.title = form.title.data
        item.description = form.description.data or None
        item.category_id = form.category.data
        category = item.category.name

        db.session.commit()

        return redirect(url_for('get_catalog_items', category=category))

    form.process()

    return render_template('edit.html', title=item.title,
                           categories=categories,
                           form=form,
                           authenticated=authenticated)


# TODO: ideally should be DELETE verb
@app.route('/catalog/<item>/delete', methods=['GET', 'POST'])
@login_required
def delete_category_item(item):
    """ Deletes item from catalog """
    authenticated = session.get('access_token') is not None
    query = CategoryItem.query.filter(CategoryItem.title == item)
    item = query.first()

    if not item:
        return redirect(url_for('index'))

    form = DeleteForm()

    if request.method == 'POST' and form.validate_on_submit():
        query.delete()

        db.session.commit()

        return redirect(url_for('index'))

    return render_template('delete.html', title=item.title,
                           form=form,
                           authenticated=authenticated)


@app.route('/catalog.json')
def display_catalog():
    """ Displays the entire catalog as JSON """
    categories = [dict(id=category.id,
                       name=category.name,
                       items=[item.to_dict()
                              for item in CategoryItem.query
                              .filter(CategoryItem.category_id == category.id)
                              .all()])
                  for category in Category.query
                  .order_by(Category.id.asc())
                  .all()]

    return jsonify(dict(Categories=categories))

# TODO: should be POST
@app.route('/logout', methods=['GET'])
def logout():
    """ Logout """
    authenticated = session.get('access_token') is not None

    if not authenticated:
        return redirect(url_for('index'))

    session.pop('access_token', None)

    return redirect(url_for('index'))


@app.route('/login', methods=['GET'])
def login():
    """ Login """
    authenticated = session.get('access_token') is not None

    if authenticated:
        return redirect(url_for('index'))

    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route(app.config.get('GOOGLE_OAUTH_REDIRECT_URI') or '/oauth2callback')
def authorize():
    """ Authorization callback """
    token = oauth.google.authorize_access_token()

    if token is None:
        return '500: Server-side Error Occured.'

    session['access_token'] = (token['access_token'], '')

    return redirect(url_for('index'))


@app.route('/')
def index():
    """ Main page"""
    authenticated = session.get('access_token') is not None
    categories = [category.name for category in Category.query
                  .order_by(Category.id.asc())
                  .all()]
    latest = [dict(title=item.title,
                   category=item.category.name) for item in CategoryItem.query
              .order_by(CategoryItem.created.desc()).all()]

    return render_template('index.html', categories=categories,
                           items=latest,
                           authenticated=authenticated)
