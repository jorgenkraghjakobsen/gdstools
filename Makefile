# BUILD AND COMPILE GDSTOOLS

# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -O2

# Libraries to link against
LIBS = -lgdstk -lz -lqhull -lqhull_r -lclipper

# Source files
SRC = src/gdst.cpp

# Output binary
TARGET = build/gdst

# Build the target
$(TARGET): $(SRC)
	mkdir -p build
	$(CXX) $(CXXFLAGS) $(SRC) $(LIBS) -o $(TARGET)


# INSTALLATION

# Python script to install
PYTHON_SCRIPT = src/gds2gltf.py

# Installation directory
PREFIX = /usr/local

# Install the target and the Python script
install: $(TARGET)
	install -d $(DESTDIR)$(PREFIX)/bin
	install -m 755 $(TARGET) $(DESTDIR)$(PREFIX)/bin/
	install -m 755 $(PYTHON_SCRIPT) $(DESTDIR)$(PREFIX)/bin/gds2gltf

# Uninstall the target and the Python script
uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(notdir $(TARGET))
	rm -f $(DESTDIR)$(PREFIX)/bin/gds2gltf


# Clean up build artifacts
clean:
	rm -f $(TARGET)

.PHONY: install uninstall clean