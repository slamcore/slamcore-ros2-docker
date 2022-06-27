#!/bin/bash

ros_version=$(cat ~/.ros_version)
source /opt/ros/$ros_version/setup.bash

slamcore_mode=${SLAMCORE_MODE:-SLAM}

case $slamcore_mode in
    SLAM)
        exec "ros2" "launch" "slamcore_slam" "slam_publisher.launch.py" "$@"
        ;;
    DATASET_RECORDER)
        exec "ros2" "launch" "slamcore_slam" "dataset_recorder.launch.py" "$@"
        ;;
    BASH)
        RCFILE="/tmp/rcfile.sh"
        echo "source /opt/ros/$ros_version/setup.bash" > $RCFILE
        exec bash --rcfile $RCFILE
        ;;
    PASSTHROUGH)
        exec $@
        ;;
    *)
        echo "SLAMCORE_MODE=$SLAMCORE_MODE was not recognised"
        exit 1
esac
