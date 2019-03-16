I'm using nginx, uwsgi, and systemd.

The nginx config file goes here `/etc/nginx/sites-available/myweather.conf`

The uwsgi config file goes here `/etc/uwsgi/apps-enabled/uwsgi.ini`

For the systemd config file `/etc/systemd/system/uwsgi.service`, update these two lines appropriately:

```
Environment=SECRET_KEY=your_secret_key
Environment=WUNDERGROUND_KEY=your_api_key
```

The file `crontab` is used to regularly refresh the data for a few locations
and to send a daily report. It needs you to have a `.profile` file in your
home directory where you set `export WUNDERGROUND_KEY="your_api_key"`.

You may need to run this from time to time: `sudo service uwsgi restart`
