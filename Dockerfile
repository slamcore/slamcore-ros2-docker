FROM ros:foxy-ros-core

ARG SLAMCORE_DEB
ARG ENTRYPOINT_FILE

COPY $SLAMCORE_DEB /slamcore_ros.deb
RUN apt-get update && apt-get install -y /slamcore_ros.deb

COPY $ENTRYPOINT_FILE /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
