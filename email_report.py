#!/usr/bin/python
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email_credentials import email_credentials
from sqlite3 import connect
from os.path import dirname, abspath
from dateutil.parser import parse

def send_mail(data):
	mailhost, fromaddr, toaddrs, subject, credentials = email_credentials()
	username, password = credentials
	subject = 'seanweather daily report'
	head = '<head><style>\ntable, th, td {\n  border: 0px solid black;\n  padding: 5px;\n}\n</style></head>'
	body = '<body>\nHere are some interesting results, my good-looking friend:\n\n' + data + '\n</body>'
	msg = MIMEText(head+body, 'html', _charset="UTF-8")
	msg.add_header('Subject', subject)
	server = smtplib.SMTP(mailhost)
	server.starttls()
	server.login(username, password)
	server.sendmail(fromaddr, toaddrs, msg.as_string())
	server.quit()

def gather_data(cur):
	query = 'select count(*) as c, name from lookup group by name order by c desc'
	counts, cities = zip(*cur.execute(query))
	return pd.DataFrame(dict(Count=counts, City=cities)).to_html(index=False, col_space=3, justify='left')

def clean_up(cur):
	cur.execute('delete from lookup')
	cur.execute('update location set cache="" where julianday(last_updated) < julianday()-1')

if __name__ == '__main__':
	directory = dirname(abspath(__file__))
	conn = connect(directory + '/db.db')
	cur = conn.cursor()
	send_mail(gather_data(cur))
	clean_up(cur)
	conn.commit()
	conn.close()