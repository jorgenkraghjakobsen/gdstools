# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -O2

# Libraries to link against
LIBS = -lgdstk -lz -lqhull -lqhull_r -lclipper

# Source files
SRC = src/gdstool.cpp

# Output binary
TARGET = build/gdstool

# Build the target
$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) $(LIBS) -o $(TARGET)

# Clean up build artifacts
clean:
	rm -f $(TARGET)
