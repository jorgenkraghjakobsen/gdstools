#include "gdstool.h"
#include <iostream>
#include <unordered_set>
#include <cstdio>
#include <cstdlib>
#include <unistd.h>
#include <sys/stat.h>
#include <curl/curl.h>

int main(int argc, char* argv[]) {
    try {
        cxxopts::Options options(argv[0], "GDSII Tool - A tool for handling GDSII files");

        options.add_options()
            ("h,help", "Print usage")
            ("f,file", "GDSII file", cxxopts::value<std::string>())
            ("c,cellname", "Cell name", cxxopts::value<std::string>())
            ("l,layerstack", "Layer stack file", cxxopts::value<std::string>());

        cxxopts::ParseResult result = options.parse(argc, argv);

        if (result.count("help") || argc < 2) {
            print_help(options);
            return 0;
        }

        std::string command = argv[1];

        if (command == "list_cells" || command == "lc") {
            std::string filename;
            auto lib = read_gds_file(result, filename);
            if (lib == nullptr) {
                return 1;
            }


            list_cells(*lib);
            lib->free_all();
            save_filename_to_file(filename);

            return 0;


        } else if (command == "open_3d_cell" || command == "ocv") {
            if (!result.count("cellname")) {
                printf("Error: Cell name not specified\n");
                print_help(options);
                return 1;
            }

            std::string filename = get_filename_from_file();
            if(filename == "") {
                printf("Error: GDSII file not specified and cant be read from file\n");
                return 1;
            }

            std::string cell_name = result["cellname"].as<std::string>();
            return open_3d_cell(filename, cell_name);

        } else if (command == "export_gltf" || command == "eg") {
            printf("Exporting to GLTF\n");
            // Call the Python script to perform the conversion
            std::string filename;
            std::string layerstack;
            if (!result.count("file")) {
                filename = get_filename_from_file();
                if (filename == "") {
                    printf("Error: GDSII file not specified\n");
                    return 1;
                }

            } else {
                filename = result["file"].as<std::string>();
            }

            if(!result.count("layerstack")) {
                printf("Error: Layer stack file not specified\n");
                return 1;
            } else {
                if(!check_file_exists(result["layerstack"].as<std::string>())) {
                    if(!check_file_exists("/usr/local/share/gdst/" + result["layerstack"].as<std::string>())) {
                        printf("Error: Layer stack file does not exist\n");
                        return 1;

                    } else {
                        layerstack = "/usr/local/share/gdst/" + result["layerstack"].as<std::string>();
                    }

                } else {
                layerstack = result["layerstack"].as<std::string>();

                }
            }

            return export_gltf_file(filename, layerstack);

            return 0;

        } else {
            printf("Invalid command\n");
            print_help(options);
            return 1;
        }
    } catch (const cxxopts::exceptions::exception& e) {
        printf("Error parsing options: %s\n", e.what());
        return 1;
    }
}

int print_help(cxxopts::Options& options) {
    printf("%s\n", options.help().c_str());
    printf("Commands:\n");
    printf("  list_cells, lc        - List cells in a GDSII file\n");
    printf("  open_3d_cell, ocv     - Open a 3D view of a cell\n");
    printf("  export_gltf, eg       - Export GDSII file to GLTF\n");
    return 0;
}

std::string get_filename_from_file() {
    FILE* tmp_file = fopen("/var/tmp/.tmp_gdst_file", "r");
    if (tmp_file == NULL) {
        printf("No file was opened with list_cells\n");
        return "";
    }

    char filename[100];
    fscanf(tmp_file, "%s", filename);
    fclose(tmp_file);

    return std::string(filename);
}

bool check_file_exists(const std::string& filename) {
    struct stat buffer;
    return (stat(filename.c_str(), &buffer) == 0);
}

int save_filename_to_file(const std::string& filename) {
    FILE* tmp_file = fopen("/var/tmp/.tmp_gdst_file", "w");
    if (tmp_file == NULL) {
        printf("Failed to open .tmp_file\n");
        return 1;
    }
    char full_path[4096];

    char* res = realpath(filename.c_str(), full_path);
    if (res == NULL) {
        printf("Failed to get the full path: %s\n", strerror(errno));
        perror("Failed to get the full path");
        return 1;
    }
    fprintf(tmp_file, "%s\n", full_path);
    fclose(tmp_file);
    return 0;
}

std::unique_ptr<gdstk::Library> read_gds_file(cxxopts::ParseResult result, std::string& fname) {
    double unit = 0;
    double precision = 0;
    std::string filename;
    if (!result.count("file")) {
        filename = get_filename_from_file();
        if (filename == "") {
            printf("Error: GDSII file not specified\n");
            return nullptr;
        }

    } else {
        filename = result["file"].as<std::string>();
    }

    // Copy filename to fname
    fname = filename;

    gdstk::ErrorCode error_code = gdstk::gds_units(filename.c_str(), unit, precision);
    if (error_code != gdstk::ErrorCode::NoError) {
        printf("Failed to load GDS file: %s with code %d\n", filename, error_code);
        return nullptr;
    }
    auto lib = std::make_unique<gdstk::Library>();
    *lib = gdstk::read_gds(filename.c_str(), unit, precision, nullptr, &error_code);

    if (error_code != gdstk::ErrorCode::NoError) {
        printf("Failed to load GDS file: %s with code %d\n", filename, error_code);
        return nullptr;
    }

    return lib;
}

int list_cells(gdstk::Library lib) {
    for (uint64_t i = 0; i < lib.cell_array.count; i++) {
        gdstk::Cell* cell = lib.cell_array[i];
        printf("%s ", cell->name);
    }
    printf("\n");
    return 0;
}

int open_3d_cell(const std::string& filename, const std::string& cell_name) {
    // Run system command
    std::string command = "GDS3D -i " + filename + " -p sg13g2.txt -t " + cell_name;

    int ret = system(command.c_str());
    if (ret != 0) {
        printf("Failed to run GDS3D\n");
        return 1;
    }

    return 0;
}

int export_gltf_file(const std::string& filename, const std::string& layerstack) {
    // Call the Python script to perform the conversion
    std::string command = "gds2gltf " + filename + " " + layerstack;
    int result = system(command.c_str());
    
    if (result == 0) {
        printf("GLTF export successful\n");
    } else {
        printf("GLTF export failed\n");
        printf("Command: %s\n", command.c_str());
        printf("Result: %d\n", result); 
        printf("Check if gds2gltf and libraries is installed\n");
        return 1;
    }

    // Ask if user wants to upload the file to the server
    std::string upload;
    printf("Do you want to upload the file to the server? (y/n): ");
    std::cin >> upload;

    if (upload != "y" && upload != "Y") {
        return 0;
    }

    // Upload the file to the server
    CURL *curl;
    CURLcode res;
    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();
    std::string upload_filename = filename + ".glb";
    if (curl) {
        const char* url = "https://anyvej11.dk/vr/upload_files";
        curl_mime *mime;
        curl_mimepart *part;

        mime = curl_mime_init(curl);

        part = curl_mime_addpart(mime);
        curl_mime_name(part, "uploaded_file");
        curl_mime_filedata(part, upload_filename.c_str());

        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_MIMEPOST, mime);

        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
            return 1;
        }

        curl_easy_cleanup(curl);
        curl_mime_free(mime);
    }

    curl_global_cleanup();
    printf("File uploaded to server. \n");
    printf("URL: https://anyvej11.dk/vr/\n");

    return 0;
}