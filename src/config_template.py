import datetime

## List of NJ MVC's
# (268) BAYONNE
# (274) SOUTH PLAINFIELD
# (275) EDISON
# (276) FLEMINGTON
# (279) LODI
# (281) NEWARK
# (282) NORTH BERGEN
# (283) WAYNE
# (284) OAKLAND
# (285) PATERSON
# (287) RAHWAY
# (288) RANDOLPH

mvc_to_process = [268,274,275,276,279,281,282,283,284,285,287,288]
#mvc_to_exclude = [269,289,280,271,286,270,272,277,267,278,273]

apt_threshold = datetime.datetime(2022,3,15)


tg_user     = "xxxxxxxxx"
tg_group    = "@xxxxxxxx"
tg_token    = "xxxxxxxxx"

apt_firstName       ="xxx"
apt_lastName        ="xxx"
apt_email           ="xxx"
apt_phone           ="xxx"
apt_driverlicense   ="axx"

### system settings
url                     = "xxx"
make_appointment_url    = "xxx"
worker_candidates       = ["worker", "localhost"]
request_interval        = 10 
