#!/bin/bash

_gdst_complete() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    commands="list_cells lc open_3d_cell ocv export_gltf eg help"
    cells=""

    case "${prev}" in
        gdst)
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            return 0
            ;;
        list_cells|lc)
            opts="--file -f"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        open_3d_cell|ocv)
            opts="--cellname -c"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        export_gltf|eg)
            opts="--file -f --layerstack -l"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        --file|-f)
            COMPREPLY=( $(compgen -f -- ${cur} | grep -E '\.(gds|gdsii)$') )
            return 0
            ;;
        --cellname|-c)
            if [ -z "$cells" ]; then
                cells=$(gdst lc)
            fi
            COMPREPLY=( $(compgen -W "${cells}" -- ${cur}) )
            return 0
            ;;
        --layerstack|-l)
            local target_dir="/usr/local/share/gdst"

            # Use find to list text files, handle filenames with spaces
            local text_files
            text_files=$(find "$target_dir" -maxdepth 1 -type f -name '*.txt' | paste -sd " ")

            # Generate completions
            COMPREPLY=($(compgen -W "${text_files}" -- ${cur}))
            return 0
            ;;
    esac
}

complete -F _gdst_complete gdst
