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
TECH_DIR = data/tech
TECH_FILES = $(wildcard $(TECH_DIR)/*.txt)
SHARE_DIR = $(DESTDIR)/usr/local/share/gdst

# Autocompletion directories
BASH_COMPLETIONS_DIR = $(DESTDIR)$(PREFIX)/share/bash-completion/completions
ZSH_COMPLETIONS_DIR = $(DESTDIR)$(PREFIX)/share/zsh/site-functions

# Check for available shells
BASH_VERSION = $(shell bash --version 2>/dev/null | head -n 1)
ZSH_VERSION = $(shell zsh --version 2>/dev/null | head -n 1)

# Determine available shells
HAS_BASH = $(if $(BASH_VERSION),yes)
HAS_ZSH = $(if $(ZSH_VERSION),yes)

# Install the target and the Python script
install: $(TARGET)
	install -d $(DESTDIR)$(PREFIX)/bin
	install -m 755 $(TARGET) $(DESTDIR)$(PREFIX)/bin/
	install -m 755 $(PYTHON_SCRIPT) $(DESTDIR)$(PREFIX)/bin/gds2gltf

	install -d $(SHARE_DIR)
	cp -r $(LAYERSTACK_DIR)/*.txt $(SHARE_DIR)
	cp -r $(TECH_DIR)/*.txt $(SHARE_DIR)

	# Install autocompletion scripts based on SHELL_TYPE
	if [ "$(HAS_BASH)" = "yes" ]; then \
		install -d $(BASH_COMPLETIONS_DIR); \
		install -m 644 completions/gdst_completion.sh $(BASH_COMPLETIONS_DIR)/gdst; \
	fi
	if [ "$(HAS_ZSH)" = "yes" ]; then \
		install -d $(ZSH_COMPLETIONS_DIR); \
		install -m 644 completions/gdst_completion.zsh $(ZSH_COMPLETIONS_DIR)/_gdst; \
	fi

# Uninstall the target and the Python script
uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(notdir $(TARGET))
	rm -f $(DESTDIR)$(PREFIX)/bin/gds2gltf

	# Remove the text files and the directory if empty
	rm -f $(addprefix $(SHARE_DIR), $(notdir $(TECH_FILES)))
	rm -f $(addprefix $(SHARE_DIR), $(notdir $(LAYERSTACK_FILES)))
	-rmdir $(SHARE_DIR) 2>/dev/null || true

	# Remove autocompletion scripts based on SHELL_TYPE
	if [ -n "$BASH_VERSION" ]; then \
		rm -f $(BASH_COMPLETIONS_DIR)/gdst; \
	elif [ -n "$ZSH_VERSION" ]; then \
		rm -f $(ZSH_COMPLETIONS_DIR)/_gdst; \
	fi


# Clean up build artifacts
clean:
	rm -f $(TARGET)

.PHONY: install uninstall clean