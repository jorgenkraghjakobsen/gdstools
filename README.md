# GDSTOOLS

This project requires the Qhull, zlib, and gdstk libraries to be compiled and installed before you can compile and run the code. Below are the steps to set up these dependencies.

## Prerequisites

Before proceeding, ensure you have the following tools installed:

- A C++ compiler (e.g., `g++`, `clang`)
- CMake (for Qhull and zlib)
- Git (to clone repositories)

## Step 1: Install Qhull

Qhull is a library used for computing convex hulls, Delaunay triangulations, and Voronoi diagrams.

1. **Clone the Qhull repository:**
    ```sh
    git clone https://github.com/qhull/qhull.git
    cd qhull
    ```

2. **Compile and install Qhull:**
    ```sh
    cd build
    cmake ..
    make
    sudo make install
    ```

3. **Verify the installation:** *Optional*
    Ensure that the Qhull library and headers are installed in a standard location like `/usr/local/lib` and `/usr/local/include`, or a directory included in your `CMAKE_PREFIX_PATH` or `LD_LIBRARY_PATH`.

## Step 2: Install zlib

zlib is a compression library required for handling compressed data formats.

1. **Download source and extract:**
    ```sh
    wget http://www.zlib.net/zlib-1.3.1.tar.gz
    tar -xvf zlib-1.3.1.tar.gz
    cd zlib-1.3.1
    ```

2. **Compile and install zlib:**
    ```sh
    ./configure --prefix=/usr/local/zlib
    make
    sudo make install
    ```

3. **Verify the installation:** *Optional*
    Check that the zlib library and headers are installed in the correct locations (e.g., `/usr/local/lib` and `/usr/local/include`).

## Step 3: Install gdstk

gdstk is a library for creating, manipulating, and reading GDSII files, which are used in integrated circuit layout design.

1. **Clone the gdstk repository:**
    ```sh
    git clone https://github.com/heitzmann/gdstk.git
    cd gdstk
    ```

2. **Compile and install gdstk:**
    ```sh
    cmake -S . -B build
    cmake --build build --target install
    ```

3. **Verify the installation:**
    Confirm that the gdstk library and headers are installed in the appropriate locations (e.g., `/usr/local/lib` and `/usr/local/include`).

## Step 4: Compile and run GDSTOOLS

With Qhull, zlib, and gdstk installed, you can now compile your project. Assuming you have a CMake-based project, follow these steps:

1. **Compile source:**
    ```sh
    make
    ```

2. **Run the executable:**
    ```sh
    ./list_layers
    ```
    
### Note:

- Ensure that the library paths for Qhull, zlib, and gdstk are included in your `LD_LIBRARY_PATH` or specified in your project's CMake configuration.
- If your system does not find the libraries, you may need to specify the paths explicitly during the configuration step with CMake, using flags like `-D CMAKE_PREFIX_PATH=/path/to/libs`.

## Troubleshooting

- If you encounter issues with finding the libraries, ensure that your compiler and linker can locate them. You may need to adjust environment variables like `CMAKE_PREFIX_PATH`, `LD_LIBRARY_PATH`, or `PKG_CONFIG_PATH`.
- On some systems, you might need to use `sudo` to install the libraries globally.
