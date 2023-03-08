#!/usr/bin/python3

import requests
import json
import datetime
from vars import *

if __name__ == "__main__":
    out = {}
    print ("Content-Type: application/json\n\n")
    r = requests.get(f"https://www.eventbriteapi.com/v3/organizations/{ORG_ID}/events/?status=live&expand=ticket_availability&token={TOKEN}")
    
    if ((r.status_code >= 200) and (r.status_code <= 299)):
        j = r.json()

        for x in j['events']:
            n = x['name']['text']
            if "MOPA " in n or "Epilog " in n or "Laser" in n:
                t =  (x['start']['local'])
                # 2023-03-19T10:00:00
                d = datetime.datetime.strptime(t,"%Y-%m-%dT%H:%M:%S")
                ds = d.strftime("%A, %B %d, %I:%M %p")
                l =  x['listed']
                s =  x['ticket_availability']['is_sold_out']
                #print (n,t,l,s,d,ds)
                if l:
                    if n not in out:
                        out[n]=[]
                    out[n].append({"when":ds,"sold_out":s})
                #print (json.dumps(x,indent=2))

    print(json.dumps(out,indent=2))
