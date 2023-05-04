import csv

base_compose = '''
version: '3'
networks:
  wordpress-network:
    name: wordpress-network

services:
'''

service_template = '''
  {service_name}:
    image: docker.io/bitnami/wordpress-nginx:latest
    volumes:
      - {volume_name}:/bitnami/wordpress
    environment:
      - ALLOW_EMPTY_PASSWORD=no
      - WORDPRESS_DATABASE_HOST=mariadb
      - WORDPRESS_DATABASE_PORT_NUMBER=3306
      - WORDPRESS_DATABASE_NAME={db_name}
      - WORDPRESS_TABLE_PREFIX={db_prefix}
      - WORDPRESS_DATABASE_USER=${{DB_USER}}
      - WORDPRESS_DATABASE_PASSWORD=${{DB_PASSWORD}}
      - WORDPRESS_DATA_TO_PERSIST=wp-config.php wp-content files icon
      - WORDPRESS_ENABLE_REVERSE_PROXY=yes
      - WORDPRESS_ENABLE_HTTPS=yes
    depends_on:
      mariadb:
        condition: service_healthy
    extra_hosts:
      - "{service_name}:172.18.0.1"
    networks:
      - wordpress-network

'''

volumes_template = '''
volumes:
{volumes}
'''

with open('sites.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    sites = list(reader)

compose = base_compose.format(network_name=network_name)

services = ''
volumes = ''

for site in sites:
    service_name = site['sitename']
    db_name = site['dbname']
    db_prefix = site['prefix']
    volume_name = f'wordpress-{service_name.replace(".", "-")}-1'

    volumes += f'  {volume_name}:\n    driver: local\n\n'
    services += service_template.format(
        service_name=service_name,
        volume_name=volume_name,
        db_name=db_name,
        db_prefix=db_prefix,
    )

with open('docker-compose.yml', 'w') as f:
    f.write(compose + services + volumes_template.format(volumes=volumes))
