# Flask-Exercise

reference: https://www.youtube.com/playlist?list=PLtgJR0xD2TPeVeq6azvnKXYSeYHFzGaMi

## Babel command for creating translations

creating translations

```
pybabel extract -F babel.cfg -k lazy_gettext -o app/translations/messages.pot .
pybabel init -i app/translations/messages.pot -d app/translations -l zh
```

complie and update

```
pybabel compile -d app/translations
pybabel update -i app/translations/messages.pot -d app/translations

```

## Database initialisation

in the flakenv, there is a default uri configured to a docker container running postgres defined in `.devcontainer/*`. to init the database execute the following commands

```
flask db init
flask db migrate
flask db upgrade
```

## Labs

7. Error Handeling
8. Followers
9. Home page posts pagination
10. email
11. bootstrap
12. date and times
13. lang translations

# Running the application in codespace or devcontainer

0.  create virtual enviroment

```
python -m venv venv
source ./venv/bin/activate
pip install -U -r requirements.txt
```

1. create .flaskenv

```
.flaskenv.template to .flaskenv
change config as needed
contents in .template is set up for development in codespace and devcontainer
```

2. comple babel translations, see above
3. initialise database, see above
4. test data init, the following script will create 5 users with 5 posts for each users

```
python data_init.py
```

see contents of data_init.py for details

5. Update Service account info on .flaskenv
    1. put the content of your service account json file into the `service_account.json`
    2. this file is not tracked by git
    3. replace the `GOOGLE_STORAGE_BUCKET` paramater value with the one you have or a name for the bucket that will store images uploaded.
    4. flask execure, the script will ceate the bucket if it doesn't exists and enable public access to the bucket. 

7. execute

```
python app.py
```

# Extra notes

For dev purpous use

```
sqlite:////workspaces/Flask-Exercise/app/app.db
```

on SQLALCHEMY_DATABASE_URI in .flaskenv. Both of these files are untracked, when the database got messed up and for some reason you need to delete the database, you can simply delete this file instead of the db running in codespace
<hr>
Remove the SERVER_NAME param in .flaskenv when using codespace broswer, otherwise, all page will return error 404, unless you are hosting in local or using codespace in local vscode
