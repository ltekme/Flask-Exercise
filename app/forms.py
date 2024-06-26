from collections.abc import Sequence
from flask_wtf import FlaskForm
from flask_babel import gettext

from wtforms import (
    StringField,
    DecimalField,
    PasswordField,
    BooleanField,
    SubmitField,
    DateTimeField,
    ValidationError,
    TextAreaField,
    MultipleFileField,
    EmailField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask_wtf.file import FileAllowed

from .models import User, GalleryPostImage, SecondHandPost
from . import flask_app
import re


def _username_validator(curr_username: str = None, username: str = None):
    if not re.fullmatch(r'\b[A-Za-z0-9._]{3,32}\b', username):
        raise ValidationError(gettext(
            'Username must be between 3 and 24 characters long and contain only letters, numbers, dots and underscores.'))
    if curr_username != username:
        if User.query.filter_by(username=username).first():
            raise ValidationError(
                gettext("Username not avaliable. Please use a different username."))


def _password_validator(password: str):
    conditions = ['Your password must:']
    if len(password) < 8:
        conditions.append('contain at least 8 charactors.')
    if not re.search('[a-z]', password):
        conditions.append('contain at least one lowercase letter.')
    if not re.search('[A-Z]', password):
        conditions.append('contain at least one uppercase letter.')
    if not re.search('[0-9]', password):
        conditions.append('contain at least one number.')
    if len(conditions) > 1:
        raise ValidationError(''.join(conditions))


class LoginForm(FlaskForm):
    username = StringField(gettext("Username or email"),
                           validators=[DataRequired()])
    password = PasswordField(gettext("Password"), validators=[DataRequired()])
    remember_me = BooleanField(gettext("Remember Me"))
    submit = SubmitField(gettext("Sign In"))


class RegisterForm(FlaskForm):
    display_name = StringField(gettext('Display Name'), validators=[
                               Length(max=100, message='Max Allowed leanth is 100 Charactor')])
    username = StringField(gettext("Username"), validators=[DataRequired(), Length(
        max=64, message='Max Allowed leanth is 64 Charactor')])
    email = EmailField(gettext("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(gettext("Password"), validators=[DataRequired()])
    password2 = PasswordField(gettext("Repeat Password"), validators=[
                              DataRequired(), EqualTo("password")])
    submit = SubmitField(gettext("Register"))

    def validate_username(self, username: StringField):
        _username_validator(username=username.data)

    def validate_email(self, email: StringField):
        if User.query.filter_by(username=email.data).first():
            raise ValidationError(gettext("This email is already in use."))

    def validate_password(self, password: StringField):
        if not flask_app.config['IS_DEV_LOCAL']:
            _password_validator(password=password.data)


class EditProfileForm(FlaskForm):
    username = StringField(gettext('Username'))
    display_name = StringField(gettext('Display Name'), validators=[
                               Length(max=100, message='Max Allowed leanth is 100 Charactor')])
    about_me = TextAreaField(gettext('About Me'), validators=[Length(
        max=256, message='Max Allowed leanth is 256 Charactor')])
    submit = SubmitField(gettext('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username: StringField):
        _username_validator(
            curr_username=self.original_username, username=username.data)


class CreatePostForm(FlaskForm):
    title = StringField(gettext('Title'), validators=[Length(min=0, max=128)])
    body = TextAreaField(gettext('Say something to the world'), validators=[
                         DataRequired(), Length(min=0, max=512)])
    submit = SubmitField(gettext('Post'))


class ResetPasswordRequestForm(FlaskForm):
    email = EmailField(gettext("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(gettext("Request Password Reset"))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(gettext("New password"),
                             validators=[DataRequired()])
    password2 = PasswordField(gettext("Repeat new Password"), validators=[
                              DataRequired(), EqualTo("password")])
    submit = SubmitField(gettext("Reset password"))

    def validate_password(self, password: StringField):
        if not flask_app.config['IS_DEV_LOCAL']:
            _password_validator(password=password.data)


# ----------------------------------------------------------------
class CreateGallery(FlaskForm):
    title = StringField(gettext('Title'), validators=[DataRequired(message='A title for your submission is required'), Length(
        max=128, min=1, message='Title must be less then 128 charactor')])
    description = TextAreaField(gettext("Description"), validators=[Length(
        max=512, min=0, message='Title must be less then 512 charactor')])
    images = MultipleFileField(gettext('Select Photos'), validators=[DataRequired(message='You must select at least one image, 10 at once'), FileAllowed(
        flask_app.config['ALLOWED_IMAGE_FORMATS'], message='You can only upload images!')])
    category = StringField(gettext("Category"), validators=[Length(
        max=50, min=0, message='Title must be less then 512 charactor')])
    submit = SubmitField(gettext("Create"))

    def validate_images(self, images: MultipleFileField):
        if len(images.data) > flask_app.config['IMAGE_PER_UPLOAD']:
            raise ValidationError(
                f'You can upload a maximum of {flask_app.config["IMAGE_PER_UPLOAD"]} images at once')

    def validate_category(self, category: StringField):
        if category.data != '':
            if not re.fullmatch(r'\b[A-Za-z0-9._]{3,50}\b', category.data):
                raise ValidationError(gettext(
                    'Category must be between 3 and 50 characters long and contain only letters, numbers, dots and underscores.'))


class EditGallery(FlaskForm):
    title = StringField(gettext('Title'), validators=[DataRequired(message='A title for your submission is required'), Length(
        max=128, min=1, message='Title must be less then 128 charactor')])
    description = TextAreaField(gettext("Description"), validators=[Length(
        max=512, min=0, message='Title must be less then 512 charactor')])
    category = StringField(gettext("Category"), validators=[Length(
        max=50, min=0, message='Title must be less then 512 charactor')])
    submit = SubmitField(gettext("Save Changes"))

    def validate_category(self, category: StringField):
        if category.data != '':
            if not re.fullmatch(r'\b[A-Za-z0-9._]{3,50}\b', category.data):
                raise ValidationError(gettext(
                    'Category must be between 3 and 50 characters long and contain only letters, numbers, dots and underscores.'))


class AddGalleryImages(FlaskForm):
    images = MultipleFileField(gettext('Select Photos'), validators=[FileAllowed(
        flask_app.config['ALLOWED_IMAGE_FORMATS'], message='You can only upload images!')])
    submit = SubmitField(gettext("Add"))

    def validate_images(self, images: MultipleFileField):
        if len(images.data) > flask_app.config['IMAGE_PER_UPLOAD']:
            raise ValidationError(
                f'You can upload a maximum of {flask_app.config["IMAGE_PER_UPLOAD"]} images at once')


class DeleteGalleryImages(FlaskForm):
    filehash = StringField(gettext("Image key of image to delete"))
    submit = SubmitField(gettext("Delete"))

    def __init__(self, post_id: int, *args, **kwargs):
        super(DeleteGalleryImages, self).__init__(*args, **kwargs)
        self.post_id = post_id

    def validate_file_hash(self, filehash: StringField):
        img = GalleryPostImage.query.filter_by(
            object_key=filehash, gallerypost_id=self.post_id).first()
        if not img:
            raise ValidationError("Image key was not found")
        

class DeleteGallery(FlaskForm):
    confirm = StringField(gettext('Please Input "delete me" to delete your post'), validators=[DataRequired(message='Please input "delete me" to confirm delete your post.')])
    submit = SubmitField(gettext("Delete My Post"))

    def validate_confirm(self, confirm: StringField):
        if confirm.data != 'delete me':
            raise ValidationError(gettext('Please input "delete me" to confirm delete your post.'))

# ----------------------------------------------------------------
class CreateSecondHandPost(FlaskForm):
    title = StringField(gettext('Title'), validators=[DataRequired(message='A title for your submission is required'), Length(max=128, min=1, message='Title must be less then 128 charactor')])
    type = StringField(gettext('Type'), validators=[DataRequired(message='Type of product is required')])
    category = StringField(gettext('Category'), validators=[DataRequired(message='Category is required')])
    price = DecimalField(gettext('Product Price'), validators=[DataRequired(message='Price is required')])
    images = MultipleFileField(gettext('Select Photos'), validators=[FileAllowed(['jpg', 'png', 'gif', 'jfif'], message='You can only upload images!')])
    description = TextAreaField(gettext("Description"), validators=[Length(max=512, min=0, message='Description must be less then 512 charactor')])
    submit = SubmitField("Submit")

    def validate_images(self, images: MultipleFileField):
        if len(images.data) > 10:
            raise ValidationError('You can upload a maximum of 10 images')
        
    def validate_price(self, price):
        if price.data < 0:
            raise ValidationError('Invalid price')
        

class EditSecondHandPost(FlaskForm):
    title = StringField(gettext('Title'), validators=[DataRequired(message='Title is required')])
    type = StringField(gettext('Type'), validators=[DataRequired(message='Type is required')])
    category = StringField(gettext('Category'), validators=[DataRequired(message='Category is required')])
    price = DecimalField(gettext('Product Price'), validators=[DataRequired(message='Price is required')])
    description = TextAreaField(gettext("Description"), validators=[Length(max=512, min=0, message='Description must be less then 512 charactor')])
    submit = SubmitField(gettext("Save Changes"))


class DeleteSecondHandPost(FlaskForm):
    confirm = StringField(gettext("Please input 'delete' to delete post"))
    submit = SubmitField(gettext("Delete"))
    
    def validate_confirm(self, confirm: StringField):
        if confirm.data != 'delete':
            raise ValidationError('Please input "delete" to delete post')


# ----------------------------------------------------------------
class TravelBlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=128)])
    content = TextAreaField('Content', validators=[DataRequired()])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(TravelBlogForm, self).__init__(*args, **kwargs)

        if not self.title.data or not self.content.data or not self.country.data or not self.city.data:
            self.title.data = ''
            self.content.data = ''
            self.country.data = ''
            self.city.data = ''

# ----------------------------------------------------------------