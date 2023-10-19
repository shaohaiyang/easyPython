#!/bin/sh
cp -a requirements.txt requirements.bak 
pip3.10 install -U pip
pip3.10 install "robyn" -U
pip3.10 install "robyn[templating]" -U
prisma db push --schema sqldb/schema.prisma 
supervisorctl stop robyn
/opt/python3.10.6/bin/python3 /root/robyn_demo/main.py 
supervisorctl restart robyn
supervisorctl status
python3.10 -m pip freeze > requirements.txt
