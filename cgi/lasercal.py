#!/usr/bin/python3
#import ConfigParser
import icalendar,sys,os,datetime
import stripe
import pytz
import urllib
import json
from dateutil import tz


MOPA_URL="https://calendar.google.com/calendar/ical/c_1886b6dkec306jdkk38lsbpbejeo8%40resource.calendar.google.com/private-0887c278adb9b128c9b0435325d2cac9/basic.ics"
EPILOG_URL="https://calendar.google.com/calendar/ical/makeitlabs.com_3133373236393938363631%40resource.calendar.google.com/private-d118fdab09a69377936a3e516b25ae45/basic.ics"

EPILOG_ID="mailto:makeitlabs.com_3133373236393938363631@resource.calendar.google.com"
MOPA_ID="mailto:c_1886b6dkec306jdkk38lsbpbejeo8@resource.calendar.google.com"

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
    now = datetime.datetime.now().replace(tzinfo=tz.gettz('GMT'))

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
        calend =  component['DTEND'].dt
        calend =  utctolocal(calend,endofdate=True)
        shortstart = calstart.strftime("%-I:%M %p")
        shortend = calend.strftime("%-I:%M %p")
        yday = calstart.timetuple().tm_yday
        nowday = now.timetuple().tm_yday
        code = calstart.toordinal()
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
        if ((calstart  >= now) or (calend >= now))  and ( calstart <= cutoff ) :

            #print ("FUTURE",organizer,calstart, "END",calend)
            for c in component['ATTENDEE']:
                #print ("ATTENDEE",str(c),c.params)
                if (c == MOPA_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['MOPA']=True
                if (c == EPILOG_ID) and (c.params['PARTSTAT'] == 'ACCEPTED'):
                    reserved['EPILOG']=True
	
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
            entries.append ({
                "SUMMARY":str(component['SUMMARY']),
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
          short = calstart.strftime("%b-%d %H:%M ")+component['SUMMARY']
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
    cal = get_calendar(MOPA_URL,"MOPA")
    #print ("MOPA:",cal['entries'])
    mopa = cal['entries']
    cal = get_calendar(EPILOG_URL,"EPILOG")
    #print ("EPILOG:",cal['entries'])
    epi = cal['entries']
    e = mopa + epi

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
    res = []
    for x in sorted(out,key=lambda i:i['CODE'])[0:4]:
        res.append(x)
    print (json.dumps(res,indent=2))
