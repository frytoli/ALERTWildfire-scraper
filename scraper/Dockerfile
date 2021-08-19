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
	billiard==3.6.4.0 \
	celery==5.0.5 \
	click==7.1.2 \
	click-didyoumean==0.0.3 \
	click-plugins==1.1.1 \
	click-repl==0.1.6 \
	kombu==5.0.2 \
	prompt-toolkit==3.0.18 \
	pytz==2021.1 \
	six==1.15.0 \
	vine==5.0.0 \
	wcwidth==0.2.5

# Add supervisord app config file
ADD conf/supervise-* /etc/supervisor/conf.d/

# Add app files
RUN mkdir /app
ADD producer.py /app/producer.py
ADD consumer.py /app/consumer.py

# Let 'er rip
CMD /usr/bin/supervisord -n
