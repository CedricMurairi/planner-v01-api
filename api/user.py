from flask import Blueprint, request, abort

user = Blueprint('user', __name__)

@user.route('/users')
def login():

    # if not response.json():
    #     abort(400)

    return {"users": "I am the user"}