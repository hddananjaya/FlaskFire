"""Simple module for firebase user auth REST API 
Why?:
  Because pyrebase failed me.  

Methods:
  create_user_with_email_password()
  sign_in_user_with_email_password()
TODO:
  create methods for other functions.
 """

__author__ = "HD Dananjaya"

import requests

def initialize(api_key):
    return (FirebaseUserAuth(api_key))

class FirebaseUserAuth:

    def __init__(self, api_key):
        self.api_key = api_key

    def create_user_with_email_password(self, email, password):
        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser'
        headers = {'Content-Type': 'application/x-www-form-urlencoded',}
        params = {
            'key': self.api_key,
            'email': email,
            'password': password,
            'returnSecureToken': 'true'
        }
        response = requests.post(url, headers=headers, params=params)
        raise_detailed_error(response)
        return (response.json())

    def sign_in_user_with_email_password(self, email, password):
        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword'
        headers = {'Content-Type': 'application/x-www-form-urlencoded',}
        params = {
            'key': self.api_key,
            'email': email,
            'password': password,
            'returnSecureToken': 'true'
        }
        response = requests.post(url, headers=headers, params=params)
        raise_detailed_error(response)
        return (response.json())

# copied this cool func from pyrebase
def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
    except requests.HTTPError as e:
        # raise detailed error message
        raise requests.HTTPError(e, request_object.text)