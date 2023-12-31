#!/bin/sh
daytime=$(date +%s)

echo "now time: $daytime "
for time in $(crontab  -l | awk '/^[^#]/{print $NF}');do
  cron_tmp=$(crontab  -l | awk '/'"$time"'/{print $(NF-2)}')
  echo -en "cron task time: $time | "
  if [ $daytime -gt $time ];then
    echo "--- task: $cron_tmp"
    #rm -rf $cron_tmp
    #crontab  -l | grep -vE "$time|^$" | crontab
  else
    echo "+++ task: $cron_tmp"
  fi
done
