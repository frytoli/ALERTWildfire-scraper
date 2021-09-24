FROM python:3.9-slim

# Set bash to default shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Do not prompt apt for user input when installing packages
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && \
		apt install -y \
			build-essential supervisor software-properties-common && \
		apt dist-upgrade -y

ENV VIRTUAL_ENV=/venv
RUN python3.9 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install python packages
RUN pip install --no-dependencies \
	certifi==2021.5.30 \
	charset-normalizer==2.0.4 \
	DateTime==4.3 \
	future==0.18.2 \
	idna==3.2 \
	pyArango==1.3.5 \
	python-dateutil==2.8.2 \
	pytz==2021.1 \
	PyYAML==5.4.1 \
	requests==2.26.0 \
	searchtweets-v2==1.1.1 \
	six==1.16.0 \
	urllib3==1.26.6 \
	zope.interface==5.4.0

# Add app files
ADD db /home/db
ADD main.py /home/main.py

# Let 'er rip
CMD ["/home/main.py"]
ENTRYPOINT ["python"]
