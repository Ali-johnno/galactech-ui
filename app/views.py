"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from logging import log

import os
import random, string
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory,current_app, make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash 
from app.models import UserProfile
from .forms import SignUpForm, UploadForm, LoginForm
from mimetypes import guess_extension
###
# Routing for your application.
###

@app.route('/home')
def home():
    return render_template('home.html', background="homebackground")


@app.route('/testing')
def testing():
    return render_template('testing.html')

    
@app.route('/profile')
def profile():
    username = session['username']
    user = db.session.query(UserProfile).filter(UserProfile.username == username).first()
    # flash(user.password)
    password = user.password
    return render_template('profile.html', user=user, password=password)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/identifier', methods=['POST','GET'])
def identifier():
    form = UploadForm()
    return render_template('accentpage.html', form=form)

@app.route('/upload', methods=['POST', 'GET'])
def upload():

  
    if request.method == 'POST':
        if 'audio_file' in request.files:
            file = request.files['audio_file']
            extname = guess_extension(file.mimetype)
            if not extname:
                abort(400)
            x = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
            filename = secure_filename(f'audio_record_{x}{extname}')
            dst = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(dst)

        

    return render_template('accentpage.html')



# def get_uploaded_images():
#     rootdir = os.getcwd()
#     photo_files = []
#     for subdir, dirs, files in os.walk(rootdir + '/uploads'):
#         for file in files:
#             photo_files.append(file)
#     return photo_files

# @app.route('/uploads/<filename>')
# def get_image(filename):
#     root_dir = os.getcwd()
#     return send_from_directory(os.path.join(root_dir, app.config['UPLOAD_FOLDER']), filename)


@app.route('/files')
def files():
    if not session.get('logged_in'):
        abort(401)
    return render_template('files.html',images=get_uploaded_images())

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    form= LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']    
        user = db.session.query(UserProfile).filter(UserProfile.username == username).first()
        if user is not None and check_password_hash(user.password, password):
            login_user(user)   
            flash('Successfully Logged in','success')
            session['username'] = username
            return redirect(url_for('home'))  # they should be redirected to a secure-page route instead
        flash("Incorrect Credentials")
        return render_template("login.html", form=form, background="homebackground")  
    return render_template('login.html', form=form, background="homebackground")

@app.route('/', methods=['GET','POST'])
def signup():
    form= SignUpForm()
    if request.method=='POST':
        if request.form['password'] == request.form['password_reenter']:
            person = UserProfile(request.form['fullname'], request.form['username'],request.form['email'],request.form['dateofbirth'],request.form['password'])
            db.session.add(person)
            db.session.commit()
    return render_template('signup.html',form=form, background="homebackground")



@app.route('/logout')
def logout():
    logout_user()
    session.pop('username',None)
    flash('You were logged out', 'success')
    return redirect(url_for('login'))


@app.route('/delete-audio')
def deleteAudio():
    return redirect(url_for('identifier'))
###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
