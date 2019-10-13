FROM alpine:latest

# PACKAGE INSTALLATION
RUN apk update
RUN apk add --no-cache --update-cache shadow 

# PYTHON AND PIP PACKAGES INSTALLATION
RUN echo "**** install Python ****" && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

# USER CREATION
RUN mkdir /var/mail 
RUN mkdir /home/worker
RUN useradd worker
RUN chown -R worker /home/worker
USER worker
WORKDIR /home/worker
ENTRYPOINT ["tail", "-f", "/dev/null"]