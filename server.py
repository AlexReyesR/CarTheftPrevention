# Imports generales
import os
import sys
#import csv
import json
import urllib
import requests
import socketserver
from datetime import datetime,date

# Imports para hacer HTTP Request
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler

from twilio.rest import Client

# Initial configuration for sending sms (sid, token and sending number from Alex' account)
account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)

message_body = "ALERTA! SU CARRO PUEDE ESTAR EN PELIGRO!"
sending_number = ""
destination_number = ""

#timeSpan = ["id", datetime.time(datetime.now()), datetime.time(datetime.now())]
last_cam = ["id"]
last_detection = [datetime.time(datetime.now())]
last_sms = [datetime.time(datetime.now())]

detection_delta = 10
sms_delta = 10

def parsey(c):
    x = c.decode().split("&")
    d = json.loads(x[0])
    return d


class Handler(BaseHTTPRequestHandler):
    # POST
    def do_POST(self):
        # Obtien informacion para hacer el POST
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        d = post_data#parsey(post_data)

        # Se manda la respuesta de que llego correctamente la respuesta
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><head><title>RECEIVED</title></head></html>")

        d = str(d)
        
        splitted_data = d.split("&")
        label_id = splitted_data[1]
        label_id = label_id[6:]
        cam_id = splitted_data[2]
        cam_id = cam_id[7:]
        cam_id = cam_id[:-1]

        print("Detection on " + str(cam_id))
        
        local_time = datetime.time(datetime.now())

        if (cam_id != last_cam[0]):
            #print(label_id)
            #print(cam_id)
            detection_delta = (datetime.combine(date.today(), local_time) - datetime.combine(date.today(),last_detection[0])).total_seconds()
            sms_delta = (datetime.combine(date.today(), local_time) - datetime.combine(date.today(),last_sms[0])).total_seconds()

            """
            print("=========================================\n=========================================\n=========================================")
            print("Detection delta: " + str(detection_delta))
            print("Sms delta: " + str(sms_delta))
            print("=========================================\n=========================================\n=========================================")
            """

            if (detection_delta < 5) and (sms_delta > 15):
                print("\t === SECURITY ALERT: YOUR CAR MIGHT IN DANGER ===")
                
                message = client.messages \
                .create(
                    body = message_body,
                    from_= sending_number,
                    #media_url=['https://i.kym-cdn.com/entries/icons/original/000/027/100/_103330503_musk3.jpg'],
                    to = destination_number
                )
                
                if (message.status != "queued"):
                    print("Error sending SMS")
                else:
                    print("\tSMS sent to " + destination_number)

                
                last_sms[0] = local_time
            last_cam[0] = cam_id
        last_detection[0] = local_time
    
    # Get
    def do_GET(self):
        # Obtien informacion para hacer el POST
        print(self.headers)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        d = post_data#parsey(post_data)
        try:
            print("Getting environment variables")
        except:
            print("Failed to get environment variables")
      
        print(str(d))
        # Se manda la respuesta de que llego correctamente la respuesta
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><head><title>OK</title></head></html>")


def run():
    print('starting server...')
    #my_ip = requests.get('http://ip.42.pl/raw').text
    server_address = ("", 80)

    httpd = HTTPServer(server_address, Handler)

    # httpd=socketserver.TCPServer(server_address,SimpleHTTPRequestHandler)
    print('running server...')
    httpd.serve_forever()


try:
    # Arranca el servidor
    run()

except KeyboardInterrupt:
    sys.exit(0)