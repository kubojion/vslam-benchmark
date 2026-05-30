# Dockerfile for Voxel-SVIO (RA-L 2025).
# https://github.com/ZikangYuan/voxel_svio
#
# Voxel-SVIO is a stereo MSCKF-based visual-inertial odometry that uses a
# voxel-based map. Built on ROS 1 Noetic / Ubuntu 20.04.
#
# This image installs the required system dependencies (Eigen, OpenCV 4.2,
# PCL 1.10, Ceres, glog) and Python dependencies for the data player. The
# voxel_svio package itself is built later by scripts/setup/setup_voxel_svio_docker.sh
# inside the container against the bind-mounted source tree.
FROM osrf/ros:noetic-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=noetic

# osrf/ros:noetic-desktop-full already provides:
#   - OpenCV 4.2 (libopencv-dev), PCL 1.10 (libpcl-dev), Eigen3 (libeigen3-dev)
#   - cv_bridge, image_transport, message_filters
#   - rospy + python3 sensor_msgs/cv_bridge bindings
#
# We add: Ceres (>= 1.14 needed), glog/gflags, build tools, and a few Python
# packages used by the EuRoC->ROS data player.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        libgoogle-glog-dev \
        libgflags-dev \
        libsuitesparse-dev \
        libceres-dev \
        python3-pip \
        python3-numpy \
        python3-yaml \
        python3-rospkg \
        ros-noetic-rviz \
    && rm -rf /var/lib/apt/lists/*

# Newer scikit-build on noetic has no use here; only opencv-python is needed
# in case the runtime image uses Python cv operations (the data player below
# uses cv_bridge for ROS images, not opencv-python directly, but having it
# installed is convenient for ad-hoc debugging).
RUN pip3 install --no-cache-dir opencv-python==4.5.5.64

# Workspace mountpoint - voxel_svio source is bind-mounted here at runtime.
RUN mkdir -p /root/catkin_ws/src
WORKDIR /root/catkin_ws

# Pre-source ROS in interactive shells.
RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc \
 && echo "[ -f /root/catkin_ws/devel/setup.bash ] && source /root/catkin_ws/devel/setup.bash" >> /root/.bashrc

CMD ["/bin/bash", "-c", "tail -f /dev/null"]
