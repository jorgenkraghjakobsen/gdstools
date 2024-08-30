// gdstool.h
#ifndef GDSTOOL_H
#define GDSTOOL_H

#include <gdstk/gdstk.hpp>
#include <string>
#include "cxxopts.hpp"


// Function declarations
int print_help(cxxopts::Options& options);

std::string get_filename_from_file();
bool check_file_exists(const std::string& filename);
int save_filename_to_file(const std::string& filename);
std::unique_ptr<gdstk::Library> read_gds_file(cxxopts::ParseResult result, std::string& fname);

int list_cells(gdstk::Library lib);
int open_3d_cell(const std::string& filename, const std::string& cell_name);

#endif // GDSTOOL_H
