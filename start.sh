# start.sh

export FLASK_APP=wsgi.py
export FLASK_DEBUG=1
export APP_CONFIG_FILE=config.py

mkdir -p logs
source ~/.bash_profile

ps -ef|grep core|awk '{print $2}'|xargs kill -9

nohup python3 wsgi.py >> logs/wsgi.log 2>&1 &
