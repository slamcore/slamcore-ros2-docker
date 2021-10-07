# SLAMcore ROS2 docker

## Building

To build the docker image, invoke the following script **on the same device the node will run**.

```shell
./build.py ../path/to/slamcore_ros2_package.deb [--tag image_tag]
```
You must provide the path to the SLAMcore ROS2 Wrapper debian package for x64 or Jetson, depending on your host system. A docker image will be created with the tag provided by the second argument or default to `slamcore-ros2`.

## Running

### SLAM node

The docker container will by default run the SLAM node.
To start it just call:

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

If you would like to save the resulting session from the SLAM run, which can be later used for localisation mode, you will need to provide the `--volume` or `-v` flag, as well as the `session_save_dir` argument, when launching the container. This will allow you to save the file to the host machine when calling the `/slamcore/save_session` service from another terminal, as explained in the [Calling a service](#calling-a-service) section.

```shell
docker run --rm -it --privileged --volume /path/to/save/session:/output:rw slamcore-ros2 session_save_dir:=/output
```
Simply replace the `/path/to/save/session` above, with the absolute path to the directory where the session file should be saved on your host machine. 

> The `--volume` flag maps the host machine directory `/path/to/save/session` to the container directory `/output` - this is done by mounting the `/path/to/save/session` directory as `/output` inside the container. Therefore, when something is saved to the `/output` directory in the container, it will be saved to the provided path on the host machine and not lost when the container is shut down.

### SLAM using a recorded dataset

To run with a dataset pass it to the docker container via the `-v` flag:

```shell
docker run --rm -it -v /absolute/path/to/dataset:/dataset:ro slamcore-ros2 dataset_path:=/dataset
```
replace `slamcore-ros2` with your custom image tag if you set one and the `/absolute/path/to/dataset` (the absolute path to the dataset on the host machine) section when passing in the `-v /absolute/path/to/dataset:/dataset` flag.

### Localisation Mode

In localisation mode, our system uses a previously created session map to localise. To load a session map, the `--volume` or `-v` flag with the path to the session file on the host machine (`/absolute/path/to/file.session`) needs to be provided:

```shell
docker run --rm -it --privileged -v /absolute/path/to/file.session:/sessions/file.session:ro slamcore-ros2 session_file:=/sessions/file.session
```
When the system is able to localise on the map, it will start publishing data to the topics.

### Height Mapping Mode

In mapping mode, our system runs in SLAM mode but also generates a height map and an occupancy map which can be used in autonomous navigation.

To generate a height map, set the `generate_map2d` parameter to true and ensure the depth stream is enabled using the `override_realsense_depth` and `realsense_depth_override_value` parameters:

```shell
docker run --rm -it --privileged --volume /path/to/save/session:/output:rw slamcore-ros2 generate_map2d:=true override_realsense_depth:=true realsense_depth_override_value:=true session_save_dir:=/output
```
You will also need to provide the `--volume` flag along with the `session_save_dir` parameter as shown above if you want to save the session file containing the maps to your host machine. To save the session, you must trigger the `/slamcore/save_session` service, explained in the [Calling a service](#calling-a-service) section.

### Alternative Nodes

Alternative nodes can be invoked by setting the `SLAMCORE_MODE` environment variable, valid options are:

1. `SLAM`: run the default SLAM node
2. `DATASET_RECORDER`: run the dataset recorder node

e.g:

```shell
docker run --rm -it --privileged --env SLAMCORE_MODE=DATASET_RECORDER slamcore-ros2 --show-args
```

### Recording a dataset

To record a dataset using the ROS2 wrapper, invoke the following command, with the adjustments required for your setup:

```shell
docker run --rm -it --privileged --volume /path/to/save/dataset:/output:rw --env SLAMCORE_MODE=DATASET_RECORDER slamcore-ros2 output_dir:=/output/my_dataset
```
In the example above, `--volume /path/to/save/dataset:/output` maps the host directory `/path/to/save/dataset` to the directory `/output` inside the container. You can then use the `output_dir` argument to define the dataset path inside the container. The new directory `/my_dataset` inside the container will appear in your host machine under `/path/to/save/dataset/my_dataset`.

## Subscribing to topics

Once the node is running it is possible to subscribe to the advertised topics in another docker container, for example:

```shell
docker run --rm -it ros:foxy ros2 topic echo /slamcore/pose
```
It is also possible to execute:

```shell
docker run --rm -it ros:foxy bash
```
and then within that docker run commands such as:

```shell
ros2 topic list
```
You can find more details on the available topics in our [ROS2 Wrapper Advertised Topics](https://docs.slamcore.com/ros2-wrapper.html#advertised-topics) documentation section.

## Calling a service

When the node is running, you can also call the available services from another docker container, for example:

```shell
docker run --rm -it ros:foxy ros2 service call /slamcore/save_session std_srvs/Trigger
```
will allow you to save the session file from the current session.

Similar to topics, you can run a new container with:

```shell
docker run --rm -it ros:foxy bash
```
and then inside it, run

```shell
ros2 service list -t
```
to get the full list of available services. You can find more details on the available services in our [ROS2 Wrapper Advertised Services](https://docs.slamcore.com/ros2-wrapper.html#advertised-services) documentation section.