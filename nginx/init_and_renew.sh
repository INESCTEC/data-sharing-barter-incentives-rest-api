#!/bin/sh

DOMAIN="predico02.inesctec.pt"
EMAIL="andre.f.garcia@inesctec.pt"
WEBROOT="/var/www/certbot"
LIVE_CERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"

# First-time issue if cert is missing
if [ ! -f "$LIVE_CERT" ]; then
  echo "🔐 Certificate not found, issuing for $DOMAIN..."
  certbot certonly --webroot \
    --webroot-path $WEBROOT \
    -d $DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive
else
  echo "✅ Certificate already exists, skipping issuance."
fi

# Periodic renew loop
echo "⏳ Starting auto-renewal loop..."
trap exit TERM
while :; do
  certbot renew --webroot -w $WEBROOT --quiet
  sleep 12h & wait $!
done