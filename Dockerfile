FROM ubuntu:22.04
MAINTAINER funnybrum@gmial.com

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get -y install apt-utils cron python3 python3-pip python3-opencv python3-venv ffmpeg tzdata curl nano wget
RUN apt-get -y install libmfx1 libmfx-tools libva-drm2 libva-x11-2 vainfo intel-media-va-driver-non-free ocl-icd-libopencl1

RUN wget -q -O /tmp/tmp.deb https://github.com/intel/compute-runtime/releases/download/23.52.28202.14/libigdgmm12_22.3.11_amd64.deb \
  && dpkg -i /tmp/tmp.deb \
  && rm /tmp/tmp.deb

RUN wget -q -O /tmp/tmp.deb https://github.com/intel/intel-graphics-compiler/releases/download/igc-1.0.15770.11/intel-igc-core_1.0.15770.11_amd64.deb \
  && dpkg -i /tmp/tmp.deb \
  && rm /tmp/tmp.deb

RUN wget -q -O /tmp/tmp.deb https://github.com/intel/intel-graphics-compiler/releases/download/igc-1.0.15770.11/intel-igc-opencl_1.0.15770.11_amd64.deb \
  && dpkg -i /tmp/tmp.deb \
  && rm /tmp/tmp.deb

RUN wget -q -O /tmp/tmp.deb https://github.com/intel/compute-runtime/releases/download/23.52.28202.14/intel-level-zero-gpu_1.3.28202.14_amd64.deb \
  && dpkg -i /tmp/tmp.deb \
  && rm /tmp/tmp.deb

RUN wget -q -O /tmp/tmp.deb https://github.com/intel/compute-runtime/releases/download/23.52.28202.14/intel-opencl-icd_23.52.28202.14_amd64.deb \
  && dpkg -i /tmp/tmp.deb \
  && rm /tmp/tmp.deb

WORKDIR /app

# 1. Create the virtual environment
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV

# 2. Update PATH so standard commands utilize the venv automatically
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 3. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src
COPY config/ ./config
COPY model/ ./model

# Set the entrypoint
ENTRYPOINT ["python3", "-m", "src.monitor"]
