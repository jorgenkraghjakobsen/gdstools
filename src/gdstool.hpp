// gdstool.h
#ifndef GDSTOOL_H
#define GDSTOOL_H

#include <gdstk/gdstk.hpp>
#include <string>

// Function declarations
int list_cells(const char* filename);
int open_3d_cell(std::string filename, std::string cell_name);

#endif // GDSTOOL_H
