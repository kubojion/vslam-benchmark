# Dockerfile for VINS-Fusion (HKUST-Aerial-Robotics).
# https://github.com/HKUST-Aerial-Robotics/VINS-Fusion
#
# Optimization-based stereo+IMU+GPS fusion. The upstream Dockerfile targets
# ROS Kinetic; we build on Noetic / Ubuntu 20.04 to match the rest of the
# benchmark stack (Voxel-SVIO, CIFASIS).
#
# Build context: $WS (so we can COPY src/VINS-Fusion).
FROM osrf/ros:noetic-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
ENV CATKIN_WS=/root/catkin_ws
# Ceres 2.1+ requires C++17 standard library. VINS-Fusion's CMakeLists
# hardcodes -std=c++11, which conflicts with Ceres 2.x's use of
# std::integer_sequence (C++14+). Pin to Ceres 1.14.0, the last release
# that supports C++11 compilers. (This is the version recommended by the
# upstream VINS-Fusion docs.)
ENV CERES_VERSION=1.14.0

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        libatlas-base-dev \
        libeigen3-dev \
        libgoogle-glog-dev \
        libgflags-dev \
        libsuitesparse-dev \
        python3-pip \
        python3-numpy \
        python3-yaml \
        python3-rospkg \
        python3-catkin-tools \
        ros-noetic-cv-bridge \
        ros-noetic-image-transport \
        ros-noetic-message-filters \
        ros-noetic-tf \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir opencv-python==4.5.5.64

# Build Ceres 1.14 (last C++11-compatible release; required for upstream
# VINS-Fusion which still uses -std=c++11).
WORKDIR /root
RUN git clone https://ceres-solver.googlesource.com/ceres-solver && \
    cd ceres-solver && git checkout tags/${CERES_VERSION} && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF && \
    make -j$(nproc) && make install && \
    cd /root && rm -rf ceres-solver

# Copy VINS-Fusion source (build context = $WS).
RUN mkdir -p $CATKIN_WS/src
COPY src/VINS-Fusion $CATKIN_WS/src/VINS-Fusion

# Patch for OpenCV 4 (Noetic ships OpenCV 4.2). VINS-Fusion uses
# pre-OpenCV-4 C-API constants that OpenCV 4 renamed. We rewrite them in
# the affected source files with sed. The mapping below covers every
# constant that appears in camera_models, loop_fusion, and vins_estimator.
RUN cd $CATKIN_WS/src/VINS-Fusion && \
    find . -type f \( -name '*.cpp' -o -name '*.cc' -o -name '*.h' -o -name '*.hpp' \) -print0 | \
    xargs -0 sed -i \
        -e 's/\bCV_AA\b/cv::LINE_AA/g' \
        -e 's/\bCV_GRAY2RGB\b/cv::COLOR_GRAY2RGB/g' \
        -e 's/\bCV_GRAY2BGR\b/cv::COLOR_GRAY2BGR/g' \
        -e 's/\bCV_BGR2GRAY\b/cv::COLOR_BGR2GRAY/g' \
        -e 's/\bCV_RGB2GRAY\b/cv::COLOR_RGB2GRAY/g' \
        -e 's/\bCV_THRESH_BINARY_INV\b/cv::THRESH_BINARY_INV/g' \
        -e 's/\bCV_THRESH_BINARY\b/cv::THRESH_BINARY/g' \
        -e 's/\bCV_RETR_CCOMP\b/cv::RETR_CCOMP/g' \
        -e 's/\bCV_RETR_EXTERNAL\b/cv::RETR_EXTERNAL/g' \
        -e 's/\bCV_CHAIN_APPROX_SIMPLE\b/cv::CHAIN_APPROX_SIMPLE/g' \
        -e 's/\bCV_CALIB_CB_ADAPTIVE_THRESH\b/cv::CALIB_CB_ADAPTIVE_THRESH/g' \
        -e 's/\bCV_CALIB_CB_NORMALIZE_IMAGE\b/cv::CALIB_CB_NORMALIZE_IMAGE/g' \
        -e 's/\bCV_CALIB_CB_FILTER_QUADS\b/cv::CALIB_CB_FILTER_QUADS/g' \
        -e 's/\bCV_CALIB_CB_FAST_CHECK\b/cv::CALIB_CB_FAST_CHECK/g' \
        -e 's/\bCV_ADAPTIVE_THRESH_MEAN_C\b/cv::ADAPTIVE_THRESH_MEAN_C/g' \
        -e 's/\bCV_SHAPE_CROSS\b/cv::MORPH_CROSS/g' \
        -e 's/\bCV_SHAPE_RECT\b/cv::MORPH_RECT/g' \
        -e 's/\bCV_TERMCRIT_EPS\b/cv::TermCriteria::EPS/g' \
        -e 's/\bCV_TERMCRIT_ITER\b/cv::TermCriteria::COUNT/g' \
        -e 's/\bCV_LOAD_IMAGE_GRAYSCALE\b/cv::IMREAD_GRAYSCALE/g' \
        -e 's/\bCV_LOAD_IMAGE_COLOR\b/cv::IMREAD_COLOR/g' \
        -e 's/\bCV_FONT_HERSHEY_SIMPLEX\b/cv::FONT_HERSHEY_SIMPLEX/g'

# Build VINS-Fusion with catkin_make.
WORKDIR $CATKIN_WS
RUN ["/bin/bash", "-c", "\
    source /opt/ros/noetic/setup.bash && \
    catkin_make -DCMAKE_BUILD_TYPE=Release -j$(nproc) \
"]

RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc && \
    echo "source $CATKIN_WS/devel/setup.bash" >> /root/.bashrc

CMD ["/bin/bash", "-c", "tail -f /dev/null"]
