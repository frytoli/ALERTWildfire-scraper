# Alert Wildfire Scraper

## ArangoDB
Run the instance:
```
docker run -p 127.0.0.1:8529:8529 -e ARANGO_ROOT_PASSWORD=changeme -v arangodb_data:/var/lib/arangodb3 -v arangodb_apps:/var/lib/arangodb3-apps arangodb/arangodb:3.8.0
```

## Scraper
Scraped images from cameras on an hourly cadence or when alerted by a tweet

## Tweet Alerts
Monitoring and saving of tweets @AlertWildfire that alert for wildfire activity
