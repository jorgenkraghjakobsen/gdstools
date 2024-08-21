#include <gdstk/gdstk.hpp>
#include <iostream>
#include <unordered_set>
#include <cstdio>

int main(int argc, char* argv[]) {
    // Load the GDSII file

    // const char* filename = "sg13g2_stdcell.gds";  // Replace with your GDSII file
    printf("argc: %d\n", argc);
    if(argc < 2) {
        printf("Usage: %s <gdsii file>\n", argv[0]);
        return 1;
    }
    std::string filename = argv[1];

    double unit = 0;
    double precision = 0;

    gdstk::ErrorCode error_code = gdstk::gds_units(filename.c_str(), unit, precision);
   if (error_code != gdstk::ErrorCode::NoError) exit(EXIT_FAILURE);
   
    printf("Unit: %g\n", unit);
    printf("Precision: %g\n", precision);

    printf("Reading GDS file: %s\n", filename);

    gdstk::Library lib = gdstk::read_gds(filename.c_str(), unit, precision, nullptr, &error_code);

    if (error_code != gdstk::ErrorCode::NoError) {
    // Handle the error
        printf("Failed to load GDS file: %s with code %d \n", filename, error_code);
        return 1;
    }
    printf("Successfully loaded GDS file: %s\n", filename);

    for(uint64_t i = 0; i < lib.cell_array.count; i++) {
        gdstk::Cell* cell = lib.cell_array[i];
        printf("Cell name: %s\n", cell->name);
    }
    lib.free_all();
    return 0;
}
