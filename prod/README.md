I'm using nginx, uwsgi, and systemd according to the [Digital Ocean
instructions for Flask on Ubuntu 18.04]
(https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04).

The nginx config file goes here `/etc/nginx/sites-available/myweather.conf`.
Update the lines with `root` and `uwsgi_pass` appropriately to match your
directory structure.

For the uwsgi config file `myweather.ini`, update the `chdir` line appropriately.

For the systemd config file `/etc/systemd/system/myweather.service`, update the
`WorkingDirectory` line similarly. Also update these two lines:

```
Environment=SECRET_KEY=your_secret_key
Environment=OPENWEATHERMAP_KEY=your_api_key
```

The file `crontab` is used to to send a daily report.

You may need to run these from time to time:

```
sudo systemctl daemon-reload
sudo systemctl restart myweather
sudo systemctl restart nginx
```
