The nginx config file goes here `/etc/nginx/sites-available/myweather.conf`

For `/etc/init/uwsgi.conf`, update these two lines appropriately:

```
env SECRET_KEY="my_secret_key"
env WUNDERGROUND_KEY="my_api_key"
```

`/etc/uwsgi.ini`

You need to run this from time to time: `sudo service uwsgi restart`
