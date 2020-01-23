from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

import face_recognition
from pprint import pprint

import numpy
import base64
import re
from PIL import Image
from io import BytesIO
import psycopg2
from dotenv import load_dotenv
import os

from datetime import datetime

load_dotenv(dotenv_path="./.env")

try:
  facesdb = psycopg2.connect(dbname=os.getenv('DBNAME'), user=os.getenv('DBUSER'), host=os.getenv('DBHOST'), password=os.getenv('DBPASSWORD'))
  facecursor = facesdb.cursor()
except:
  print("Could not connect to the beholder database")

@dispatcher.add_method
def foobar(**kwargs):
    return kwargs["foo"] + kwargs["bar"]

def store(behold_key, mundane_id, faceimg):
  if (behold_key != os.getenv('BEHOLDKEY')): 
    return {'error':'Insufficient authority.'}
  imgdata = base64.b64decode(re.sub('^data:image/.+;base64,', '', faceimg))
  image = Image.open(BytesIO(imgdata))
  img = numpy.array(image)
  face_encoding = face_recognition.face_encodings(img)[0].tolist()
  
  facecursor.execute("INSERT INTO faces (mundane_id, face) VALUES (%s, %s)", (mundane_id, face_encoding))
  facesdb.commit()
  
  return {'id':mundane_id,'feature':face_encoding}

def lookup(attendanceimg):
  imgdata = base64.b64decode(re.sub('^data:image/.+;base64,', '', attendanceimg))
  image = Image.open(BytesIO(imgdata))
  img = numpy.array(image)
  hits = []
  et1 = datetime.now()
  encodings = face_recognition.face_encodings(img)
  locations = face_recognition.face_locations(img)
  print("Processing time:")
  print(datetime.now() - et1)
  print("\n")
  for face in encodings:
    fe1 = datetime.now()
    face_encoding = face.tolist()
    facecursor.execute("select mundane_id, cube_distance(cube(%s), cube(face)) from faces where cube_distance(cube(%s), cube(face)) < 0.6 order by cube_distance(cube(%s), cube(face)) limit 1", (face_encoding,face_encoding,face_encoding))
    distance = facecursor.fetchone()
    print("Distance measure")
    print(datetime.now() - fe1)
    pprint(distance)
    
    hits.append(distance)
  
  return {'hits':hits,'locations':locations}
  

@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["store"] = store
    dispatcher["lookup"] = lookup

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, application)
