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
	$(CXX) $(CXXFLAGS) $(SRC) $(LIBS) -o $(TARGET)


# INSTALLATION

# Python script to install
PYTHON_SCRIPT = src/gds2gltf.py

# Installation directory
PREFIX = /usr/local
LAYERSTACK_DIR = data/layerstack
LAYERSTACK_FILES = $(wildcard $(LAYERSTACK_DIR)/*.txt)
SHARE_DIR = $(DESTDIR)/usr/local/share/gdst

# Install the target and the Python script
install: $(TARGET)
	install -d $(DESTDIR)$(PREFIX)/bin
	install -m 755 $(TARGET) $(DESTDIR)$(PREFIX)/bin/
	install -m 755 $(PYTHON_SCRIPT) $(DESTDIR)$(PREFIX)/bin/gds2gltf

	install -d $(SHARE_DIR)
	cp -r $(LAYERSTACK_DIR)/*.txt $(SHARE_DIR)

# Uninstall the target and the Python script
uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(notdir $(TARGET))
	rm -f $(DESTDIR)$(PREFIX)/bin/gds2gltf

	# Remove the text files and the directory if empty
	rm -f $(addprefix $(SHARE_DIR), $(notdir $(LAYERSTACK_FILES)))
	-rmdir $(SHARE_DIR) 2>/dev/null || true


# Clean up build artifacts
clean:
	rm -f $(TARGET)

.PHONY: install uninstall clean