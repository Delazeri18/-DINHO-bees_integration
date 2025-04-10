echo "$(date)" >> /var/log/mycron_bees_email.log 2>&1
docker run -it --rm bees_email_image >> /var/log/mycron_bees_email.log 2>&1
