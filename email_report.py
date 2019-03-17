#!/usr/bin/python
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email_credentials import email_credentials
from sqlite3 import connect
from os.path import dirname, abspath
from dateutil.parser import parse


def send_mail(data):
    mailhost, fromaddr, toaddrs, subject, credentials = email_credentials()
    username, password = credentials
    subject = 'seanweather daily report'
    body = 'Here is some interesting data, my good-looking friend:\n\n' + data
    msg = MIMEText(body, _charset="UTF-8")
    msg['Subject'] = Header(subject, "utf-8")
    server = smtplib.SMTP(mailhost)
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.quit()


def gather_data(cur):
    query = '''
select
  count(*) as c,
  location_name as name,
  location_country as country,
  location_id as id
from lookup
group by 2, 3, 4
order by c desc
'''
    return ('\n'.join('{:>3} {}, {}, {}'
            .format(*result) for result in cur.execute(query)))


def clean_up(cur):
    cur.execute('delete from lookup')

if __name__ == '__main__':
    directory = dirname(abspath(__file__))
    conn = connect(directory + '/db.db')
    cur = conn.cursor()
    send_mail(gather_data(cur))
    clean_up(cur)
    conn.commit()
    conn.close()
