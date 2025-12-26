#!/usr/bin/python3
#import ConfigParser
import icalendar,sys,os,datetime
import stripe
import pytz
import urllib
import json
import html
import recurring_ical_events
from dateutil import tz
from vars import ICALS


# Parameters({'CUTYPE': 'RESOURCE', 'ROLE': 'REQ-PARTICIPANT', 'PARTSTAT': 'ACCEPTED', 'CN': 'MiL-1-Center-Laser room - MOPA (2)', 'X-NUM-GUESTS': '0'})

EPILOG_ID="mailto:makeitlabs.com_3133373236393938363631@resource.calendar.google.com"
MOPA_ID="mailto:c_1886b6dkec306jdkk38lsbpbejeo8@resource.calendar.google.com"


def utctolocal(dt,endofdate=False):
  from_zone = tz.gettz('UTC')
  to_zone = tz.gettz('America/New_York')

  if isinstance(dt,datetime.datetime): 
    #dt = dt.replace(tzinfo=from_zone)
    dt = dt.astimezone(to_zone)
  else:
    if endofdate:
      dt = datetime.datetime.combine(dt,datetime.time(hour=23,minute=59,second=59,tzinfo=to_zone))
    else:
      dt = datetime.datetime.combine(dt,datetime.time(tzinfo=to_zone))
  return dt

weekday=['Sun','Mon','Tues','Wed','Thurs','Fri','Sat'] # OUR Sunday=0 Convention!!
def get_calendar(cal_url,device,rundate=None):
  #ICAL_URL = Config.get('autoplot','ICAL_URI')
  g = urllib.request.urlopen(cal_url)
  data=  g.read()
  #print(data)
  cal = icalendar.Calendar.from_ical(data)
  g.close()

  """
  g = urllib.urlopen(ICAL_URL)
  print g.read()
  g.close()
  """

  if rundate is not None:
    now = datetime.datetime.strptime(rundate,"%Y-%m-%d").replace(tzinfo=tz.gettz('America/New York'))
  else:
    now = datetime.datetime.now().replace(tzinfo=tz.gettz('America/New York'))

  #now = now - datetime.timedelta(days=1)
  cutoff = now + datetime.timedelta(days=12)
  #print ("CRUNCH EFFECTIVE RUNDATE FIXME!!",now) # FIXME!!
  ## ADJUST HERE FOR TZ! (i.e. If we run Midnight on Sunday don't want LAST week's run
  dow = now.weekday() # 0=Monday
  dow = (dow+1) %7  #0=Sunday
  weeknum = int(now.strftime("%U")) 
  #print "weeknum",weeknum,"Weekday",weekday[dow],"DOW",dow
  weekstart = (now - datetime.timedelta(days=dow))
  weekstart = weekstart.replace(hour=0,minute=0,second=0,microsecond=0)
  weekend = weekstart + datetime.timedelta(days=7)
  weekend = weekend - datetime.timedelta(seconds=1)
  #print "WEEKSTART",weekstart,"through",weekend
  errors=[]
  warnings=[]
  billables=[]
  summaries=[]
  debug=[]
  data={}
  entries=[]

  debug.append("{2} Week #{3} - {0} through {1}".format(weekstart.strftime("%b-%d"),weekend.strftime("%b-%d"),weekstart.year,weeknum))
  data['title']="Auto Plot Lease {2} Week #{3} - {0} through {1}".format(weekstart.strftime("%b-%d"),weekend.strftime("%b-%d"),weekstart.year,weeknum)
  data['lease-id']="autoplot-lease-{2}-Week{3:02}".format(weekstart.strftime("%b-%d"),weekend.strftime("%b-%d"),weekstart.year,weeknum)
  data['weekid']="{2:04}-{3:02}".format(weekstart.strftime("%b-%d"),weekend.strftime("%b-%d"),weekstart.year,weeknum)

  for component in cal.walk():
      """
      print (component.name)
      print (dict(component))
      print (dir(component))
      print (component)
      print ()
      """

      """
      print ()
      print(device)
      print(component.get('summary'))
      print(component.get('dtstart'))
      print(component.get('dtend'))
      print(component.get('dtstamp'))
      """
      

      summary={'errors':[],'warnings':[]}
      if component.name not in ("VEVENT"):
       pass
       #print ("NOT A VEVENT!!!",component.name)
       """
       print ()
       print ("NOT A VEVENT!!!",component.name)
       print ()
       """
      else:
       #print "VEVENT",component
       events = recurring_ical_events.of(component).between(now, cutoff)
       for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        #print("REOCCOR start {} duration {}".format(start, duration))
        component = event
        billable=False
        members=[]
        event={}
        calstart = component['DTSTART'].dt
        #print ("CALSTART",calstart)
        calstart = utctolocal(calstart)
        if 'DTEND' in component:
            calend =  component['DTEND'].dt
            calend =  utctolocal(calend,endofdate=True)
        else:
            calend = calstart
            #print ("ERROR FIX??? REPEAT EVENT??")
        shortstart = calstart.strftime("%-I:%M %p")
        shortend = calend.strftime("%-I:%M %p")
        yday = calstart.timetuple().tm_yday
        nowday = now.timetuple().tm_yday
        code = int(datetime.datetime.timestamp(calstart))
        if (yday == nowday):
            daystr = "Today"
        elif (yday == nowday+1):
            daystr = "Tomorrow"
        elif (yday == nowday-1):
            daystr = "Yesterday"
        else:
            daystr = calstart.strftime("%a")
            if (yday >= nowday+7):
                daystr = "Next "+daystr

        when = daystr+" "+shortstart+" - "+shortend
     
        organizer=""

        if 'ORGANIZER' in component: 
          # print "ORGANIZER",component['ORGANIZER']
          for p in component['ORGANIZER'].params:
            #print ("_  ---- ",p,component['ORGANIZER'].params[p])
            if p == "CN": organizer= component['ORGANIZER'].params[p]

        if organizer.endswith("@makeitlabs.com"):
            organizer = organizer.replace("@makeitlabs.com","")
            organizer = organizer.replace("."," ")
            organizer = organizer.title()

            
        reserved = {}
        resourceAccepted = False
        #print ("DATES",calstart,now,calend,cutoff)
        if ((calstart  >= now) or (calend >= now))  and ( calstart <= cutoff ) :

            #print ("FUTURE",organizer,calstart, "END",calend)
            for c in component['ATTENDEE']:
                #print ("ATTENDEE",str(c),c.params)
                if (type(c) == icalendar.prop.vCalAddress):
                    #print ("ATTENDEE",c.params)
                    if (c.params['PARTSTAT'] == 'ACCEPTED') and (c.params['CUTYPE'] == 'RESOURCE'):
                        resourceAccepted =True
                """
                if (c == MOPA_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['MOPA']=True
                if (c == EPILOG_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['EPILOG']=True
                """
	
            """
            print ("SUMMARY",component['SUMMARY'])
            print ("LOCATTION",component['LOCATION'])
            print ("STATUS",component['STATUS'])
            print ("START",calstart)
            print ("END",calend)
            print ("START",shortstart)
            print ("END",shortend)
            print ("ORGANIZER",organizer)
            print ("CODE",code)
            print ("WHEN",when)
            print ("RESERVED",reserved)
            print ()
            """

            #device=""
            if 'MOPA' in reserved and 'EPILOG' in reserved:
                device = "Laser Room"
            elif 'MOPA' in reserved:
                device = "MOPA"
            elif 'EPILOG' in reserved:
                device = "Epilog"
            #print ("APPEND", str(component['SUMMARY']),when)
            summary = ""
            if 'SUMMARY' in component:
                summary = str(component['SUMMARY'])
            if resourceAccepted:
                entries.append ({
                "SUMMARY":summary,
                "START":calstart,
                "END":calend,
                "START":shortstart,
                "END":shortend,
                "ORGANIZER":organizer,
                "CODE":code,
                "DOW":daystr,
                "ROOM":device,
                "TIME":shortstart+"-"+shortend,
                "WHEN":when
                    })
        

  if (len(errors) != 0):
    data['Decision']='error'
  elif (len(billables) == 0):
    data['Decision']='no_bill'
  else:
    data['Decision']='bill'
  return ( {
      "errors":errors,
      "warnings":warnings,
      "debug":debug,
      "data":data,
      "entries":entries
      })


def upcomming_events():
    e = []

    for cal in ICALS:
        e += get_calendar(cal[1],cal[0])['entries']
        #print (cal[0],e)

    # COLLAPSE DUPLICATES!!

    dest = []
    for (i,x) in enumerate(e):
        for y in e[i+1:]:
            if (y['ROOM'] in ('Laser-Epilog','Laser-MOPA')) and (x['WHEN'] == y['WHEN']) and (x['SUMMARY'] == y['SUMMARY']) and ('DROP' not in x):
                #print ("MATCH",x,y)
                y['DROP']= True
                x['ROOM']='Laser Room'


    out = []
    for x in e:
        if 'DROP' not in x:
            out.append(x)
    res = []
    #print (json.dumps(e,indent=2))
    for x in sorted(out,key=lambda i:i['CODE'])[0:6]:
        if '@' in x['ORGANIZER']:
            x['ORGANIZER'] = '';

        x['ORGANIZER'] = html.escape(x['ORGANIZER'])[0:30];
        x['WHEN'] = html.escape(x['WHEN'])[0:30];
        x['SUMMARY'] = html.escape(x['SUMMARY'])[0:30];
        x['ROOM'] = html.escape(x['ROOM'])[0:30];
        res.append(x)

    return res


if __name__ == "__main__":
    print ("Access-Control-Allow-Origin: *")
    print("Content-type: application/json\n\n")

    res = upcomming_events()
    print (json.dumps(res,indent=2))

