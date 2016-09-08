FROM python:3.5

RUN pip install flask_admin==1.4.1 flask_mongoengine==0.7.5 requests==2.6.0
ENV ENV_MODE docker

# build uwsgi
RUN set -ex \
	&& buildDeps=' \
		gcc \
		libbz2-dev \
		libc6-dev \
		libpcre3-dev \
		libssl-dev \
		make \
		pax-utils \
		zlib1g-dev \
	' \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends $buildDeps \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir uwsgi \
	&& runDeps="$( \
    	scanelf --needed --nobanner --recursive /usr/local \
            | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
            | sort -u | cut -c4- \
            | xargs dpkg --search \
            | cut -d ':' -f 1 | sort -u \
    )" \
	&& apt-get install -y --no-install-recommends $runDeps \
	&& apt-get purge -y --auto-remove $buildDeps

RUN apt-get update && apt-get install -y openssh-server apache2 supervisor
RUN mkdir -p /var/lock/apache2 /var/run/apache2 /var/run/sshd /var/log/supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


EXPOSE 9020
COPY . /home/linan/gtask
WORKDIR /home/linan/gtask
ENV PATH $PATH:/home/linan/gtask
ln -s /usr/local/lib/python3.5/site-packages/gtask /home/linan/gtask

RUN chown -R www-data .
USER www-data

CMD ["/usr/bin/supervisord"]

