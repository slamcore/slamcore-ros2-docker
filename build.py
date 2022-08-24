#!/usr/bin/env python3
"""Build a Docker image to use with the Slamcore software."""

__copyright__ = """
Copyright 2023 Slamcore Ltd

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions
    and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
    and the following disclaimer in the documentation and/or other materials provided with the
    distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse
    or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import errno
import os

this_directory = Path(__file__).resolve().parent


def make_working_directory():
    return tempfile.TemporaryDirectory("-slamcore")


def resolve_path(path: Path) -> Path:
    resolved_path = path.resolve()
    if not resolved_path.is_file():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
    return resolved_path


def create_image(
    ros_debian_path: Path, dev_debian_path: Path, docker_tag: str, ros_version: str
):
    # names in the temporary directory
    ros_deb_name = "slamcore-ros.deb"
    dev_deb_name = "slamcore-dev.deb"
    entrypoint_file = "entrypoint.sh"

    ros_path_resolved = resolve_path(ros_debian_path)
    dev_path_resolved = resolve_path(dev_debian_path)

    with make_working_directory() as working_directory:
        tmp_dir = Path(working_directory)

        # must use hard link (docker can't build outside of context)
        shutil.copy(src=ros_path_resolved, dst=tmp_dir / ros_deb_name)
        shutil.copy(src=dev_path_resolved, dst=tmp_dir / dev_deb_name)
        shutil.copy(src=this_directory / entrypoint_file, dst=tmp_dir / entrypoint_file)

        docker_command = (
            f"docker build --build-arg ROS_VERSION={ros_version} --build-arg SLAMCORE_ROS_DEB={ros_deb_name} "
            f"--build-arg SLAMCORE_DEV_DEB={dev_deb_name} "
            f"--build-arg ENTRYPOINT_FILE={entrypoint_file} -t {docker_tag} "
            f'-f {this_directory / "Dockerfile"} {tmp_dir}'
        )

        print(f"Running:\n\n\t{docker_command}\n")
        exit(
            subprocess.call(
                docker_command,
                shell=True,
            )
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        __doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    executable = Path(sys.argv[0]).stem
    default_tag = "slamcore-ros2"
    usecases = {
        f'Create the docker image, use ROS2 Foxy, default name "{default_tag}"': "--ros foxy path/to/ros-foxy-slamcore-ros.deb path/to/slamcore-dev.deb",
        'Create the docker image, use ROS2 Galactic, name it "myimage"': "--tag myimage --ros galactic path/to/ros-galactic-slamcore-ros.deb path/to/slamcore-dev.deb",
    }
    parser.epilog = f'Usage examples:\n{"=" * 15}\n\n' + "\n".join(
        (f"- {k}\n  {executable} {v}\n" for k, v in usecases.items())
    )

    parser.add_argument(
        "ros_path",
        help="Path to slamcore-ros2 debian to install in created image",
        type=Path,
    )
    parser.add_argument(
        "dev_path",
        help="Path to slamcore-dev debian to install in created image",
        type=Path,
    )
    parser.add_argument(
        "-t",
        "--tag",
        help="Tag to give to created image",
        type=str,
        default=default_tag,
    )
    parser.add_argument(
        "-r",
        "--ros",
        help="ROS Version to use in the created image",
        type=str,
        choices=("foxy", "galactic"),
        required=True,
    )

    args = parser.parse_args()
    create_image(args.ros_path, args.dev_path, args.tag, args.ros)
