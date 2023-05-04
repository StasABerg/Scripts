import csv

proxy_pass_file = 'proxypass.conf'

with open('sites.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    sites = list(reader)

with open(proxy_pass_file, 'w') as f:
    for site in sites:
        sitename = site['sitename']
        www_option = site['www_option']
        if www_option == "www":
            prefix = "www."
        else:
            prefix = ""

        f.write(f'server {{\n')
        f.write(f'    listen 80;\n')
        f.write(f'    server_name {sitename} www.{sitename};\n')
        f.write(f'    return 301 https://{prefix}{sitename}$request_uri;\n')
        f.write(f'}}\n\n')
        f.write(f'server {{\n')
        f.write(f'    listen 443 ssl;\n')
        f.write(f'    server_name {sitename} www.{sitename};\n\n')
        f.write(f'    ssl_certificate /etc/letsencrypt/live/{sitename}/fullchain.pem;\n')
        f.write(f'    ssl_certificate_key /etc/letsencrypt/live/{sitename}/privkey.pem;\n\n')

        if www_option == "www":
            f.write(f'    if ($host = "{sitename}") {{\n')
            f.write(f'        return 301 https://{prefix}{sitename}$request_uri;\n')
            f.write(f'    }}\n\n')
        else:
            f.write(f'    if ($host = "www.{sitename}") {{\n')
            f.write(f'        return 301 https://{prefix}{sitename}$request_uri;\n')
            f.write(f'    }}\n\n')

        f.write(f'    location = /xmlrpc.php {{\n')
        f.write(f'        deny all;\n')
        f.write(f'    }}\n\n')
        f.write(f'    location = /robots.txt {{\n')
        f.write(f'        try_files $uri $uri/ /index.php?$args;\n')
        f.write(f'        access_log off;\n')
        f.write(f'        log_not_found off;\n')
        f.write(f'    }}\n\n')
        f.write(f'    location / {{\n')
        f.write(f'        proxy_pass https://wordpress-{sitename}-1:8443/;\n')
        f.write(f'        proxy_set_header Host $host;\n')
        f.write(f'        proxy_set_header X-Real-IP $remote_addr;\n')
        f.write(f'        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n')
        f.write(f'        proxy_set_header X-Forwarded-Proto $scheme;\n')
        f.write(f'        proxy_read_timeout 180s;\n')
        f.write(f'        proxy_connect_timeout 180s;\n')
        f.write(f'    }}\n')
        f.write(f'}}\n\n')
