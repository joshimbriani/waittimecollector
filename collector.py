import pyarks
import sqlite3
import arrow

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
        c.execute('''CREATE TABLE waitTime (datetime text, ride text, wait real, park text, earlyEntry boolean)''')
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

now = arrow.now()

if now <= closeUSF or now >= earlyEntryUSF:
    for ride in usf.rides:
        if not ride.closed:
            earlyEntry = False
            if now > earlyEntryUSF and now < openUSF:
                earlyEntry = True
            c.execute("INSERT INTO waitTime VALUES ('" + now.isoformat() + "', '" + str(ride.name.encode('unicode_escape').decode('utf-8').replace("'", "''")) + "', " + str(ride.waitTime) + " , 'USF', " + str(int(earlyEntry)) + ")")
        print(ride.name, ' ', ride.waitTime)

if now <= closeIOA or now >= earlyEntryIOA:
    for ride in ioa.rides:
        if not ride.closed:
            earlyEntry = False
            if now > earlyEntryIOA and now < openIOA:
                earlyEntry = True
            c.execute("INSERT INTO waitTime VALUES ('" + now.isoformat() + "', '" + str(ride.name.encode('unicode_escape').decode('utf-8').replace("'", "''")) + "', " + str(ride.waitTime) + " , 'IOA', " + str(int(earlyEntry)) + ")")
        print(ride.name, ' ', ride.waitTime)

conn.commit()
conn.close()