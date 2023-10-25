from app import create_app
from flask_babel import _
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import json, requests

def translate(text, source_language, dest_language):
    url = "https://fasttranslator.herokuapp.com/api/v1/text/to/text"
    try:
        import certifi, ssl

        params = {"lang": f"{source_language}-{dest_language}",
                  "as": "json", "source": text}
        resp = requests.post(url, params=params)
    except requests.exceptions.RequestException as err:
        print(f"translate({text}, {source_language}, {dest_language}): {err}")
    else:
        print(resp)
        print(params)
        if resp.status_code != 200:
            if "application/json" in resp.headers.get("Content-Type"):
                return _("Ошибка: сбой службы перевода")
            else:
                return resp.status_code
        else:
            if params["as"] == "json":
                data = resp.json()
                status = data["status"]
                if status == 200:
                    return data["data"]
                else:
                    return data["message"]
            else:
                return resp.text

def get_language_by_text(text):
    try:
        language = detect(text)
    except LangDetectException:
        return ""
    if language == "UNKNOWN" or len(language) > 5:
        language = ""
    return language