import requests
import time

api_token = "apitoken"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(api_token),
}

json_data = {"purge_everything": True}

request_counter = 0

domains = []

with open("domains.txt", "r") as f:
    for line in f:
        domain = line.strip()
        domains.append(domain)

for domain in domains:
    # Make a request to the Cloudflare API to get the zone for the domain
    response = requests.get(
        "https://api.cloudflare.com/client/v4/zones",
        headers=headers,
        params={"name": domain},
    )

    if response.status_code == 200:
        zone_id = response.json()["result"][0]["id"]
        response = requests.post(
            "https://api.cloudflare.com/client/v4/zones/{}/purge_cache".format(
                zone_id
            ),
            headers=headers,
            json=json_data,
        )

        if response.status_code == 200:
            print("Cache cleared for domain: {}".format(domain))
        else:
            print("Error clearing cache for domain: {}".format(domain))

        request_counter += 1

        if request_counter == 999:
            print("Sleeping for 310 seconds...")
            time.sleep(310)
            request_counter = 0
    else:
        print("Error getting zone ID for domain: {}".format(domain))
