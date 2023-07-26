# Slamcore ROS 2 docker

## Building

To build the docker image, invoke the following script **on the same device the
node will run**. Select either `foxy`, `galactic` or `humble` as the ROS distribution 
using the `--ros` argument and make sure that you have downloaded the right Slamcore
Debian packages for this version of ROS as well as for the architecture of the
host system (`x86` or `Jetson`). You will need to provide the `slamcore-dev` package
which matches the chosen ROS 2 distribution, e.g. for `humble` you should use the `jammy` 
`slamcore-dev` package. The resulting docker image will be created with the tag provided
by the `--tag` argument or otherwise default to `slamcore-ros2`.

```shell
./build.py ../path/to/slamcore_ros2_package.deb ../path/to/slamcore_dev_package.deb --ros foxy/galactic/humble [--tag image_tag]
```

## Building with Panoptic Segmentation Support

> Note - Panoptic Segmentation is currently only supported on ROS 2 Foxy and Galactic.

On platforms that support the panoptic segmentation plugin (currently only Nvidia Jetson
platforms listed on [docs.slamcore.com/requirements](https://docs.slamcore.com/requirements.html)),
you can  provide the `slamcore-panoptic-segmenation` package using the `--panoptic_path`
argument to build a docker image with GPU support.
```shell
./build.py ../path/to/slamcore_ros2_package.deb ../path/to/slamcore_dev_package.deb --panoptic_path ../path/to/slamcore_panoptic_segmentation_package.deb --ros foxy/galactic [--tag image_tag]
```

The machine learning model will be optimised for the current GPU during the build process, which can take up to 15 minutes.
This will require a docker system set up with nvidia as the default runtime in `/etc/docker/daemon.json`:
```
"default-runtime": "nvidia"
```
The following is an example of how the added line appears in the JSON file. Do not remove any pre-existing content when making this change.
```json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

> Note - remember to restart the docker service after any change to `/etc/docker/daemon.json`:
```shell
sudo systemctl restart docker
```

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

Alternative nodes can be invoked by setting the `SLAMCORE_MODE` environment
variable, valid options are:

1. `SLAM`: run the default SLAM node
2. `DATASET_RECORDER`: run the dataset recorder node
3. `BASH`: run bash and source the ROS `setup.bash` script
4. `PASSTHROUGH`: Run a custom user command inside the docker container

e.g:

```shell
docker run --rm -it --privileged --env SLAMCORE_MODE=DATASET_RECORDER slamcore-ros2 --show-args
```

or to run an interactive bash session and run nodes manually.

```shell
docker run --rm -it --privileged --env SLAMCORE_MODE=BASH slamcore-ros2

...

$ # You now have a console inside the container.
$ # You can e.g run SLAM,
$ ros2 launch slamcore_slam slam_publisher.launch.py
...

```

### Recording a dataset

To record a dataset using the ROS 2 wrapper, invoke the following command, with the adjustments required for your setup:

```shell
docker run --rm -it --privileged --volume /path/to/save/dataset:/output:rw --env SLAMCORE_MODE=DATASET_RECORDER slamcore-ros2 output_dir:=/output/my_dataset
```
In the example above, `--volume /path/to/save/dataset:/output` maps the host directory `/path/to/save/dataset` to the directory `/output` inside the container. You can then use the `output_dir` argument to define the dataset path inside the container. The new directory `/my_dataset` inside the container will appear in your host machine under `/path/to/save/dataset/my_dataset`.

## Subscribing to topics

Once the node is running it is possible to subscribe to the advertised topics in another docker container, for example:

```shell
docker run --rm -it --privileged --env SLAMCORE_MODE=PASSTHROUGH slamcore-ros2 ros2 topic echo /slamcore/pose
```

You can find more details on the available topics in our [ROS 2 Wrapper Advertised Topics](https://docs.slamcore.com/ros2-wrapper.html#advertised-topics) documentation section.

## Calling a service

When the node is running, you can also call the available services in another
docker container. For example the following command will allow you to save the
session file from the current session:

```shell
docker run --rm -it --privileged --env SLAMCORE_MODE=PASSTHROUGH slamcore-ros2 ros2 service call /slamcore/save_session std_srvs/Trigger
```

To get the full list of available services. You can find more details on the available services in our [ROS 2 Wrapper Advertised Services](https://docs.slamcore.com/ros2-wrapper.html#advertised-services) documentation section.

## Visualising using RViz2

You can run another container with RViz2 to visualise the
topics being published. A simple way to do this is by using a `ros:<ROS_VERSION>-desktop` image:

```shell
xhost +local:docker && docker run -it --network=host --privileged --env="DISPLAY" --env="QT_X11_NO_MITSHM=1" --volume /tmp/.X11-unix:/tmp/.X11-unix:rw osrf/ros:<ROS_VERSION>-desktop && xhost -local:docker
```

Replace `<ROS_VERSION>` with your chosen distribution: `foxy`, `galactic` or `humble`.

`xhost +local:docker` allows docker to access the X server to display graphics
before launching the container and `xhost -local:docker` removes the
permissions when exiting the container, for security.

The command above will bring up a `ros:<ROS_VERSION>-desktop` image which includes RViz2,
so you can just run the following from inside the container to open RViz2:

```shell
rviz2
```
