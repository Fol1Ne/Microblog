from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_responce(status_code, message=None):
    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}
    if message:
        payload["message"] = message
    responce = jsonify(payload)
    responce.status_code = status_code
    return responce

def bad_request(message):
    return error_responce(400, message)