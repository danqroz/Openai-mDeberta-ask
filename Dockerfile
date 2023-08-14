FROM python:3.10

# Install required packages
RUN apt-get update && apt-get install -y wget gnupg

# Download and install CUDA repository pin
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin && \
    mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600

# Download and install CUDA repository package
RUN wget https://developer.download.nvidia.com/compute/cuda/12.2.1/local_installers/cuda-repo-ubuntu2004-12-2-local_12.2.1-535.86.10-1_amd64.deb && \
    dpkg -i cuda-repo-ubuntu2004-12-2-local_12.2.1-535.86.10-1_amd64.deb

# Copy CUDA keyring
RUN cp /var/cuda-repo-ubuntu2004-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/

# Update and install CUDA
RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y cuda

# Cleanup
RUN rm cuda-repo-ubuntu2004-12-2-local_12.2.1-535.86.10-1_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables for CUDA
ENV PATH="/usr/local/cuda/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"

WORKDIR /qa

COPY Pipfile Pipfile.lock /qa/

# RUN apt-get update && apt-get install -y --no-install-recommends gcc\
#     build-essential

# Verify installation
# RUN nvcc --version && nvidia-smi

RUN pip install pipenv

# RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install


COPY . /qa/

EXPOSE 8501

CMD ["pipenv", "run", "streamlit", "run", "app/main.py"]

