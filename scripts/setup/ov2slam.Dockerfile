# OV2SLAM runtime and build environment.
# The upstream project targets ROS 1 and is isolated in Ubuntu 20.04/Noetic.
FROM osrf/ros:noetic-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
ENV CATKIN_WS=/root/catkin_ws

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        libatlas-base-dev \
        libboost-filesystem-dev \
        libboost-system-dev \
        libdw-dev \
        libeigen3-dev \
        libgflags-dev \
        libgoogle-glog-dev \
        libopencv-contrib-dev \
        libsuitesparse-dev \
        python3-opencv \
        python3-rospkg \
        ros-noetic-cv-bridge \
        ros-noetic-image-transport \
        ros-noetic-pcl-ros \
        ros-noetic-tf \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p $CATKIN_WS/src
COPY src/ov2slam $CATKIN_WS/src/ov2slam

WORKDIR $CATKIN_WS/src/ov2slam

# Build the bundled versions expected by upstream. Keeping Ceres and OV2SLAM
# on the same -march=native setting avoids Eigen alignment/ABI failures.
RUN cmake -S Thirdparty/obindex2 -B Thirdparty/obindex2/build \
        -DCMAKE_BUILD_TYPE=Release -DEnableTesting=OFF && \
    cmake --build Thirdparty/obindex2/build -j$(nproc) && \
    cmake -S Thirdparty/ibow_lcd -B Thirdparty/ibow_lcd/build \
        -DCMAKE_BUILD_TYPE=Release && \
    cmake --build Thirdparty/ibow_lcd/build -j$(nproc) && \
    cmake -S Thirdparty/Sophus -B Thirdparty/Sophus/build \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=$CATKIN_WS/src/ov2slam/Thirdparty/Sophus/install \
        -DBUILD_TESTS=OFF && \
    cmake --build Thirdparty/Sophus/build -j$(nproc) --target install && \
    cmake -S Thirdparty/ceres-solver -B Thirdparty/ceres-solver/build \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_CXX_STANDARD=14 \
        -DCMAKE_CXX_FLAGS=-march=native \
        -DCMAKE_INSTALL_PREFIX=$CATKIN_WS/src/ov2slam/Thirdparty/ceres-solver/install \
        -DBUILD_EXAMPLES=OFF \
        -DBUILD_TESTING=OFF && \
    cmake --build Thirdparty/ceres-solver/build -j$(nproc) --target install

# Ubuntu's OpenCV 4 package omits the legacy xfeatures2d BRIEF header.
# OV2SLAM's supported fallback uses ORB descriptors and keeps iBoW LC active.
RUN sed -i 's/set(WITH_OPENCV_CONTRIB ON)/set(WITH_OPENCV_CONTRIB OFF)/' \
        CMakeLists.txt && \
    sed -i 's/\bCV_GRAY2RGB\b/cv::COLOR_GRAY2RGB/g' src/ov2slam.cpp

WORKDIR $CATKIN_WS
RUN ["/bin/bash", "-c", "\
    source /opt/ros/noetic/setup.bash && \
    catkin_make -DCMAKE_BUILD_TYPE=Release -j$(nproc) \
"]

RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc && \
    echo "source $CATKIN_WS/devel/setup.bash" >> /root/.bashrc

CMD ["/bin/bash", "-c", "tail -f /dev/null"]
