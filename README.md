# SLAMcore ROS2 docker

## Building

To build the docker image, invoke the following script (on the same device the node will run)

```shell
./build.py ../path/to/slamcore_ros2_package.deb [--tag image_tag]
```

A docker image will be created with the tag provided by the second argument or default to
`slamcore-ros2`.

## Running

### SLAM node

The docker container will by default run the SLAM node.
To start just call:

```shell
docker run --rm -it --privileged slamcore-ros2
```
replace `slamcore-ros2` with your custom image tag if you set one.

> Note the `--privileged` flag, used to give access to host devices and allow for live-camera
  runs

> The `-it` flag is required for the container to be run as a interactive process to be able to receive
  Ctrl-C commands

Arguments can be passed via the command line, to see available options, call:
```shell
docker run --rm -it --privileged slamcore-ros2 --show-args
```

### Running with a dataset

To run with a dataset pass it to the docker container via the `volume` flag:

```shell
docker run --rm -it -v /absolute/path/to/dataset:/dataset:ro slamcore-ros2 dataset_path:=/dataset
```
replace `slamcore-ros2` with your custom image tag if you set one.
Here `-v /absolute/path/to/dataset:/dataset`, only the `/absolute/path/to/dataset` needs to be specified by the user, and it is the path to the dataset on the host system.

### Alternative Nodes

Alternative nodes can be invoked by setting `SLAMCORE_MODE` environment variable, valid options are:

1. `SLAM`: run the default SLAM node
2. `DATASET_RECORDER`: run the dataset recorder node

e.g:

```shell
docker run --rm -it --privileged --env SLAMCORE_MODE=DATASET_RECORDER slamcore-ros2 --show-args
```

### Recording a dataset

To record a dataset using ROS2 wrapper, invoke the following command, with the adjustments required for your setup:

```shell
docker run --rm -it --privileged --volume /tmp/output:/output:rw --env SLAMCORE_MODE=DATASET_RECORDER slamcore-ros2 output_dir:=/output/my_dataset
```
Here, `--volume /tmp/output:/output` maps the host directory `/tmp/output`, to the directory `/output` inside the container to be used by the ROS node as set by the launch argument `output_dir`.

## Subscribing to topics

Once the node is running it is possible to subscribe to the advertised topics in another docker container, for example

```shell
docker run --rm -it ros:foxy ros2 topic echo /slamcore/pose
```

It is also possible to execute
```shell
docker run --rm -it ros:foxy bash
```
and then within that docker run commands such as:
```shell
ros2 topic list
```
