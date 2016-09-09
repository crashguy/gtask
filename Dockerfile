############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# Set the base image to use to Ubuntu
FROM ubuntu:14.04

# Set the file maintainer (your name - the file's author)
MAINTAINER linan

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV DOCKYARD_SRC=.
# Directory in container for all project files
ENV DOCKYARD_SRVHOME=/srv
# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=/srv

# Update the default application repository sources list
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python python-pip

# Create application subdirectories
WORKDIR $DOCKYARD_SRVHOME
RUN mkdir media static logs
VOLUME ["$DOCKYARD_SRVHOME/logs/"]

# Install Python dependencies
RUN pip install  \
    flask_admin==1.4.1 \
    flask_mongoengine==0.7.5 \
    requests==2.6.0 \
    mongoengine==0.10.6 \
    gunicorn==19.6.0 \
    requests==2.6.0

# Port to expose
EXPOSE 8000

COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Copy application source code to SRCDIR
COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ

# Copy entrypoint script into the image
WORKDIR $DOCKYARD_SRVPROJ/gtask_admin

CMD ["/docker-entrypoint.sh"]