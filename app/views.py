"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from email.mime import audio
from logging import log

import os
from sqlalchemy import asc
from pickle import FALSE, TRUE
import random, string
from time import sleep
from psycopg2 import IntegrityError
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory,current_app, make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash 
from app.models import UserProfile, Recordings
from .forms import SignUpForm, LoginForm
from mimetypes import guess_extension
from sqlalchemy.exc import  IntegrityError
###
# Routing for your application.
###

@app.route('/home')
@login_required
def home():
    return render_template('home.html', background="homebackground")

    
@app.route('/profile')
@login_required
def profile():
    username = session['username']
    user = db.session.query(UserProfile).filter(UserProfile.username == username).first()
    recordings = db.session.query(Recordings).filter(Recordings.username == username).order_by(asc(Recordings.date)).limit(5).all()
    return render_template('profile.html', user=user, recordings=recordings)

@app.route('/about/')
@login_required
def about():
    return render_template('about.html')

@app.route('/identifier', methods=['POST','GET'])
@login_required
def identifier():
    return render_template('accentpage.html')

@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        print("received")
        if 'audio_file' in request.files:
            file = request.files['audio_file']
            extname = guess_extension(file.mimetype)
            if not extname:
                abort(400)
            print(extname)
            x = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
            session['sessionaudio'] = f'audio_record_{x}{extname}'
            filename = secure_filename(f'audio_record_{x}{extname}')
            dst = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(dst)
            recording = Recordings(session['username'], f'audio_record_{x}{extname}',"JAMAICAN")
            db.session.add(recording)
            db.session.commit()
    # insert your code here
    # session['sessionaudio] is what contains the audio recording reference
    # thinking of creating a function called get file that gets the actual recording if the session variable doesnt do anything
    accent = 'Trinidadian'.upper()
    print(session['sessionaudio'])
    return render_template('results.html', accent=accent)

def convert_files():
    audioFile = 'idk'
    return audioFile

@app.route('/loading',methods=['GET'])
@login_required
def loading():
    return render_template('loading.html')

@app.route('/results', methods=['GET'])
@login_required
def results():
    accent = "Jamaican".upper()
    return render_template('results.html', accent=accent)

@app.route('/', methods=['POST', 'GET'])
def login():
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
        flash('Incorrect Credentials', 'danger')
        return redirect(url_for('login'))  
    return render_template('login.html', form=form, background="homebackground")


@app.route('/signup', methods=['GET','POST'])
def signup():
    form= SignUpForm()
    if request.method=='POST':
        if request.form['password'] == request.form['password_reenter']:
            try:
                person = UserProfile(request.form['fullname'], request.form['username'],request.form['email'],request.form['dateofbirth'],request.form['password'])
                db.session.add(person)
                db.session.commit()
                return redirect(url_for('login'))
            except IntegrityError:
                flash('Username already exists','danger')
    return render_template('signup.html',form=form, background="homebackground")



@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username',None)
    flash('You were logged out', 'success')
    return redirect(url_for('login'))


@app.route('/delete-audio')
def deleteAudio():
    flash('Recording Deleted','success')
    return redirect(url_for('identifier'))

@app.route('/recording/<filename>')
@login_required
def getRecording(filename):
    print(filename)
    root_dir = os.getcwd()
    return send_from_directory(os.path.join(root_dir, app.config['UPLOAD_FOLDER']),  filename)

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
