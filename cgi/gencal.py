#!/usr/bin/python3
#import ConfigParser
import icalendar,sys,os,datetime
import stripe
import pytz
import urllib
import json
from dateutil import tz


# TEST:
# QUERY_STRING=cal=metalshop ./gencal.py
MOPA_URL="https://calendar.google.com/calendar/ical/c_1886b6dkec306jdkk38lsbpbejeo8%40resource.calendar.google.com/private-0887c278adb9b128c9b0435325d2cac9/basic.ics"
EPILOG_URL="https://calendar.google.com/calendar/ical/makeitlabs.com_3133373236393938363631%40resource.calendar.google.com/private-d118fdab09a69377936a3e516b25ae45/basic.ics"
SHOPBOT_URL="https://calendar.google.com/calendar/ical/c_188ajec7o5sd8hnglghkkj80c1jh0%40resource.calendar.google.com/private-496ceab1e824edaedddcfe393de00f6a/basic.ics"
AUTO_LIFT_URL="https://calendar.google.com/calendar/ical/makeitlabs.com_188edv0v5b658jk8h92eemdsdeqom%40resource.calendar.google.com/private-c71d100a4b694502382fe7f0136f04d9/basic.ics"
TEXTILES_URL="https://calendar.google.com/calendar/ical/makeitlabs.com_1886o002p7k18ioal2slsj5kl9b30%40resource.calendar.google.com/public/basic.ics"
DARKROOM_URL="https://calendar.google.com/calendar/ical/c_188fr2u7d5i7kgpflmt7ue7rfgo0q%40resource.calendar.google.com/private-12462cc183e1c0cb8f4ce548017a9476/basic.ics"
BRIDGEPORT_URL="https://calendar.google.com/calendar/ical/c_188b54f39t68kgvikia14o9faugs8%40resource.calendar.google.com/private-a755c0d2e48b39e4690bdf36994decd1/basic.ics"
JETLATHE_URL="https://calendar.google.com/calendar/ical/c_18810t9nfo22qhp9h4fm2ngv5flt0%40resource.calendar.google.com/private-88b3bf13ab8611387380732b363d0a34/basic.ics"
PROTOTRAK_URL="https://calendar.google.com/calendar/ical/c_1889s1vmc5pomj84ltqr9eibcfa2k%40resource.calendar.google.com/private-f9b1a88020c187b538f724e886528754/basic.ics"
TORMACH_URL="https://calendar.google.com/calendar/ical/c_18856dus4un86j67m559qpd1he66c%40resource.calendar.google.com/private-9bc712c591cd5a37c1559419c2ad7b24/basic.ics"


EPILOG_ID="mailto:makeitlabs.com_3133373236393938363631@resource.calendar.google.com"
MOPA_ID="mailto:c_1886b6dkec306jdkk38lsbpbejeo8@resource.calendar.google.com"
SHOPBOT_ID="c_188ajec7o5sd8hnglghkkj80c1jh0@resource.calendar.google.com"
PROTOTRAK_ID="mailto:c_1889s1vmc5pomj84ltqr9eibcfa2k@resource.calendar.google.com"
JETLATHE_ID="mailto:c_18810t9nfo22qhp9h4fm2ngv5flt0@resource.calendar.google.com"
BRIDGEPORT_ID="mailto:c_188b54f39t68kgvikia14o9faugs8@resource.calendar.google.com"
TORMACH_ID="mailto:c_18856dus4un86j67m559qpd1he66c@resource.calendar.google.com"
AUTO_LIFT_ID="mailto:makeitlabs.com_188edv0v5b658jk8h92eemdsdeqom@resource.calendar.google.com"

# Parameters({'CUTYPE': 'RESOURCE', 'ROLE': 'REQ-PARTICIPANT', 'PARTSTAT': 'ACCEPTED', 'CN': 'MiL-1-Center-Laser room - MOPA (2)', 'X-NUM-GUESTS': '0'})



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
      #print(component.get('summary'))
      #print(component.get('dtstart'))
      #print(component.get('dtend'))
      #print(component.get('dtstamp'))
      summary={'errors':[],'warnings':[]}
      if component.name not in ("VEVENT"):
        """
        print ()
        print ("NOT A VEVENT!!!",component.name)
        print ()
        """
      else:
        #print "VEVENT",component
        billable=False
        members=[]
        event={}
        calstart = component['DTSTART'].dt
        #print "CALSTART",calstart
        calstart = utctolocal(calstart)
        if 'DTEND' in component:
            calend =  component['DTEND'].dt
            calend =  utctolocal(calend,endofdate=True)
        else:
            calend = calstart
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
        try:
            summarystr = str(component['SUMMARY'])
        except:
            summarystr = organizer
        if ((calstart  >= now) or (calend >= now))  and ( calstart <= cutoff ) :

            #print ("FUTURE",organizer,calstart, "END",calend)
            for c in component['ATTENDEE']:
                #print ("ATTENDEE",str(c))
                if (c == MOPA_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['MOPA']=True
                if (c == EPILOG_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['EPILOG']=True
                if (c == BRIDGEPORT_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['BRIDGEPORT']=True
                if (c == JETLATHE_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['JETLATHE']=True
                if (c == BRIDGEPORT_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['BRIDGEPORT']=True
                if (c == TORMACH_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['TORMACH']=True
                if (c == AUTO_LIFT_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['AUTO']=True
                if (c == PROTOTRAK_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['PROTOTRAK']=True
	
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

            device=""
            if 'MOPA' in reserved and 'EPILOG' in reserved:
                device = "Laser Room"
            elif 'MOPA' in reserved:
                device = "MOPA"
            elif 'EPILOG' in reserved:
                device = "Epilog"
            elif 'SHOPBOT' in reserved:
                device = "Shopbot"
            elif 'JETLATHE' in reserved:
                device = "Jet Lathe"
            elif 'PROTOTRAK' in reserved:
                device = "ProtoTrak Lathe"
            elif 'BRIDGEPORT' in reserved:
                device = "Bridgeport"
            elif 'AUTO' in reserved:
                device = "Auto"
            elif 'TORMACH' in reserved:
                device = "Tormach"

            if len (reserved) > 0:
                entries.append ({
                    "SUMMARY":summarystr,
                    "START":calstart,
                    "END":calend,
                    "START":shortstart,
                    "END":shortend,
                    "ORGANIZER":organizer,
                    "CODE":code,
                    "DOW":daystr,
                    "DEVICE":device,
                    "TIME":shortstart+"-"+shortend,
                    "WHEN":when
                        })
        #print "CHECK",weekstart,"<",calstart,
        #print "aand",calend,"<",weekend
        #if (weekstart <= calstart) and (calend <= weekend):

        rrule =  None
        weeks=1
        if 'RRULE' in component and 'COUNT' in component['RRULE'] and 'FREQ' in component['RRULE']: 
           rrule=component['RRULE']
           #print "RRULE",calstart.strftime("%b-%d %H:%M ")+component['SUMMARY'],
           #print rrule['COUNT'][0],rrule['FREQ'][0]
           if rrule['FREQ'][0]== "WEEKLY":
             weeks = rrule['COUNT'][0]

        for weekno in range(0,weeks):
          sss = ""
          if 'SUMMARY' in component:
              sss = component['SUMMARY']
          short = calstart.strftime("%b-%d %H:%M ")+sss
          if (calstart <= weekend) and (weekstart < calend):
            #print "THISWEEK calendar",calstart,calend
            #print "THISWEEK curweel",weekstart,weekend
            #print "PROCESS",short
            #print "WEEK IN SERIES",weekno
            if 'ATTENDEE' not in component: 
              summary['errors'].append("No Attendees")
            else:
              if isinstance(component['ATTENDEE'],list):
                attlist = component['ATTENDEE']
              else:
                attlist = [component['ATTENDEE']]
              for a in attlist:
                #print "  -- Attendee:",a
                #print "  -- Params:"
                for p in a.params:
                  pass #print "_  ---- ",p,a.params[p]
                if 'CUTYPE' in a.params and a.params['CUTYPE'] == 'INDIVIDUAL':
                  members.append(a.params['CN'])
                """
                print "  -- DIR",dir(a)
                print 
                print "  -- ICAL",type(a.to_ical),dir(a.to_ical())
                print 
                """

            hrs=(calend-calstart).total_seconds()/3600
            #print "*** CURRENT!!! {0} Hours total".format(hrs)
            if (hrs <= 24): 
              summary['warnings'].append("Partial day entry - NOT BILLING")
            elif (hrs <= 167):
              summary['warnings'].append("Entry isn't quite full week, but billing anyway")
            if (hrs > 24):
              if len(members) > 1:
                summary['errors'].append("More than one member assigned: "+str(", ".join(members)))
              elif len(members) == 0:
                summary['errors'].append("No attendees in calendar entry")
              else:
                if not members[0].lower().endswith("@makeitlabs.com"):
                  summary['errors'].append("Non-MIL email: "+str(members[0]))
                else:
                  billable=True
                  #print "*** BILLABLE"
                  event['summary']=short
                  event['member']=members[0]
              #if component['SUMMARY'].strip().lower().startswith("rental"):
              #  print "** IS RENTAL"

            # Figure out what to do based on Summary
            if (len(summary['errors']) == 0) and billable:
              billables.append(event)
            for e in summary['errors']:
              errors.append(short + ": "+e)
            for w in summary['warnings']:
              warnings.append(short + ": "+w)
          #print "END PARSE"
          calstart = calstart + datetime.timedelta(weeks=1)
          calend = calend + datetime.timedelta(weeks=1)
        # End of FOR for weeks
        
      """
      for x in component:
        print x,type(component[x]),
        if (isinstance(component[x],icalendar.prop.vDDDTypes)):
           print component.decoded(x)
           print type(component[x].dt)
           print component[x].dt
        else:
           print component.decoded(x)
        #print dir(component[x])
      print
      """


  if len(billables) ==0:
    warnings.append("WARNING - NO BILLABLES THIS WEEK!")
  elif len(billables) >1:
    errors.append("ERROR - MULTIPLE BILLABLES THIS WEEK!")

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


if __name__ == "__main__":
    print ("Access-Control-Allow-Origin: *")
    print("Content-type: application/json\n\n")
    e = []
    calname=None
    try:
        if ('QUERY_STRING' in os.environ):
            (k,v) = os.environ['QUERY_STRING'].split("=")
            if (k=="cal"):
                calname = v
    except:
        calname=None

    if (calname is None) or (calname == "laser"):
        e += get_calendar(MOPA_URL,"MOPA")['entries']
        e += get_calendar(EPILOG_URL,"EPILOG")['entries']
    elif (calname == "shopbot"):
        e += get_calendar(SHOPBOT_URL,"SHOPBOT")['entries']
    elif (calname == "auto"):
        e += get_calendar(AUTO_LIFT_URL,"AUTOLIFT")['entries']
    elif (calname == "metalshop"):
        e += get_calendar(BRIDGEPORT_URL,"BRIDGEPORT")['entries']
        e += get_calendar(JETLATHE_URL,"JETLATHE")['entries']
        e += get_calendar(TORMACH_URL,"TORMACH")['entries']
        e += get_calendar(PROTOTRAK_URL,"PROTOTRAK")['entries']
    elif (calname == "textiles"):
        e += get_calendar(TEXTILES_URL,"TEXTILES")['entries']
    elif (calname == "darkroom"):
        e += get_calendar(DARKROOM_URL,"DARKROOM")['entries']
    elif (calname == "bridgeport"):
        e += get_calendar(BRIDGEPORT_URL,"BRIDGEPORT")['entries']
    elif (calname == "jetlathe"):
        e += get_calendar(JETLATHE_URL,"JETLATHE")['entries']
    elif (calname == "prototrak"):
        e += get_calendar(PROTOTRAK_URL,"PROTOTRAK")['entries']

    # COLLAPSE DUPLICATES!!

    dest = []
    for (i,x) in enumerate(e):
        for y in e[i+1:]:
            if (x['WHEN'] == y['WHEN']) and (x['SUMMARY'] == y['SUMMARY']) and ('DROP' not in x):
                #print ("MATCH",x,y)
                y['DEVICE'] = "Laser Room"
                y['DROP']= True


    out = []
    for x in e:
        if 'DROP' not in x:
            out.append(x)

    # SORT

    res = []
    for x in sorted(out,key=lambda i:i['CODE'])[0:6]:
        res.append(x)
    print (json.dumps(res,indent=2))
