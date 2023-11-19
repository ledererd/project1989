FROM registry.access.redhat.com/ubi8/python-38
WORKDIR /
COPY server.py /
COPY yamlstream.txt /tmp
RUN pip install requests pyyaml fastapi uvicorn[standard] websockets
USER root
RUN chmod 664 /tmp/yamlstream.txt
USER 1001
EXPOSE 8080
CMD ["/server.py"]
