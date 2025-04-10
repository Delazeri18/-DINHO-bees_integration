echo "$(date)" >> /var/log/mycron_bees_atz.log 2>&1
docker run -it --rm atz_bees_image >> /var/log/mycron_bees_atz.log 2>&1
