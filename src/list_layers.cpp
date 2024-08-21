#include <gdstk/gdstk.hpp>
#include <iostream>
#include <unordered_set>
#include <cstdio>

int main() {
    // Load the GDSII file
    const char* filename = "sg13g2_stdcell.gds";  // Replace with your GDSII file
    // gdstk::LibraryInfo lib_info = gdstk::gds_info(filename);
    // gdstk::gds_info(filename, lib_info);
    
    // gdstk::Library lib = gdstk::read_gds(filename, );
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
    // printf("Number of cells: %ld\n", lib.cell_array.index);

    lib.cell_array.print(true);

    // for (gdstk::Cell* cell : lib.cell_array) {
    //     printf("Cell name: %s\n", cell->name);
    // }
    for(int i = 0; i < lib.cell_array.count; i++) {
        gdstk::Cell* cell = lib.cell_array[i];
        printf("Cell name: %s\n", cell->name);
    }

    // // Create a set to store unique layers
    // std::unordered_set<int> unique_layers;

    // // Iterate over all cells in the library
    // for (const gdstk::Cell* cell : lib.cell_array) {
    //     // Iterate over all polygons in the cell
    //     for (const gdstk::Polygon& polygon : cell->polygon_array) {
    //         unique_layers.insert(polygon.layer);
    //     }

    //     // Iterate over all paths in the cell
    //     for (const gdstk::FlexPath& path : cell->flexpath_array) {
    //         for (const gdstk::FlexPathElement& element : path.elements) {
    //             unique_layers.insert(element.layer);
    //         }
    //     }

    //     // Iterate over all labels in the cell
    //     for (const gdstk::Label& label : cell->label_array) {
    //         unique_layers.insert(label.layer);
    //     }
    // }

    // // Print all unique layers
    // std::cout << "Layers in the GDSII file:" << std::endl;
    // for (int layer : unique_layers) {
    //     std::cout << "Layer " << layer << std::endl;
    // }

    return 0;
}
