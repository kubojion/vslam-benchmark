# Dockerfile for CIFASIS GNSS-Stereo-Inertial Fusion (Cremona et al., 2023).
# https://github.com/CIFASIS/gnss-stereo-inertial-fusion
#
# CIFASIS GNSS-SI is a tightly-coupled extension of ORB-SLAM3 that fuses
# GNSS measurements into the stereo-inertial pipeline. Built on ROS 1
# Noetic / Ubuntu 20.04. Upstream provides its own Dockerfile that already
# installs Pangolin + GeographicLib + builds the project; we wrap that with
# our own apt additions for Python tooling used by the data player.
#
# IMPORTANT: this image is built with build context = $WS/src/cifasis_gnss_si
# (i.e. the upstream repo root) so that the upstream `COPY ./` directive
# captures the source tree. See scripts/setup/setup_cifasis_gnss_si_docker.sh.
FROM ros:noetic-perception

ENV CATKIN_WS=/root/catkin_ws \
    GNSS_SI_ROOT=/root/catkin_ws/src/gnss-stereo-inertial-fusion/
ENV DEBIAN_FRONTEND=noninteractive

# Build dependencies (mirrors upstream Dockerfile + extras for our data player).
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils && \
    apt-get install -y --no-install-recommends \
        git \
        python3-pip \
        python3-numpy \
        python3-yaml \
        python3-rospkg \
        libgeographic-dev \
        libglew-dev \
        libssl-dev \
        ros-noetic-cv-bridge \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir opencv-python==4.5.5.64

# Build Pangolin (matches upstream's pinned commit).
WORKDIR /root
RUN mkdir -p src && cd src && \
    git clone https://github.com/stevenlovegrove/Pangolin.git && \
    cd Pangolin && \
    git checkout 86eb4975fc4fc8b5d92148c2e370045ae9bf9f5d && \
    mkdir build && cd build && \
    cmake .. && cmake --build . -- -j$(nproc) && \
    cmake --install .

# Copy the upstream source tree into the catkin workspace.
COPY ./ $GNSS_SI_ROOT

# Build (Thirdparty + library + ROS node).
WORKDIR $GNSS_SI_ROOT
RUN chmod +x modify_entrypoint.sh && sync && ./modify_entrypoint.sh
RUN ["/bin/bash", "-c", "\
    chmod +x build.sh build_ros.sh && \
    source /opt/ros/$ROS_DISTRO/setup.bash && \
    export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:$GNSS_SI_ROOT/Examples/ROS && \
    ./build.sh && ./build_ros.sh \
"]

# Pre-source ROS in interactive shells.
RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc && \
    echo "export ROS_PACKAGE_PATH=\$ROS_PACKAGE_PATH:$GNSS_SI_ROOT/Examples/ROS" \
        >> /root/.bashrc

CMD ["/bin/bash", "-c", "tail -f /dev/null"]
