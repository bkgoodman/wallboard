#!/usr/bin/python3

import requests
import json
import datetime
from vars import *

if __name__ == "__main__":
    out = {}
    print ("Access-Control-Allow-Origin: *")
    print ("Content-Type: text/html\n\n")
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
                    out[n].append({"when":ds,"sold_out":s,"sold_out_text":"<b>Sold Out!</b>" if s else ""})
                #print (json.dumps(x,indent=2))

    print ("""
    	<h2 style="margin:2px;text-align:center;color:#888"> Upcoming Classes</h2>
	<table>
    """)

    for o in out:
        print (f"""
		<tr>
			<th colspan=3>{o}</th>
		</tr>
        """)

        for x in out[o]:
            print (f"""
            <tr>
                <td />
                <td>{x['when']}</td>
                <td>{x['sold_out_text']}</td>
            </tr>
            """)
    print ("""
	</table>
    """)

