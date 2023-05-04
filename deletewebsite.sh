!#/bin/bash
while true;
do
	echo "Enter the domain name(or type 'q' to quit):"
	read domain
	if [ "$domain" = "q" ]; then
		break
	fi
	
	rm -rf /var/www/$domain
	echo "/var/www/"$domain" deleted."
	
	rm -rf /etc/nginx/conf.d/$domain.conf
	echo "/etc/nginx/conf.d/"$domain".conf deleted."
done


________________________________________

!#/bin/bash

while true;
do
    echo "Enter the domain name (or type 'q' to quit):"
    read domain
    if [ "$domain" = "q" ]; then
        break
    fi

    notlddomain=$(echo "$domain" | cut -d. -f1)
	
    rm -rf "/var/www/$notlddomain"
    echo "/var/www/$notlddomain deleted."

    rm -rf "/etc/nginx/conf.d/$domain.conf"
    echo "/etc/nginx/conf.d/$domain.conf deleted."
done


_____________________________

#! /bin/bash

domains_file="domains.txt"

if [ ! -f "$domains_file" ]; then
    echo "Error: $domains_file not found."
    exit 1
fi

while read domain; do
    rm -rf "/var/www/$domain"
    echo "/var/www/$domain deleted."
    rm -rf "/pathto/config/$domain.php"
    echo "/pathto/config/config/$domain.php deleted."
    rm -rf "/pathto/config/backup/1.3/$domain.php"
    echo "/pathto/config/1.3/$domain.php deleted."
    rm -rf "/usr/local/nginx/conf/$domain.conf"
    echo "/usr/local/nginx/conf/$domain.conf deleted."
done < "$domains_file"

