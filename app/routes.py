from flask import render_template, flash, redirect, url_for, request, abort, g
from flask_login import login_user, current_user, login_required, logout_user
from flask_babel import _, get_locale
from . import flask_app, db, forms
from .models import User, Post, PasswordResetTokens
from .email import send_password_reset_email

from urllib.parse import urlparse
from datetime import datetime as dt


@flask_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_seen()
    g.locale = str(get_locale())


def _get_next_url_from_request(request):
    next_url = request.args.get('next', None)
    if not next_url or urlparse(next_url).netloc != urlparse(request.url).netloc:
        if request.referrer != request.url:
            return request.referrer or url_for('index')
        else:
            return url_for('index')
    return next_url


@flask_app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('explore'))
    
    form = forms.CreatePostForm()
    if current_user.is_authenticated and form.validate_on_submit():
        post = Post(
            title = form.title.data,
            body = form.body.data,
            author = current_user)
        post.create()
        flash(_('Your post is live'))

    page = request.args.get("page", 1, type=int)
    posts = current_user.followed_posts().paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('index', page=posts.prev_num) if posts.prev_num else None

    return render_template("index.html.j2", title="Home", form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, home=True)


@flask_app.route('/explore')
def explore():

    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.prev_num else None

    return render_template("index.html.j2", title="Explore", posts=posts.items, next_url=next_url, prev_url=prev_url)


@flask_app.route("/login", methods=['GET', 'POST'])
def login():

    next_url = _get_next_url_from_request(request)
    if current_user.is_authenticated:
        return redirect(next_url)

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(db.or_(User.email == form.username.data, User.username == form.username.data)).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(_('Welcome Back!'))
            return redirect(url_for('index'))
        else:
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        
    return render_template('user/login.html.j2', title="Sign In", form=form)


@flask_app.route('/register', methods=['GET','POST'])
def register():

    next_url = _get_next_url_from_request(request)
    if current_user.is_authenticated:
        return redirect(next_url)

    form = forms.RegisterForm()
    if form.validate_on_submit():

        user = User(username=form.username.data,
                    email=form.email.data,
                    display_name=form.display_name.data)
        user.set_password(form.password.data)
        user.create()

        flash(_('You are now a registered'))
        return redirect(url_for('login'))

    return render_template('user/register.html.j2', title='Register', form=form)


@flask_app.route('/logout')
@login_required
def logout():

    next_url = _get_next_url_from_request(request)

    logout_user()

    flash(_('You have been logged out'))
    return redirect(next_url)


@flask_app.route('/user/<username>')
def profile(username):

    user = User.query.filter_by(username=username).first_or_404()
    title = _('User  %(dn)s', dn=user.display_name) if user else _('Not Found')

    page = request.args.get("page", 1, type=int)
    posts = Post.query.filter_by(author = user).order_by(Post.timestamp.desc()).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('profile', page=posts.next_num, username=username) if posts.next_num else None
    prev_url = url_for('profile', page=posts.prev_num, username=username) if posts.prev_num else None

    return render_template('user/profile.html.j2', user=user, posts=posts, title=title, next_url=next_url, prev_url=prev_url)


@flask_app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = forms.EditProfileForm(original_username=current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.display_name = form.display_name.data
        current_user.about_me = form.about_me.data
        
        db.session.commit()

        flash(_('Your changes have been saved.'))
        return redirect(url_for('profile', username=current_user.username))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.display_name.data = current_user.display_name
        form.about_me.data = current_user.about_me

    return render_template('user/edit_profile.html.j2', title='Edit Profile', form=form)


@flask_app.route("/reset_password", methods=['GET', 'POST'])
def reset_password_request():
    
    next_url = _get_next_url_from_request(request)

    if current_user.is_authenticated:
        return redirect(next_url)
    
    form = forms.ResetPasswordRequestForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)

        flash(_('An email will be sent to you shortly if the email is found in our records'))
        return redirect(url_for('login'))
    
    return render_template('user/reset_password.html.j2', title="Reset Password", form=form)


@flask_app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token: str):

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if not PasswordResetTokens.validate(token=token):
        return abort(403, description=_("Invalid access token"))
    
    form = forms.ResetPasswordForm()
    if form.validate_on_submit():

        user = PasswordResetTokens.use(token=token)
        if not user:
            flash(_('Invalid or expired token'))
            return redirect(url_for('login'))

        user.set_password(form.password.data)
        db.session.commit()

        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    
    return render_template('user/reset_password.html.j2', title="Reset Password", form=form)


@flask_app.route('/follow/<username>')
@login_required
def follow(username: str):

    current_user_profile = redirect(url_for('profile', username=current_user.username))
    user = User.query.filter_by(username = username).first()

    if not user:
        flash(_('user %(u)s was not found', u=username))
        return current_user_profile
    if user == current_user:
        flash(_('You cannot follow yourself'))
        return current_user_profile
    
    resault = current_user.follow(user)
    if resault:
        flash(_('You are now following %(dn)s', dn=user.display_name))
    else:
        flash(_('You are already following %(dn)s or something went wrong.', dn=user.display_name))

    return redirect(url_for('profile', username=user.username))


@flask_app.route('/unfollow/<username>')
@login_required
def unfollow(username: str):

    current_user_profile = redirect(url_for('profile', username=current_user.username))
    user = User.query.filter_by(username = username).first()

    if not user:
        flash(_('user %(n)s was not found', n=username))
        return current_user_profile
    if user == current_user:
        flash(_('You cannot unfollow yourself'))
        return current_user_profile
    
    resault = current_user.unfollow(user)
    if resault:
        flash(_('You are no longer following %(a)s', a=user.display_name))
    else:
        flash(_('You are not following %(a)s or something went wrong.', a=user.display_name))

    return redirect(url_for('profile', username=user.username))