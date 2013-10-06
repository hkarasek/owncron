import time, sqlite3, argparse, requests

parser = argparse.ArgumentParser()
parser.add_argument("--list", help="show links from database", action="store_true")
parser.add_argument("--add", help="add link to db", action="store_true")
parser.add_argument("--remove", help="remove link from db", action="store_true")

args = parser.parse_args()

conn = sqlite3.connect('sites.db')
c = conn.cursor()

if args.remove:
	print('remove link from db: \n ###############################')
	print('links:')
	for row in c.execute('SELECT * FROM sites'):
		print(row[0],"\t",row[1],"\t",row[2])
	print('###############################')
	url = input('url: \t\t')
	period = input('period: \t')
	c.execute("DELETE FROM sites WHERE url = \'"+url+"\' AND period = \'"+period+"\'")
	conn.commit()
	conn.close()
	exit()

if args.add:
	print('Add link to db: \n###############################')
	url = input('url: \t\t')
	period = input('period: \t')
	c.execute("INSERT INTO sites VALUES (?,?,?)", (url, period,-1))
	conn.commit()
	conn.close()
	exit()

if args.list:
	for row in c.execute('SELECT * FROM sites'):
		print(row[0],"\t",row[1],"\t",row[2])
	conn.close()
	exit()



def send_mail(url,mtype):
	message = ['DOWN','UP']
	return requests.post(
        "https://api.mailgun.net/v2/hkar.mailgun.org/messages",
        auth=("api", "key-5nfl-1iurn9qvd-r9veh4p4r231w9by7"),
        data={"from": "OwnCron <cron@hkar.mailgun.org>",
              "to": ["admin@hkar.eu"],
              "subject": "Cron " +message[mtype],
              "text": 'The '+url+' is '+message[mtype]})

########################
# define some variables#
########################
cron_error = {} # dictionary of the error links
#####

while 1:
	for row in c.execute('SELECT * FROM sites'):
		if int((time.time() - int(row[2]))) > int(row[1]):
			try:
				r = requests.get(row[0], timeout=15)
				print(row[0], row[1], row[2], "\t -- ok")
				c.execute("UPDATE sites SET last=? WHERE url=?", (time.time(), row[0]))        
				conn.commit()
				try:
					del cron_error[row[0]]
					send_mail(row[0], 1)
				except:
					pass
				del r
			except:
				print(row[0], row[1], row[2], "\t -- no")
				try:
					cron_error[row[0]] += 1
					print('times \t' + str(cron_error[row[0]]))
				except:
					cron_error[row[0]] = 1
					print('times \t' + str(cron_error[row[0]]))
					print(send_mail(row[0], 0))
	time.sleep(10)
conn.close()