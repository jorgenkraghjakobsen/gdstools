#compdef gdst

_gdst_complete() {
    local cur prev opts commands cells

    _arguments \
        '1: :->command' \
        '2: :->option' \
        '3: :->value' \
        && return 0

    case "$state" in
        command)
            commands=("list_cells" "lc" "open_3d_cell" "ocv" "export_gltf" "eg" "help")
            _describe 'command' commands
            ;;
        option)
            case "$prev" in
                list_cells|lc)
                    opts=("--file" "-f")
                    _describe 'option' opts
                    ;;
                open_3d_cell|ocv)
                    opts=("--cellname" "-c")
                    _describe 'option' opts
                    ;;
                export_gltf|eg)
                    opts=("--file" "-f" "--layerstack" "-l")
                    _describe 'option' opts
                    ;;
                --file|-f)
                    _files -g '*.(gds|gdsii)'
                    ;;
                --cellname|-c)
                    if [ -z "$cells" ]; then
                        cells=$(gdst lc)
                    fi
                    _describe 'cell name' ${(f)cells}
                    ;;
                --layerstack|-l)
                    local directories files
                    directories=($(compgen -d -S / -- "$cur"))
                    files=($(compgen -f -- "$cur" | grep -E '\.(txt)$'))
                    _describe 'file or directory' "${directories[@]}" "${files[@]}"
                    ;;
            esac
            ;;
    esac
}

compdef _gdst_complete gdst
