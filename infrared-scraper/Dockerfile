FROM python:3.9-slim

# Set bash to default shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Do not prompt apt for user input when installing packages
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && \
		apt install -y \
			build-essential supervisor software-properties-common \
			gconf-service libasound2 libatk1.0-0 libc6 libcairo2 \
			libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 \
			libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 \
			libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 \
			libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
			libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 \
			libxrender1 libxss1 libxtst6 ca-certificates \
			fonts-liberation libnss3 lsb-release xdg-utils wget && \
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
celery==5.1.2 \
certifi==2021.5.30 \
charset-normalizer==2.0.4 \
click==7.1.2 \
click-didyoumean==0.0.3 \
click-plugins==1.1.1 \
click-repl==0.2.0 \
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
kombu==5.1.0 \
lxml==4.6.3 \
oauthlib==3.1.1 \
parse==1.19.0 \
prompt-toolkit==3.0.20 \
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
urllib3==1.25.11 \
vine==5.0.0 \
w3lib==1.22.0 \
wcwidth==0.2.5 \
websockets==9.1 \
zipp==3.5.0 \
zope.interface==5.4.0

# Run pyppeteer download/install chromium script
RUN pyppeteer-install

# Add supervisord app config files
ADD conf/supervise-* /etc/supervisor/conf.d/

# Add app directories and files
RUN mkdir home/imgs
ADD src/ home/

# Let 'er rip
CMD /usr/bin/supervisord -n
