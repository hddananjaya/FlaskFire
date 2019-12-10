# imports for flask
from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify

# imports for firebase
from firebase_admin import credentials, firestore, auth
import firebase_admin

# custom lib
import firebase_user_auth

# realtime communication
from flask_socketio import SocketIO, emit, send

# trying to implement session variable access
from flask import stream_with_context, Response

import requests
import datetime
import random

app = Flask(__name__)
app.secret_key = b'\xbd\x93K)\xd3\xeeE_\xfb0\xa6\xab\xa5\xa9\x1a\t'
socketio = SocketIO(app, cors_allowed_origins="*")

# add your config
WEB_API_KEY = ""
SERVER_CONFIG = {

}

# firebase-admin init
cred = credentials.Certificate(SERVER_CONFIG)
default_app = firebase_admin.initialize_app(cred)
# firestore db reference
db = firestore.client()
# users collection reference
users_coll = db.collection(u"users")

# notes collection reference
chats_coll = db.collection(u"notes")

# firebase user auth init
user_auth = firebase_user_auth.initialize(WEB_API_KEY)

# this might be stupid. i dont know
# this is how i keep track of all using chats
#chats = {}

# after backup
# lets try to implement using sessions baby.

#return Response(stream_with_context(get_user_saved_tracks(session['token'], session['spotify_id'], session),
#               mimetype='text/event-stream')

def testx():
    session["chats"][doc_snapshot[0].id] = True

def _on_snapshot_callback(doc_snapshot, changes, readtime):
    #session["chats"][doc_snapshot[0].id] = True
    return Response(testx(), mimetype="text/event-stream")

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
            session['email_addr'] = decoded_clamis['email']
            return render_template("index.html")
        except Exception as e:
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

@app.route("/chat/<chatid>")
def user_chat(chatid):
    """
    ToDo:
        * implement chat system somehow
    """
    chat_doc = chats_coll.document(chatid)
    chat_details = chat_doc.get().to_dict()
    #return (jsonify(chat_details))
	
	# if user is not already joined then append him
    if (session["email_addr"] not in chat_details.get("users")):
        chat_details.get("users").append(session["email_addr"])
        chat_doc.update(chat_details, option=None)

    if (chatid not in session["chats"]):
        chat_watch = chat_doc.on_snapshot(_on_snapshot_callback)
        session["chat"][chatid] = False		
	
    # Watch the chat document if it is not waching
    #if (chatid not in chats):
	#    chat_watch = chat_doc.on_snapshot(_on_snapshot_callback)
	#    chats[chatid] = False	

    return (render_template("chat.html", users_list=chat_details.get("users"), logged_user=session["email_addr"], chatid=chatid))
	
@app.route("/new-chat")
def new_chat():
    return (render_template("new-note.html"))


@app.route("/new-chat/create")
def create_new_chat():
    try:
        cid = str(random.random())[2:] + str(random.randint(1241, 4124))
        chats_coll.add({"nid": cid,
                        "users": [session["email_addr"]],
						"chat": ""
        }, cid)
        return (redirect("/chat/{}".format(cid)))
    except:
	    return ("There is an error. Please try again.")
	

# get chatid and return chat_detail
@app.route("/chat/getinfo/<chatid>")
def get_chat_info(chatid):
    if (session["chats"][chatid]):
        cht_info = chats_coll.document(chatid)
        session["chats"][chatid] = False	
        return (jsonify(cht_info.get().to_dict()))
    return (jsonify(None))


@app.route("/chat/add/<chatid>/<message>")
def add_chat(chatid, message):
    chat_doc = chats_coll.document(chatid)
    chat_details = chat_doc.get().to_dict()
	
    chat_details["chat"] += "\n[{}] : {}".format(session["email_addr"].split("@")[0], message)
    chat_doc.update(chat_details, option=None)
	
    # need to handle errors but for now
    return (jsonify({}))


"""
# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(u'Received document snapshot: {}'.format(doc.id))

doc_ref = db.collection(u'cities').document(u'SF')

# Watch the document
doc_watch = doc_ref.on_snapshot(on_snapshot)

"""

"""
solution for resolve out of context
https://stackoverflow.com/questions/51170784/setting-flask-session-variable-outside-request-context-inside-a-generator

from flask import Flask, stream_with_context, request, Response, session
....

return Response(stream_with_context(get_user_saved_tracks(session['token'], session['spotify_id'], session),
                mimetype='text/event-stream')


"""




if (__name__ == "__main__"):
    #app.run(debug=True)
	socketio.run(app, debug=True)

