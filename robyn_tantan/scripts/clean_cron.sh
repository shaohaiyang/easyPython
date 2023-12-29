#!/bin/sh
daytime=$(date +%s)

echo "now time: $daytime "
for time in $(crontab  -l | awk '/^[^#]/{print $NF}');do
  echo -en "cron task time: $time | "
  if [ $daytime -gt $time ];then
    cron_tmp=$(crontab  -l | awk '/'"$time"'/{print $(NF-2)}')
    echo "--- task: $cron_tmp"
    rm -rf $cron_tmp
    crontab  -l | grep -vE "$time|^$" | crontab
  else
    echo "+++ task: $cron_tmp"
  fi
done
