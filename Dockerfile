ARG ROS_VERSION
FROM ros:${ROS_VERSION}-ros-core
ARG ROS_VERSION

ARG SLAMCORE_DEB
ARG ENTRYPOINT_FILE

COPY $SLAMCORE_DEB /slamcore_ros.deb
RUN apt-get update && apt-get install -y /slamcore_ros.deb

RUN echo $ROS_VERSION > ~/.ros_version
COPY $ENTRYPOINT_FILE /entrypoint.sh

# Make sure that only one ROS version is installed
RUN if [ "$(/bin/ls /opt/ros/ | wc -l)" -ne "1" ]; then \
    echo "\n\nDetected multiple installed versions of ROS. Make sure that you have installed the right SLAMcore debian package for the dockerfile at hand.\n\n"; \
    exit 1; \
    fi
ENTRYPOINT [ "/entrypoint.sh" ]
