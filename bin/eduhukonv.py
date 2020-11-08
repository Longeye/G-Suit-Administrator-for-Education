####################################################################################
# G Suit/Google Workspace domain konverter
#
# Ez a script módosítja az összes felhasználó és csoport levelezési címében
# a "sulinet.hu" stringet "edu.hu"-ra. A régi e-mail címet meghagyja alaias-ként.
#
# Készítette: Venczel József
#
# Debrecen, 2020. 11. 07.
####################################################################################


from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError # Hibakezeléshez a callback függvényhez

import socket

# A ebben található függvények segítségével mérem le, melyik programrész meddig fut
import time

import sys

SCOPES = ['https://www.googleapis.com/auth/admin.directory.user',
          'https://www.googleapis.com/auth/admin.directory.group'
]

print("Kapcsolatfelvétel a szerverrel...")

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

socket.setdefaulttimeout(600)  # legfeljebb 10 percig vár egy kapcsolatra (ez több, mint elég)

serviceAdmin = build('admin', 'directory_v1', credentials=creds)

if serviceAdmin:
    print("Szerverhez kapcsolódva.")
else:
    print("Nem sikerült kapcsolatot létesíteni a szerverrel!")


totalTime=time.time()

print("Felhasználók e-mail címének módosítása")
lista={}
page_token="a"
db=0
while page_token is not None:
    if not lista:
        lista = serviceAdmin.users().list(customer="my_customer", maxResults=30, query="email:teszt*").execute()
    else:
        lista = serviceAdmin.users().list(customer="my_customer", pageToken=page_token, maxResults=30, query="email:teszt*").execute()
    page_token=lista.get("nextPageToken")

    for sor in lista.get("users"):
        email=str(sor.get("primaryEmail"))
        id=str(sor.get("id"))
        if email.find("teszt") == 0:
            primail=email.replace("sulinet", "edu")
            # print(primail)
            tanar = {   "primaryEmail" : primail,
                        "aliases" : [email]
            }
            tanar = serviceAdmin.users().patch(userKey=id, body=tanar).execute()
            print(tanar)
            db+=1
print("\nMódosított e-mail címek száma:", db)
elapsedTime = time.time() - totalTime
print("Ez a programrész %.3fs alatt futott le." % elapsedTime)