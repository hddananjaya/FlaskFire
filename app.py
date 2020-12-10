# imports for flask
from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify

# imports for firebase
from firebase_admin import credentials, firestore, auth
import firebase_admin

# custom lib
import firebase_user_auth

# realtime communication
from flask_socketio import SocketIO, emit, send

import requests
import datetime
import random

from dotenv import load_dotenv
import os
import uuid
from random_username.generate import generate_username
load_dotenv()

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins="*")

# firebase-admin init
cred = credentials.Certificate(os.path.join(__location__, 'firebase-config.json'))
default_app = firebase_admin.initialize_app(cred)
# firestore db reference
db = firestore.client()
# users collection reference
users_coll = db.collection(u"users")

# notes collection reference
chats_coll = db.collection(u"notes")

# firebase user auth init
user_auth = firebase_user_auth.initialize(os.getenv("WEB_API_KEY"))

@app.route('/')
def index_page():
    flash_msg = None
    if ("session_id" in session):
        try:
            # verify session_id
            decoded_clamis = auth.verify_session_cookie(session["session_id"])   
            #flash(decoded_clamis)
            session['email_addr'] = decoded_clamis['email']
            session['user_id'] = decoded_clamis['user_id']
            #
            # Trying to implement users connected chats list
            #
            user_doc = users_coll.document(decoded_clamis['user_id'])
            user_details = user_doc.get().to_dict()
            connected_chats = user_details.get("connected_chats")
            #flash(decoded_clamis)
            connected_chats_list = []
            for i in connected_chats:
                connected_chats_list.append(i.get().to_dict())
            return render_template("index.html", user_name=user_details.get('name'), chats_list=connected_chats_list[::-1])
        except Exception as e:
            # if unable to verify session_id for any reason
            # maybe invalid or expired, redirect to login
            flash_msg = "Your session is expired!"
            flash(flash_msg)
            return redirect(url_for("user_login"))   
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
    flash_msg = None
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
                            "email": user_email,
                            "connected_chats": []
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
    #session.pop('session_id', None)
    session.clear()
    return redirect(url_for('index_page'))

@app.route("/chat/<chatid>")
def user_chat(chatid):
    try:
        chat_doc = chats_coll.document(chatid)
        chat_details = chat_doc.get().to_dict()

        # if user is not already joined then append him to users list
        if (session["email_addr"] not in chat_details.get("users")):
            chat_details.get("users").append(session["email_addr"])
            chat_doc.update(chat_details, option=None)

            # then append chat_doc to user's connected chats
            user_doc = users_coll.document(session['user_id'])
            user_details = user_doc.get().to_dict()
            user_details.get("connected_chats").append(chat_doc)
            user_doc.update(user_details, option=None)
        return (render_template("chat.html", users_list=chat_details.get("users"), logged_user=session["email_addr"], chatid=chatid))
    except:
        return (redirect(url_for('user_login')))

@app.route("/new-chat")
def new_chat():
    return (render_template("new-note.html"))

@app.route("/chat/create")
def create_new_chat():
    try:
        id = str(uuid.uuid4())
        name = generate_username(1)[0]
        chats_coll.add({
            "nid": id,
            "users": [],
            "chat": "",
            "name": name,
        }, id)
        return (redirect("/chat/{}".format(id)))
    except:
	    return ("There is an error. Please try again.")
	

# get chatid and return chat_detail
@app.route("/chat/getinfo/<chatid>")
def get_chat_info(chatid):
    cht_info = chats_coll.document(chatid)
    return (jsonify(cht_info.get().to_dict()))


@app.route("/chat/add/<chatid>", methods=["POST"])
def add_chat(chatid):
    message = request.get_json().get("message")
    chat_doc = chats_coll.document(chatid)
    chat_details = chat_doc.get().to_dict()
    chat_details["chat"] += "\n[{}] : {}".format(session.get("email_addr").split("@")[0], message)
    chat_doc.update(chat_details, option=None)

    # need to handle errors but for now
    return (jsonify({}))

@app.route("/chat/leave/<chatid>")
def leave_chat(chatid):
    try:
        chat_doc = chats_coll.document(chatid)
        chat_details = chat_doc.get().to_dict()
        chat_details.get("users").remove(session.get("email_addr"))
        chat_doc.update(chat_details, option=None)

        user_doc = users_coll.document(session["user_id"])
        user_details = user_doc.get().to_dict()
        user_details.get("connected_chats").remove(chat_doc)
        user_doc.update(user_details, option=None) 
        return redirect(url_for("index_page"))   
    except Exception as e:
        return (str(e))

@socketio.on('messageHandler')
def handle_message(transfer_obj):
    if ("session_id" in session):
        try:
            decoded_clamis = auth.verify_session_cookie(session["session_id"])   
            email = decoded_clamis['email']
            chat_id = transfer_obj.get("chatId")
            message = transfer_obj.get("message")
            socketio.emit(chat_id, {
                "message": '[{}]: {}'.format(email.split('@')[0], message)
            })
        except:
            pass
if (__name__ == "__main__"):
	socketio.run(app, debug=bool(os.getenv("DEBUG")), host='0.0.0.0', port=8080)

