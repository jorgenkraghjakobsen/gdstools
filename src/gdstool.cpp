#include "gdstool.hpp"
#include <iostream>
#include <unordered_set>
#include <cstdio>

int main(int argc, char* argv[]) {
    // Load the GDSII file
    if(argc < 2) {
        printf("Usage: %s <command>\n", argv[0]);
        printf("Commands: \n");
        printf("  - list_cells <gdsii file> || lc <gdsii file> \n");
        printf("  - open_3d_cell <cell name> || ocv <cell name>         # Uses last files that was opened with list_cells \n");
        return 1;
    }

    if(strcmp(argv[1], "list_cells") == 0 || strcmp(argv[1], "lc") == 0) {
        if(argc < 3) {
            printf("Usage: %s list_cells <gdsii file> || lc <gdsii file> \n", argv[0]);
            return 1;
        }

        std::string filename = argv[2];
        return list_cells(filename.c_str());

    } else if(strcmp(argv[1], "open_3d_cell") == 0 || strcmp(argv[1], "ocv") == 0) {
        if(argc < 3) {
            printf("Usage: %s open_3d_cell <cell name> || ocv <cell name> \n", argv[0]);
            return 1;
        }

        FILE* tmp_file = fopen(".tmp_file", "r");

        if(tmp_file == NULL) {
            printf("No file was opened with list_cells\n");
            return 1;
        }

        char filename[100];
        fscanf(tmp_file, "%s", filename);
        fclose(tmp_file);

        std::string cell_name = argv[2];

        return open_3d_cell(filename, cell_name);
    } else {
        printf("Invalid command\n");
        return 1;
    }
}

int list_cells(const char* filename) {
    double unit = 0;
    double precision = 0;

    gdstk::ErrorCode error_code = gdstk::gds_units(filename, unit, precision);
    
    if (error_code != gdstk::ErrorCode::NoError) exit(EXIT_FAILURE);
    gdstk::Library lib = gdstk::read_gds(filename, unit, precision, nullptr, &error_code);

    if (error_code != gdstk::ErrorCode::NoError) {
    // Handle the error
        printf("Failed to load GDS file: %s with code %d \n", filename, error_code);
        return 1;
    }

    for(uint64_t i = 0; i < lib.cell_array.count; i++) {
        gdstk::Cell* cell = lib.cell_array[i];
        printf("%s ", cell->name);
    }
    lib.free_all();

    // If everything went well, write file name to .tmp_file
    FILE* tmp_file = fopen(".tmp_file", "w");
    fprintf(tmp_file, "%s", filename);
    fclose(tmp_file);
    
    return 0;
}

int open_3d_cell(std::string filename, std::string cell_name) {
    // Run system command
    std::string command = "GDS3D -i " + filename + " -p sg13g2.txt -t " + cell_name;

    int ret = system(command.c_str());
    if(ret != 0) {
        printf("Failed to run GDS3D\n");
        return 1;
    }
    
    return 0;
}