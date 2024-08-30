#!/bin/zsh

_gdst_complete() {
    local -a commands opts cells files dirs

    # The current word being completed
    local cur prev
    cur="${words[CURRENT]}"
    prev="${words[CURRENT-1]}"

    # Define command names
    commands=("list_cells" "lc" "open_3d_cell" "ocv" "export_gltf" "eg" "help")

    # Completion for the main command
    if [[ "$prev" == "gdst" ]]; then
        _describe -t commands 'gdst commands' commands
        return
    fi

    # Completion options for list_cells or lc
    if [[ "$prev" == "list_cells" || "$prev" == "lc" ]]; then
        opts=("--file" "-f")
        _describe -t opts 'options' opts
        return
    fi

    # Completion options for open_3d_cell or ocv
    if [[ "$prev" == "open_3d_cell" || "$prev" == "ocv" ]]; then
        opts=("--cellname" "-c")
        _describe -t opts 'options' opts
        return
    fi

    # Completion options for export_gltf or eg
    if [[ "$prev" == "export_gltf" || "$prev" == "eg" ]]; then
        opts=("--file" "-f" "--layerstack" "-l")
        _describe -t opts 'options' opts
        return
    fi

    # File completion for --file or -f
    if [[ "$prev" == "--file" || "$prev" == "-f" ]]; then
        _files -g '*.(gds|gdsii)'
        return
    fi

    # Completion for cell names for --cellname or -c
    if [[ "$prev" == "--cellname" || "$prev" == "-c" ]]; then
        if [[ -z "$cells" ]]; then
            cells=("${(@s: :)$(gdst lc)}")
        fi
        _describe -t cells 'cell names' cells
        return
    fi

    # File or directory completion for --layerstack or -l
    if [[ "$prev" == "--layerstack" || "$prev" == "-l" ]]; then
        dirs=(${(f)"$(compgen -d)"})
        files=(${(f)"$(compgen -f)"})
        _describe -t dirs 'directories' dirs
        _describe -t files 'files' files
        return
    fi
}

compdef _gdst_complete gdst
