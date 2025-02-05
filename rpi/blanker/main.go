package main
import (
        "fmt"
        "flag"
        "time"
)


/*

if (message.topic == "facility/alarm/system"):
        if msg == "armed":
            print ("ARMED")
            tv_onoff(False)
        elif msg == "disarmed":
        */

func main() {
        configfile := flag.String("config", "blanker.cfg", "Config file")
        flag.Parse()
        fmt.Printf("Wprdptr: %s\n",*configfile)
        get_config(*configfile)
        fmt.Printf("Config: %+v\n",cfg)
        mqtt_init()

        for  {
                time.Sleep(60)
        }
}
