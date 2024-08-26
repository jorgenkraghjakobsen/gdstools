#!/bin/bash

_gdst_complete() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    commands="list_cells lc open_3d_cell ocv help"
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
        --file|-f)
            COMPREPLY=( $(compgen -f -- ${cur} | grep -E '\.(gds|gdsii)$') )
            return 0
            ;;
        --cellname|-c)
            # Additional logic for cell name completion can be added here
            if [ -z "$cells" ]; then
                cells=$(gdst lc)
            fi
            COMPREPLY=( $(compgen -W "${cells}" -- ${cur}) )
            return 0
            ;;
    esac
}

complete -F _gdst_complete gdst
