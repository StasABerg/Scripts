import requests
import time

api_token = "api token"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(api_token),
}

json_data = {"purge_everything": True}
request_counter = 0
page = 1

while True:
    response = requests.get(
        "https://api.cloudflare.com/client/v4/zones",
        headers=headers,
        params={"per_page": 100, "page": page},
    )

    if response.status_code == 200:
        zones = response.json()["result"]

        for zone in zones:
            zone_id = zone["id"]

            response = requests.post(
                "https://api.cloudflare.com/client/v4/zones/{}/purge_cache".format(
                    zone_id
                ),
                headers=headers,
                json=json_data,
            )

            if response.status_code == 200:
                print("Cache cleared for zone: {}".format(zone["name"]))
            else:
                print("Error clearing cache for zone: {}".format(zone["name"]))

            request_counter += 1

            if request_counter == 999:
                print("Sleeping for 310 seconds...")
                time.sleep(310)
                request_counter = 0

        page += 1
    else:
        print("Error getting list of zones")
        break
