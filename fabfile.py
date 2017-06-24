from fabric.api import run, env, cd

env.use_ssh_config = True
env.hosts = ['seanweather']


def deploy():
    with cd('myweather'):
        run('git pull')
        run('sudo service uwsgi restart')
