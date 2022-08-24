ARG ROS_VERSION
FROM ros:${ROS_VERSION}-ros-core
ARG ROS_VERSION

ARG SLAMCORE_ROS_DEB
ARG SLAMCORE_DEV_DEB
ARG ENTRYPOINT_FILE

COPY $SLAMCORE_DEV_DEB /slamcore-dev.deb
COPY $SLAMCORE_ROS_DEB /slamcore-ros.deb
RUN apt-get update && apt-get install -y /slamcore-dev.deb /slamcore-ros.deb

RUN echo $ROS_VERSION > ~/.ros_version
COPY $ENTRYPOINT_FILE /entrypoint.sh

# Make sure that only one ROS version is installed
RUN if [ "$(/bin/ls /opt/ros/ | wc -l)" -ne "1" ]; then \
    echo "\n\nDetected multiple installed versions of ROS. Make sure that you have installed the right Slamcore debian package for the dockerfile at hand.\n\n"; \
    exit 1; \
    fi
ENTRYPOINT [ "/entrypoint.sh" ]
