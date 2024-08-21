#include <gdstk/gdstk.hpp>
#include <iostream>
#include <unordered_set>
#include <cstdio>

int main(int argc, char* argv[]) {
    // Load the GDSII file
    char filename[64];
    // const char* filename = "sg13g2_stdcell.gds";  // Replace with your GDSII file
    printf("argc: %d\n", argc);
    if(argc < 2) {
        printf("Usage: %s <gdsii file>\n", argv[0]);
        return 1;
    }
    strcpy(filename, argv[1]);
    // printf("Enter the GDSII file name: ");
    // printf(fgets(filename, 32, stdin))
    // if(fgets(filename, 32, stdin) != 0) {
    //     printf("Error reading file name\n");
    // };

    gdstk::Set<long unsigned int> layers;
    gdstk::ErrorCode error_code;

    printf("Reading GDS file: %s\n", filename);

    gdstk::Library lib = gdstk::read_gds(filename, 0, 0, &layers, &error_code);

    if (error_code != gdstk::ErrorCode::NoError) {
    // Handle the error
        printf("Failed to load GDS file: %s\n", filename);
        return 1;
    }
    printf("Successfully loaded GDS file: %s\n", filename);

    for(uint64_t i = 0; i < lib.cell_array.count; i++) {
        gdstk::Cell* cell = lib.cell_array[i];
        printf("Cell name: %s\n", cell->name);
    }

    return 0;
}
