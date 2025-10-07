# Environment Setup

This guide provides instructions for setting up a development environment optimized for model training and evaluation. We recommend using WSL2 with a Linux distribution for better compatibility and performance.

## Prerequisites

Before starting, ensure you have:

* Windows 11 Pro with WSL2 enabled
* NVIDIA GPU with compatible drivers
* Administrative privileges on your system

# Recommended Environment

## Windows Host System
* **OS**: Windows 11 Pro 25H2
* **CUDA**: 13.0 Update 1

## WSL2 Environment
* **OS**: Fedora Linux 42 (WSL2)
* **Python**: 3.11.13
* **CUDA**: 12.8.1

# Setup Instructions (WSL Environment)

## 1. CUDA Installation

> **Important**: Ensure you have installed the latest NVIDIA GPU driver and CUDA version mentioned in the recommended environment (Windows host) before proceeding with the WSL setup.

```bash
sudo dnf update -y
sudo dnf config-manager addrepo --from-repofile https://developer.download.nvidia.com/compute/cuda/repos/fedora41/x86_64/cuda-fedora41.repo
sudo dnf clean all
sudo dnf -y install cuda-toolkit-12-8
```
## 2. Python Environment Setup

### Install pyenv and Dependencies

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add pyenv to bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

# Install build dependencies
sudo dnf install gcc openssl-devel bzip2-devel libffi-devel sqlite-devel readline-devel zlib-devel xz-devel
sudo dnf install tcl tk tcl-devel tk-devel
```

### Build and Install Tcl/Tk 8.6.14

```bash
# Build and install Tcl 8.6.14
cd /tmp
wget https://prdownloads.sourceforge.net/tcl/tcl8.6.14-src.tar.gz
tar -xzf tcl8.6.14-src.tar.gz
cd tcl8.6.14/unix
./configure --prefix=/opt/tcltk8.6
make -j$(nproc)
sudo make install

# Build and install Tk 8.6.14
cd /tmp
wget https://prdownloads.sourceforge.net/tcl/tk8.6.14-src.tar.gz
tar -xzf tk8.6.14-src.tar.gz
cd tk8.6.14/unix
./configure --prefix=/opt/tcltk8.6 --with-tcl=/opt/tcltk8.6/lib
make -j$(nproc)
sudo make install
```

### Install Python and UV Package Manager

```bash
# Install Python 3.11.13 with pyenv
export CPPFLAGS="-I/opt/tcltk8.6/include"
export LDFLAGS="-L/opt/tcltk8.6/lib -ltcl8.6 -ltk8.6"
pyenv uninstall 3.11.13  # Clean up any existing installation
PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I/opt/tcltk8.6/include' --with-tcltk-libs='/opt/tcltk8.6/lib'" pyenv install -v 3.11.13

# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync  # This will automatically install all required packages
```
## 3. Installation Validation

Verify that your installation is working correctly by running the following validation scripts:

```bash
# Check if PyTorch is installed and can utilize CUDA for computing
uv run tools/check_cuda.py

# Compare processing time between CPU and GPU to verify GPU acceleration
uv run tools/time_cpu.py
uv run tools/time_gpu.py
```

The GPU should show significantly faster processing times compared to CPU if everything is configured correctly.
