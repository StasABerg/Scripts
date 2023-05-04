import csv

with open('list.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    sites = list(reader)

for site in sites:
    sitename = site['sitename']
    www_option = site['www_option']
    if www_option == "www":
        prefix = "www."
        redirect_site = sitename
    else:
        prefix = ""
        redirect_site = f"www.{sitename}"


    with open(f{sitename}.conf', 'w') as f:
        f.write(f'server {{\n')
        f.write(f'    listen 443 ssl http2;\n')
        f.write(f'    ssl_certificate /etc/letsencrypt/live/{sitename}/fullchain.pem;\n')
        f.write(f'    ssl_certificate_key /etc/letsencrypt/live/{sitename}/privkey.pem;\n')
        f.write(f'    server_name {sitename} www.{sitename};\n')
        f.write(f'    root /var/www/{sitename};\n')
        f.write(f'    if ($host = "{redirect_site}") {{\n')
        f.write(f'        return 301 https://{prefix}{sitename}$request_uri;\n')
        f.write(f'    }}\n\n')
        f.write(f'}}\n\n')

        f.write(f'server {{\n')
        f.write(f'    listen 80;\n')
        f.write(f'    server_name {sitename} www.{sitename};\n\n')
        f.write(f'    location = / {{\n')
        f.write(f'        return 301 https://{prefix}{sitename}$request_uri;\n')
        f.write(f'    }}\n\n')
        f.write(f'}}\n\n')
