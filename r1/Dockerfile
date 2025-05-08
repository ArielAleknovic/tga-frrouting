FROM frrouting/frr:latest

COPY frr.conf /etc/frr/frr.conf
COPY daemons /etc/frr/daemons
RUN chown frr:frr /etc/frr/frr.conf /etc/frr/daemons
