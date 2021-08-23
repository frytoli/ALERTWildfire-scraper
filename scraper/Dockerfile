FROM python:3.9-slim

# Set bash to default shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Do not prompt apt for user input when installing packages
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && \
		apt install -y \
			build-essential \
      supervisor \
			software-properties-common && \
		apt dist-upgrade -y

ENV VIRTUAL_ENV=/venv
RUN python3.9 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install python packages
RUN pip install --no-dependencies \
amqp==5.0.6 \
appdirs==1.4.4 \
beautifulsoup4==4.9.3 \
billiard==3.6.4.0 \
bs4==0.0.1 \
cachetools==4.2.2 \
celery==5.0.5 \
certifi==2021.5.30 \
charset-normalizer==2.0.4 \
click==7.1.2 \
click-didyoumean==0.0.3 \
click-plugins==1.1.1 \
click-repl==0.1.6 \
cssselect==1.1.0 \
DateTime==4.3 \
fake-useragent==0.1.11 \
future==0.18.2 \
google-api-core==2.0.0 \
google-api-python-client==2.17.0 \
google-auth==2.0.1 \
google-auth-httplib2==0.1.0 \
google-auth-oauthlib==0.4.5 \
googleapis-common-protos==1.53.0 \
httplib2==0.19.1 \
idna==3.2 \
importlib-metadata==4.6.4 \
kombu==5.0.2 \
lxml==4.6.3 \
oauthlib==3.1.1 \
parse==1.19.0 \
prompt-toolkit==3.0.18 \
protobuf==3.17.3 \
pyArango==1.3.5 \
pyasn1==0.4.8 \
pyasn1-modules==0.2.8 \
pyee==8.2.2 \
pyparsing==2.4.7 \
pyppeteer==0.2.6 \
pyquery==1.4.3 \
pytz==2021.1 \
requests==2.26.0 \
requests-html==0.10.0 \
requests-oauthlib==1.3.0 \
rsa==4.7.2 \
six==1.15.0 \
soupsieve==2.2.1 \
tqdm==4.62.1 \
uritemplate==3.0.1 \
urllib3==1.26.6 \
vine==5.0.0 \
w3lib==1.22.0 \
wcwidth==0.2.5 \
websockets==9.1 \
zipp==3.5.0 \
zope.interface==5.4.0

# Add supervisord app config file
ADD conf/supervise-* /etc/supervisor/conf.d/

# Add app files
RUN mkdir /app
ADD producer.py /app/producer.py
ADD consumer.py /app/consumer.py
ADD db /app/db
ADD drive /app/drive
ADD invoke_hourly.py /app/invoke_hourly.py
ADD invoke_tweet.py /app/invoke_tweet.py

# Let 'er rip
CMD /usr/bin/supervisord -n
