#!/bin/bash

websites=$(ls /root/var/www)

for website in $websites; do
  echo "Looking for matching docker volumes for website: $website"
  for volume in $(docker volume ls --format '{{.Name}}'); do
    if [[ "$volume" == *"$website"* ]]; then
      echo "Found matching docker volume: $volume"
      rsync -azh /root/var/www/$website/public_html/wp-content /var/lib/docker/volumes/${volume}/_data/
      rsync -azh /root/var/www/$website/public_html/files /var/lib/docker/volumes/${volume}/_data/
      rsync -azh /root/var/www/$website/public_html/icon /var/lib/docker/volumes/${volume}/_data/
    fi
  done
done
