echo "$(date)" >> /var/log/mycron_bees_insert.log 2>&1
docker run --rm insert_bees_image >> /var/log/mycron_bees_insert.log 2>&1
