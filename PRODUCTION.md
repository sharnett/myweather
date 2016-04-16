I'm using nginx, uwsgi, and upstart.

The nginx config file goes here `/etc/nginx/sites-available/myweather.conf`

The uwsgi config file goes here `/etc/uwsgi.ini`

For the upstart config file `/etc/init/uwsgi.conf`, update these two lines appropriately:

```
env SECRET_KEY="my_secret_key"
env WUNDERGROUND_KEY="my_api_key"
```

The file `crontab` is used to regularly refresh the data for a few locations and to send a daily report.

You need to run this from time to time: `sudo service uwsgi restart`
