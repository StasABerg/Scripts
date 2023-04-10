BEARER_TOKEN="apitoken"

while read domain ip; do
    echo "Updating DNS record for $domain to $ip"

    zone_result=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$domain" \
        -H "Authorization: Bearer $BEARER_TOKEN" \
        -H "Content-Type: application/json")

    zone_id=$(echo "$zone_result" | jq -r '.result[0].id')
    if [ -z "$zone_id" ]; then
        echo "Zone ID not found for $domain"
        continue
    fi

    record_result=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records?type=A&name=$domain" \
        -H "Authorization: Bearer $BEARER_TOKEN" \
        -H "Content-Type: application/json")

    record_id=$(echo "$record_result" | jq -r '.result[0].id')
    if [ -z "$record_id" ]; then
        echo "DNS record not found for $domain and IP $ip"
        continue
    fi

    update_result=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records/$record_id" \
        -H "Authorization: Bearer $BEARER_TOKEN" \
        -H "Content-Type: application/json" \
        --data "{\"type\":\"A\",\"name\":\"$domain\",\"content\":\"$ip\",\"ttl\":1,\"proxied\":true}")

    if [[ $update_result == *"\"success\":false"* ]]; then
        echo "Failed to update DNS record for $domain"
        echo "$update_result"
    else
        echo "DNS record updated for $domain"
    fi
done < domains.txt
