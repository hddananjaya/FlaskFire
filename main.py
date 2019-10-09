import requests
import datetime

# imports for flask
from flask import Flask, render_template, request, url_for, redirect, flash, session

# imports for firebase
from firebase_admin import credentials, firestore, auth
import firebase_admin

import firebase_user_auth

app = Flask(__name__)
app.secret_key = b'\xbd\x93K)\xd3\xeeE_\xfb0\xab\xa5\xa9\x1a\t'

WEB_API_KEY = "###"
SERVER_CONFIG = {
    #
    #
    #
}

# firebase-admin init
cred = credentials.Certificate(SERVER_CONFIG)
default_app = firebase_admin.initialize_app(cred)
# firestore db reference
db = firestore.client()
# users collection reference
users_coll = db.collection(u"users")

# firebase user auth init
user_auth = firebase_user_auth.initialize(WEB_API_KEY)

@app.route('/')
def index_page():
    flash_msg = None
    if ("session_id" in session):
        try:
            # verify session_id
            decoded_clamis = auth.verify_session_cookie(session["session_id"])
            # decoded_token = auth.verify_id_token(session["id_token"])
            flash_msg = "Welcome!, " + decoded_clamis['email'] 
            flash(flash_msg)
            return render_template("index.html")
        except Exception:
            # if unable to verify session_id for any reason
            # maybe invalid or expired, redirect to login
            flash_msg = "Your session is expired!"
            flash(flash_msg)
            return redirect(url_for("user_login"))   

    flash_msg = "Please Log In"
    flash(flash_msg)
    return redirect(url_for("user_login"))    

@app.route('/login', methods=["GET","POST"])
def user_login():
    if (request.method == "POST"):
        user_email = request.form['userEmail']
        user_password = request.form['userPassword']
        flash_msg = None
        try:
            user_recode = user_auth.sign_in_user_with_email_password(user_email, user_password)
            # get idToken
            user_id_token = user_recode.get('idToken')
            # get a session cookie using id token and set it in sessions
            # this will automatically create secure cookies under the hood
            user_session_cookie = auth.create_session_cookie(user_id_token, expires_in=datetime.timedelta(days=14))           
            session['session_id'] = user_session_cookie
            # if username passwd valid then redirect to index page
            return redirect(url_for('index_page'))
        except requests.HTTPError as e:
            if ("EMAIL_NOT_FOUND" in str(e)):
                flash_msg = "Please register before login"
            elif ("INVALID_EMAIL" in str(e)):
                flash_msg = "Please enter a valid email address"
            elif ("INVALID_PASSWORD" in str(e)):
                flash_msg = "Email or Password is wrong"
            else:
                flash_msg = "Something is wrong!!"
        flash(flash_msg)
    # return login page for GET request
    return render_template("login.html")
    

@app.route('/register', methods=["GET", "POST"])
def user_register():
    if (request.method == "POST"):
        user_name = request.form['userName']
        user_email = request.form['userEmail']
        user_password = request.form['userPassword']
        flash_msg = None
        try:
            user_recode = user_auth.create_user_with_email_password(user_email, user_password)
            # get idToken
            user_id_token = user_recode.get('idToken')
            # get a session cookie using id token and set it in sessions
            # this will automatically create secure cookies under the hood
            user_session_cookie = auth.create_session_cookie(user_id_token, expires_in=datetime.timedelta(days=14))           
            session['session_id'] = user_session_cookie

            # add user document to users collection
            users_coll.add({"name": user_name,
                            "email": user_email
            }, user_recode.get('localId'))
            
            # if registration is valid then redirect to index page
            return redirect(url_for('index_page'))
        except requests.HTTPError as e:
            if ("EMAIL_EXISTS" in str(e)):
                flash_msg = "You have already registerd! Please log in."
            elif ("INVALID_EMAIL" in str(e)):
                flash_msg = "Please enter a valid email address"
            elif ("WEAK_PASSWORD" in str(e)):
                flash_msg = "Please use a strong password"
            else:
                flash_msg = "Something is wrong!!"                
            flash(flash_msg)
    # return to login page for GET
    return redirect(url_for('user_login'))

@app.route('/logout')
def user_logout():
    session.pop('session_id', None)
    return redirect(url_for('index_page'))



if (__name__ == "__main__"):
    app.run(debug=True)


