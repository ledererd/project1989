FROM registry.access.redhat.com/ubi8/python-38
WORKDIR /
COPY server.py /
COPY pod-template.yaml /

ENV OKD_DOWNLOAD_BASE_URL="https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp" \
    VERSION=latest-4.12 \
    ARCHIVE=openshift-client-linux

RUN curl -sSL "${OKD_DOWNLOAD_BASE_URL}/${VERSION}/${ARCHIVE}.tar.gz" -o /tmp/oc.tgz && \
    cd /tmp && \
    tar -xzvf /tmp/oc.tgz && \
    chmod 755 "/tmp/oc"

EXPOSE 8080
CMD ["/server.py"]
