import time
import sqlite3
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--links", help="show links from database",
                    action="store_true")
args = parser.parse_args()

conn = sqlite3.connect('sites.db')
c = conn.cursor()

if args.links:
	for row in c.execute('SELECT * FROM sites'):
		print(row[0],"\t",row[1],"\t",row[2])
	conn.close()
	exit()

while 1:
	for row in c.execute('SELECT * FROM sites'):
		if int((time.time() - int(row[2]))) > int(row[1]):
			r = requests.get(row[0])
			if r:
				print(row[0], row[1], row[2], "\t -- ok")
			else:
				print(row[0], row[1], row[2], "\t -- no")
			del r
			c.execute("UPDATE sites SET last=? WHERE url=?", (time.time(), row[0]))        
			conn.commit()
	time.sleep(30)

conn.close()