#!/bin/bash

sites=$(find /var/www/ -maxdepth 1 -type d)

for site in $sites; do
    if [ -d "$site/public_html" ]; then
        echo "Running wp --path=$site/public_html/ autoptimize clear"
        wp --path=$site/public_html/ autoptimize clear --allow-root
    else
        echo "Running wp --path=$site/ autoptimize clear"
        wp --path=$site/ autoptimize clear --allow-root
    fi
done

echo "All done!"
