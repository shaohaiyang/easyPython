#!/bin/sh
daytime=$(date +%s)

for time in $(crontab  -l | awk '/^[^#]/{print $NF}');do
  echo "current daytime: $time  ----> "
  if [ $daytime -gt $time ];then
    cron_tmp=$(crontab  -l | awk '/'"$time"'/{print $(NF-2)}')
    echo "remove $time file: $cron_tmp ......................"
    rm -rf $cron_tmp
    crontab  -l | grep -vE "$time|^$" | crontab
  fi
done
