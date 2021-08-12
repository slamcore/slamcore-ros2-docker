#!/usr/bin/env python3

__copyright__ = """
Copyright 2021 SLAMcore Ltd

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
import tempfile

from pathlib import Path

this_directory = Path(__file__).resolve().parent


def make_working_directory():
    return tempfile.TemporaryDirectory("-slamcore")


def create_image(debian_path: Path, docker_tag):
    deb_name = "slamcore_ros.deb"
    entrypoint_file = "entrypoint.sh"

    real_debian_path = debian_path.resolve()
    if not real_debian_path.is_file():
        raise RuntimeError(f"{debian_path} is not a file")

    with make_working_directory() as working_directory:
        tmp_dir = Path(working_directory)

        # must use hard link (docker can't build outside of context)
        shutil.copy(src=real_debian_path, dst=tmp_dir / deb_name)
        shutil.copy(src=this_directory / entrypoint_file, dst=tmp_dir / entrypoint_file)

        docker_command = (
            f"docker build --build-arg SLAMCORE_DEB={deb_name} "
            f"--build-arg ENTRYPOINT_FILE={entrypoint_file} -t {docker_tag} "
            f'-f {this_directory / "Dockerfile"} {tmp_dir}'
        )

        print(f"Running: {docker_command}")
        exit(subprocess.call(docker_command, shell=True,))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "path",
        help="Path to slamcore-ros2 debian to install in created image",
        type=Path,
    )
    parser.add_argument(
        "-t",
        "--tag",
        help="Tag to give to created image",
        type=str,
        default="slamcore-ros2",
    )

    args = parser.parse_args()

    create_image(args.path, args.tag)
