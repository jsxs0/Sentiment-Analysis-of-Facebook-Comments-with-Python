#Download Facebook Comments 
import requests 
import requests 
import pandas as pd
import os, sys

token = ""
try:
    token = os.environ['FB_TOKEN']
except:
    print ("Set FB_TOKEN variable")
    #sys.exit(-1)

fb_pageid = "228735667216"
fb_postid = "10154922624762217"
commentlst = []
datelst = []

url = "https://graph.facebook.com/v2.9/"+ fb_pageid +"_"+ fb_postid +"/comments?limit=100&access_token="+token

while(True):
    posts = requests.get(url)
    posts_json = posts.json()
    for x1 in posts_json['data']:
        commentlst.append(x1.get('message').encode('utf-8').strip())
        datelst.append(x1.get('created_time'))
    next_page = ""
    try:
        next_page = posts_json['paging']['next']
        url = next_page
    except:
        break
    if not next_page: break
    print ("Count: %s,  Next Page: %s" % ( len(commentlst), url))

print ("\nGenerating JSON File")

df = pd.DataFrame({'comment': commentlst, 'dates': datelst})
df['dates'] = pd.to_datetime(df['dates'])
df['day_of_week'] = df['dates'].dt.weekday_name
df['year'] = df['dates'].dt.year
df['month'] = df['dates'].dt.month
df['count'] = 1 

df.to_json('comment_data.json')
#Generate Sentimental Results
import requests 
import json
from google.cloud import language, exceptions

client = language.Client()
# export GOOGLE_APPLICATION_CREDENTIALS environment variable 

with open('comment_data.json') as data_file:
    data = json.load(data_file)

sentiment_list = []
for x1,y1  in data['comment'].items():
    try:
        document = client.document_from_text(y1)
        sentiment = document.analyze_sentiment().sentiment
        sentiment_list.append({"id": x1, "comment": y1, "sentiment_score": sentiment.score, "sentiment_magnitude": sentiment.magnitude })
        print ("Pass")
    except:
        print ("Fail")

with open('sentiment_comments.json', 'w') as outfile:
    json.dump(sentiment_list, outfile)
