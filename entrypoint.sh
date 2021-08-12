#!/bin/bash

source /opt/ros/foxy/setup.bash

slamcore_mode=${SLAMCORE_MODE:-SLAM}

case $slamcore_mode in
    SLAM)
        exec "ros2" "launch" "slamcore_slam" "slam_publisher.launch.py" "$@"
        ;;

    DATASET_RECORDER)
        exec "ros2" "launch" "slamcore_slam" "dataset_recorder.launch.py" "$@"
        ;;

    *)
        echo "SLAMCORE_MODE=$SLAMCORE_MODE was not recognised"
        exit 1
esac
