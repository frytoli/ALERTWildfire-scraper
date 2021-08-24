# ALERTWildfire Scraper

Service that scrapes images from http://www.ALERTWildfire.org on an hourly basis and when a Tweet alert is detected to @ALERTWildfire's Twitter account about a potential wildfire. A zip compressed directory of scraped images is uploaded to Google Drive after each execution.

To Run:
```
docker-compose build --parallel && docker-compose up -d
```

Technologies:
* Docker
* ArangoDB
* Python 3.9
  * Celery
  * requests_html
* Redis
* RabbitMQ
* Twitter Developer API
* Google API
* Free Proxyscrape API

## ArangoDB
All data saved in a local ArangoDB instance

## Scraper
Scraped images from cameras on an hourly cadence or when alerted by a tweet

## Tweet Alerts
Monitoring and saving of tweets @AlertWildfire that alert for wildfire activity
