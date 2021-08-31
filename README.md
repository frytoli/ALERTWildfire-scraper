# ALERTWildfire Scraper

A multi-pronged service created for the goal of collecting training data for USC research project "Early Fire Detection" that includes:
* an asynchronous scraper which collects images from http://www.AlertWildfire.org and uploads a zip compressed archive of the images to Google Drive after each full execution
* a Tweet monitor that saves Tweets that mention @AlertWildfire's Twitter account (potentially in regards to a wildfire) to a database
* an ArangoDB instance which stores the urls of ALERTWildfire's cameras (as collected by ```scripts/enumerator.py```) and Tweets of interest as collected by the Tweet monitor

"ALERTWildfire is a network of over 900 specialized camera installations in California, Nevada, Idaho and Oregon used by first responders and volunteers to detect and monitor wildfires." <b>[Nevada Today](https://www.unr.edu/nevada-today/news/2021/alertwildfire-thermal-cameras)

## Prerequisites

1. Create a Twitter Developer account, start a new project, and set the CLIENT_ID and CLIENT_SECRET environment variables in ```docker-compose.yml``` accordingly. [Step-by-step guide to making your first request to the new Twitter API v2](https://developer.twitter.com/en/docs/tutorials/step-by-step-guide-to-making-your-first-request-to-the-twitter-api-v2)
2. Create a Google Developer account, create a new project with the Google Drive API (ensure that the scopes include read access to file metadata and write/file upload access to drive), authenticate a user outside of Docker (I used Google's [quickstart](https://developers.google.com/drive/api/v3/quickstart/python#step_2_configure_the_sample)), and set PROJECT_ID, TOKEN, REFRESH_TOKEN, and GDRIVE_PARENT_DIR environment variables accordingly.

## Run
```
docker-compose build --parallel && docker-compose up -d
```

## ArangoDB
Local ArangoDB database instance that stores all camera URLS (as collected by ```scripts/enumerator.py```) and Tweets from the Tweet Alerts monitor

Technologies:
* Docker
* ArangoDB (latest)

## RabbitMQ
Celery broker in Scraper.

Technologies:
* Docker
* RabbitMQ (latest)

## Redis
Celery backend in Scraper.

Technologies:
* Docker
* Redis (latest)

## Scraper
Distributed, asynchronous scraping service of images from ALERTWildfire cameras.

Technologies:
* Docker
* ArangoDB (latest)
* Python 3.9
  * [Celery](https://github.com/celery/celery) (5.1.2)
  * [requests_html](https://github.com/psf/requests-html) (0.10.0)
* Redis (latest)
* RabbitMQ (latest)
* Twitter Developer API
* Google Drive API
* Free Proxyscrape API

### Environment Variables
<b>RABBITMQ_DEFAULT_USER</b>: RabbitMQ user

<b>RABBITMQ_DEFAULT_PASS</b>: RabbitMQ password

<b>CONCURRENCY</b>: integer number of concurrent celery tasks

<b>LOGLEVEL</b>: logging level (i.e. info)

<b>CHUNK_SIZE</b>: integer number of camera urls to be retrieved by asynchronous HTTP requests per celery task

<b>DB_HOST</b>: database host

<b>DB_PORT</b>: (arangodb) database port

<b>DB_NAME</b>: (arangodb) database name

<b>DB_USER</b>: (arangodb) database user

<b>DB_PASS</b>: (arangodb) database password

<b>CLIENT_ID</b>: Twitter API client ID

<b>CLIENT_SECRET</b>: Twitter API client secret

<b>PROJECT_ID</b>: Google Drive API project ID

<b>TOKEN</b>: Google Drive API token

<b>REFRESH_TOKEN</b>: Google Drive API refresh token

<b>GDRIVE_PARENT_DIR</b>: ID of Google Drive directory in which to save zip archives of the scraped images

## Logs

Stdout and stderr are sent to ```/var/log/celery.log``` and ```/var/log/producer.log```. This can be changed in ```scraper/conf/supervise-celery.conf``` and ```scraper/conf/supervise-producer.conf```.

## Tweet Alerts
Monitoring service that looks for and saves Tweets at @AlertWildfire to a local database that, one can assume, indicate wildfire activity on one of the cameras

Technologies:
* Docker
* ArangoDB (latest)
* Python 3.9
  * [searchtweets-v2](https://github.com/twitterdev/search-tweets-python)
* Twitter Developer API

## Environment Variables

<b>DB_HOST</b>: database host

<b>DB_PORT</b>: (arangodb) database port

<b>DB_NAME</b>: (arangodb) database name

<b>DB_USER</b>: (arangodb) database user

<b>DB_PASS</b>: (arangodb) database password

<b>CLIENT_ID</b>: Twitter API client ID

<b>CLIENT_SECRET</b>: Twitter API client secret

<b>PROJECT_ID</b>: Twitter API project ID
