import pyarks
import sqlite3
import arrow
import requests

conn = sqlite3.connect('waitTimes.db')

c = conn.cursor()

try:
    c.execute("SELECT 1 FROM waitTime LIMIT 1;")
    exists = True
except sqlite3.OperationalError as e:
    message = e.args[0]
    if message.startswith("no such table"):
        print("Table 'waitTime' does not exist. Creating.")
        exists = False
        c.execute('''CREATE TABLE waitTime (datetime text, ride text, wait real, park text, earlyEntry boolean, weather text, temp real, humidity real, windspeed real)''')
    else:
        raise

usf = pyarks.getPark('USF')
ioa = pyarks.getPark('IOA')

scheduleTodayUSF = usf.getOpenCloseTime()[0]
earlyEntryUSF = scheduleTodayUSF['earlyEntryTime']
openUSF = scheduleTodayUSF['openTime']
closeUSF = scheduleTodayUSF['closeTime']

scheduleTodayIOA = ioa.getOpenCloseTime()[0]
earlyEntryIOA = scheduleTodayIOA['earlyEntryTime']
openIOA = scheduleTodayIOA['openTime']
closeIOA = scheduleTodayIOA['closeTime']
weather = requests.get('http://api.openweathermap.org/data/2.5/weather?id=4167147&appid=2dfb662eba418c99bb6a79afa3cbfe09')
if weather.status_code != 200:
    print("Weather get failed. Try again later")
    exit()

weather = weather.json()
weatherfeature = weather['weather'][0]['main']
temp = ((weather['main']['temp'] - 273.15) * (9/5) + 32)
humidity = weather['main']['humidity']
windspeed = weather['wind']['speed']

now = arrow.now()

if now <= closeUSF and now >= earlyEntryUSF:
    for ride in usf.rides:
        if not ride.closed:
            earlyEntry = False
            if now > earlyEntryUSF and now < openUSF:
                earlyEntry = True
            c.execute("INSERT INTO waitTime VALUES ('" + now.isoformat() + "', '" + str(ride.name.encode('unicode_escape').decode('utf-8').replace("'", "''")) + "', " + str(ride.waitTime) + " , 'USF', " + str(int(earlyEntry)) + ", '" + str(weatherfeature) + "', " + str(int(temp)) + ", " + str(int(humidity)) + ", " + str(int(windspeed)) + ")")
        print(ride.name, ' ', ride.waitTime)

if now <= closeIOA and now >= earlyEntryIOA:
    for ride in ioa.rides:
        if not ride.closed:
            earlyEntry = False
            if now > earlyEntryIOA and now < openIOA:
                earlyEntry = True
            c.execute("INSERT INTO waitTime VALUES ('" + now.isoformat() + "', '" + str(ride.name.encode('unicode_escape').decode('utf-8').replace("'", "''")) + "', " + str(ride.waitTime) + " , 'IOA', " + str(int(earlyEntry)) + ", '" + str(weatherfeature) + "', " + str(int(temp)) + ", " + str(int(humidity)) + ", " + str(int(windspeed)) + ")")
        print(ride.name, ' ', ride.waitTime)

conn.commit()
conn.close()