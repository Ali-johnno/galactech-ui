"""
Project: Capstone Group Work
Company: Galactech
System: Accent Identification System

Group Members:
* Kalia-Lee Rodney
* Alexandria Burnett
* Aaliyah Johnston
* Jamar Lee
"""
from email.mime import audio
from logging import log
from dataprocess import AudioPreProc
import numpy as np

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



### User credentials checked and they are allowed access into the system
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
            return redirect(url_for('home'))  # if login is successful user is redirected to home page
        flash('Incorrect Credentials', 'danger')
        return redirect(url_for('login'))  #if login is unsuccessful they are redirected to the login page
    return render_template('login.html', form=form, background="homebackground")


### user enters their credentials that is stored in POSTGRESQL
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
            except IntegrityError: #catches "username already exists" error from database - as usernames must be unique
                flash('Username already exists','danger')
    return render_template('signup.html',form=form, background="homebackground")


### logs the user out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username',None)
    flash('You were logged out', 'success')
    return redirect(url_for('login'))

### displays the home page
@app.route('/home')
@login_required
def home():
    return render_template('home.html', background="homebackground")

    
### Displays user information as well as the last 5 recordings they submitted
@app.route('/profile')
@login_required
def profile():
    username = session['username']
    user = db.session.query(UserProfile).filter(UserProfile.username == username).first() #gets User Details
    recordings = db.session.query(Recordings).filter(Recordings.username == username).order_by(asc(Recordings.date)).all()[-5:] #shows the last 5 recordings in a database for a specific user
    return render_template('profile.html', user=user, recordings=recordings)


### Gets a recording from the uploads folder
@app.route('/recording/<filename>')
@login_required
def getRecording(filename):
    print(filename)
    root_dir = os.getcwd()
    return send_from_directory(os.path.join(root_dir, app.config['UPLOAD_FOLDER']),  filename)


### displays information about the software and the team members
@app.route('/about/')
@login_required
def about():
    return render_template('about.html')


### interface for the accent identification system
@app.route('/identifier', methods=['POST','GET'])
@login_required
def identifier():
    return render_template('accentpage.html')


### deletes an uploaded audio file or live recording
@app.route('/delete-audio')
def deleteAudio():
    flash('Recording Deleted','success')
    return redirect(url_for('identifier'))

### uploads the uploaded or live recording to the database. accepts audio from ajax post request
### see app.js
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
            print(x)
            filename = secure_filename(f'audio_record_{x}{extname}')
            dst = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            recording = Recordings(session['username'],f'audio_record_{x}{extname}',"")
            db.session.add(recording)
            db.session.commit()
            file.save(dst)
    return render_template('accentpage.html')


### preprocessor
def single_file_preprocessing(sample_data):
  (aud,sr) = AudioPreProc.open(sample_data)   
  tot = AudioPreProc.rechannel((aud,sr), 1)
  tot=AudioPreProc.pad_trunc(tot,12000)            
  mfcc,hop=AudioPreProc.get_mfccs(tot)
  
  f0=AudioPreProc.get_fundamental_freq(tot,hop)
  f0=f0.reshape((1,f0.shape[0]))
  energy=AudioPreProc.get_energy(tot,hop)
  fin=np.concatenate([mfcc,f0,energy])
  return fin


### loading page
@app.route('/loading',methods=['GET'])
@login_required
def loading():
    return render_template('loading.html')


### results page showing accent prediction
@app.route('/results', methods=['GET'])
@login_required
def results():
    # prediction code here
    root_dir = os.getcwd()
    last_rec = db.session.query(Recordings).order_by(Recordings.id)[-1]
    audio =  os.path.join(root_dir, app.config['UPLOAD_FOLDER'],  last_rec.recording)
    fin=single_file_preprocessing(audio)
    print("predicting value")
    argmax,percentages=app.config['RNNT'].predict_val(np.reshape(fin,(1,15,1198)),1)
    if argmax[0]==1:
        accent='Trinidadian'.upper()
    else:
        accent = 'Jamaican'.upper()
    last_rec.accent = accent
    db.session.commit()
    return render_template('results.html', accent=accent)


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
