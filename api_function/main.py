import base64
import functions_framework
import requests
from os import environ as env
import json
from google.cloud import firestore_v1
from datetime import datetime

def get_data_from_dtdd(dtdd_link):
    movie_id  = dtdd_link.split("/")[-1]
    url = "https://www.doesthedogdie.com/media/{}".format(movie_id)   
    headers = {
      "accept": "application/json",
      "X-API_KEY": env.get("DTDD_API_KEY")
    }
    response = requests.get(url, headers=headers)
    return response

def update_firestore_metadata(response, video_id):
    db = firestore_v1.Client(project='scareflix', database='scareflix-db')
    metadata_col_ref = db.collection(u'dtdd_metadata')
    video_col_ref = db.collection(u'videos')
    
    metadata_dict = {'request_url': response.url, 'ts': datetime.now(), 'data': response.json()}
    update_time, metadata_ref = metadata_col_ref.add(metadata_dict)

    video_ref = video_col_ref.document(video_id)
    video_ref.update({u'dtdd_metadata_id': metadata_ref.id})
    print("Updated firestore metadata {}".format(metadata_ref.id))

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def get_metadata(cloud_event):
    
    event_data = json.loads(base64.b64decode(cloud_event.data["message"]["data"]))

    link=event_data["link"]

    print(get_data_from_dtdd(link).text)
    update_firestore_metadata(get_data_from_dtdd(link), event_data["video_id"])

    