# Stream2Prompt

## Requirements
- Python 3.11+
- Cuda 12.8+
- UV 0.9.0+

uv run label-studio start

## Common Issues
### Install python 3.11.13 with pyenv on fedora 42
The system Tcl and Tk libraries are too new. Install 8.6.14 with the following procedures:
```bash
# Install dependencies
sudo dnf install gcc openssl-devel bzip2-devel libffi-devel sqlite-devel readline-devel zlib-devel xz-devel
sudo dnf install tcl tk tcl-devel tk-devel
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
# Install Python 3.11.13 with pyenv
export CPPFLAGS="-I/opt/tcltk8.6/include"
export LDFLAGS="-L/opt/tcltk8.6/lib -ltcl8.6 -ltk8.6"
pyenv uninstall 3.11.13  # Clean up
PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I/opt/tcltk8.6/include' --with-tcltk-libs='/opt/tcltk8.6/lib'" pyenv install -v 3.11.13
```
