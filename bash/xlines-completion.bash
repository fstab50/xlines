#!/usr/bin/env bash

# GPL v3 License
#
# Copyright (c) 2018-2019 Blake Huber
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# option strings
declare -a exceptions
exceptions=(
    'p3_env'
    'p3_venv'
    'venv'
    '.git'
    '__pycache__'
)


function _filter_objects(){
    ##
    ##  returns file objects in pwd; minus exception list members
    ##
    declare -a container fcollection

    mapfile -t fcollection < <(ls $PWD)

    for object in "${fcollection[@]}"; do
        if [[ $(echo "${exceptions[@]}" | grep $object) ]]; then
            continue
        else
            container=( "${container[@]}" "$object" )
        fi
    done
    echo "${container[@]}"
    return 0
}


function _complete_4_horsemen_commands(){
    local cmds="$1"
    local split='5'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${cur}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_region_subcommands -->
}


function _complete_4_horsemen_subcommands(){
    local cmds="$1"
    local split='3'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${cur}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_region_subcommands -->
}


function _complete_xlines_commands(){
    local cmds="$1"
    local split='6'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${COMP_WORDS[1]}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_xlines_commands -->
}


function _filedir(){
    local i IFS='
' xspec;
    _tilde "$cur" || return 0;
    local -a toks;
    local quoted x tmp;
    _quote_readline_by_ref "$cur" quoted;
    x=$( compgen -d -- "$quoted" ) && while read -r tmp; do
        toks+=("$tmp");
    done <<< "$x";
    if [[ "$1" != -d ]]; then
        xspec=${1:+"!*.@($1|${1^^})"};
        x=$( compgen -f -X "$xspec" -- $quoted ) && while read -r tmp; do
            toks+=("$tmp");
        done <<< "$x";
    fi;
    [[ -n ${COMP_FILEDIR_FALLBACK:-} && -n "$1" && "$1" != -d && ${#toks[@]} -lt 1 ]] && x=$( compgen -f -- $quoted ) && while read -r tmp; do
        toks+=("$tmp");
    done <<< "$x";
    if [[ ${#toks[@]} -ne 0 ]]; then
        compopt -o filenames 2> /dev/null;
        COMPREPLY+=("${toks[@]}");
    fi
}


function _numargs(){
    ##
    ## Returns count of number of parameter args passed
    ##
    local parameters="$1"
    local numargs

    if [[ ! "$parameters" ]]; then
        printf -- '%s\n' "0"
    else
        for i in $(echo $parameters); do
            numargs=$(( $numargs + 1 ))
        done
        printf -- '%s\n' "$numargs"
    fi
    return 0
    #
    # <-- end function _numargs -->
}


function _parse_compwords(){
    ##
    ##  Interogate compwords to discover which of the  5 horsemen are missing
    ##
    compwords=("${!1}")
    four=("${!2}")

    declare -a missing_words

    for key in "${four[@]}"; do
        if [[ ! "$(echo "${compwords[@]}" | grep ${key##*-})" ]]; then
            missing_words=( "${missing_words[@]}" "$key" )
        fi
    done
    printf -- '%s\n' "${missing_words[@]}"
    #
    # <-- end function _parse_compwords -->
}


function _pathopt(){
    ##
    ##  bash v4.4 profile reference function
    ##
    local cur prev words cword split;

    _init_completion -s || return;

    case "${prev,,}" in
        --help | --usage | --version)
            return
        ;;
        --*dir*)
            _filedir -d;
            return
        ;;
        --*file* | --*path*)
            _filedir;
            return
        ;;
        --+([-a-z0-9_]))
            local argtype=$( LC_ALL=C $1 --help 2>&1 | command sed -ne "s|.*$prev\[\{0,1\}=[<[]\{0,1\}\([-A-Za-z0-9_]\{1,\}\).*|\1|p" );
            case ${argtype,,} in
                *dir*)
                    _filedir -d;
                    return
                ;;
                *file* | *path*)
                    _filedir;
                    return
                ;;
            esac
        ;;
    esac;
    $split && return;
    if [[ "$cur" == -* ]]; then
        COMPREPLY=($( compgen -W "$( LC_ALL=C $1 --help 2>&1 | command sed -ne 's/.*\(--[-A-Za-z0-9]\{1,\}=\{0,1\}\).*/\1/p' | sort -u )" -- "$cur" ));
        [[ $COMPREPLY == *= ]] && compopt -o nospace;
    else
        if [[ "$1" == @(rmdir|chroot) ]]; then
            _filedir -d;
        else
            [[ "$1" == mkdir ]] && compopt -o nospace;
            _filedir;
        fi;
    fi
}


function compword_autofilter(){
    ##
    ##  Return compreply with any of the comp_words that
    ##  not already present on the command line
    ##

    declare -a compwords=("${!1}")
    declare -a horsemen

    horsemen=(  '--multiprocess' '--no-whitespace' '--sum' )
    subcommands=$(_parse_compwords compwords[@] horsemen[@])
    numargs=$(_numargs "$subcommands")
    if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
        _complete_4_horsemen_subcommands "${subcommands}"
    else
        COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
    fi
    return 0
}


function _xlines_completions(){
    ##
    ##  Completion structures for xlines exectuable
    ##
    local commands                  #  commandline parameters (--*)
    local subcommands               #  subcommands are parameters provided after a command
    local numargs                   #  integer count of number of commands, subcommands
    local cur                       #  completion word at index position 0 in COMP_WORDS array
    local prev                      #  completion word at index position -1 in COMP_WORDS array
    local initcmd                   #  completion word at index position -2 in COMP_WORDS array

    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    initcmd="${COMP_WORDS[COMP_CWORD-2]}"

    # initialize vars
    COMPREPLY=()
    numargs=0
    numoptions=0

    options='--help --exclusions --configure --version'
    commands='--debug --multiprocess --sum --no-whitespace'


    if [[ "$(echo "${COMP_WORDS[@]}" | grep '\-\-sum' 2>/dev/null)" ]] && \
       [[ ! "$(echo "${COMP_WORDS[@]}" | grep '\-\-multiprocess' 2>/dev/null)" ]] && \
       [[ ! "$(echo "${COMP_WORDS[@]}" | grep '\-\-no-whitespace' 2>/dev/null)" ]]; then

        case "${#COMP_WORDS[@]}" in
            #6 | 7 | 8 | 9 | 1[0-9])
            #    compword_autofilter COMP_WORDS[@]
            #    ;;

            6 | 7 | 8 | 9 | 1[0-9])
                ##
                ##  Return compreply with any of the comp_words that
                ##  not already present on the command line
                ##
                declare -a horsemen
                horsemen=(  '--multiprocess' '--no-whitespace' '--sum' )
                subcommands=$(_parse_compwords COMP_WORDS[@] horsemen[@])
                numargs=$(_numargs "$subcommands")
                if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
                    _complete_4_horsemen_subcommands "${subcommands}"
                else
                    COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
                fi
                return 0
            ;;
        esac

    elif [[ "$(echo "${COMP_WORDS[@]}" | grep '\-\-sum' 2>/dev/null)" ]] && \
       [[ "$(echo "${COMP_WORDS[@]}" | grep '\-\-multiprocess' 2>/dev/null)" ]] && \
       [[ ! "$(echo "${COMP_WORDS[@]}" | grep '\-\-no-whitespace' 2>/dev/null)" ]]; then

        case "${#COMP_WORDS[@]}" in
            [8-9] | 1[0-9])
                ##
                ##  Return compreply with any of the comp_words that
                ##  not already present on the command line
                ##
                declare -a horsemen
                horsemen=(  '--multiprocess' '--no-whitespace' '--sum' )
                subcommands=$(_parse_compwords COMP_WORDS[@] horsemen[@])
                numargs=$(_numargs "$subcommands")
                if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
                    _complete_4_horsemen_subcommands "${subcommands}"
                else
                    COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
                fi
                return 0
                ;;
        esac

    elif [[ "$(echo "${COMP_WORDS[@]}" | grep '\-\-sum' 2>/dev/null)" ]] && \
       [[ "$(echo "${COMP_WORDS[@]}" | grep '\-\-multiprocess' 2>/dev/null)" ]] && \
       [[ "$(echo "${COMP_WORDS[@]}" | grep '\-\-no-whitespace' 2>/dev/null)" ]]; then

        case "${#COMP_WORDS[@]}" in
            9 | 1[0-9])
                ##
                ##  Return compreply with any of the comp_words that
                ##  not already present on the command line
                ##
                declare -a horsemen
                horsemen=(  '--multiprocess' '--no-whitespace' '--sum' )
                subcommands=$(_parse_compwords COMP_WORDS[@] horsemen[@])
                numargs=$(_numargs "$subcommands")
                if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
                    _complete_4_horsemen_subcommands "${subcommands}"
                else
                    COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
                fi
                return 0
                ;;
        esac

    elif [[ "$(echo "${COMP_WORDS[@]}" | grep '\-\-sum' 2>/dev/null)" ]]; then
        case "${cur}" in
            '--')
                ##
                ##  Return compreply with any of the 5 comp_words that
                ##  not already present on the command line
                ##
                declare -a horsemen
                horsemen=(  '--multiprocess' '--no-whitespace' '--sum' '--debug' )
                subcommands=$(_parse_compwords COMP_WORDS[@] horsemen[@])
                numargs=$(_numargs "$subcommands")

                if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
                    _complete_4_horsemen_subcommands "${subcommands}"
                else
                    COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
                fi
                return 0
            ;;
        esac
    fi

    case "${initcmd}" in

        '--sum')
            _pathopt
            return 0
            ;;

    esac
    case "${cur}" in

        '--h')
            COMPREPLY=( $(compgen -W '--help' -- ${cur}) )
            return 0
            ;;

        '--c')
            COMPREPLY=( $(compgen -W '--configure' -- ${cur}) )
            return 0
            ;;

        '--d')
            COMPREPLY=( $(compgen -W '--debug' -- ${cur}) )
            return 0
            ;;

        '--e')
            COMPREPLY=( $(compgen -W '--exclusions' -- ${cur}) )
            return 0
            ;;

        '--m')
            COMPREPLY=( $(compgen -W '--multiprocess' -- ${cur}) )
            return 0
            ;;

        '--no')
            COMPREPLY=( $(compgen -W '--no-whitespace' -- ${cur}) )
            return 0
            ;;

        '--s')
            COMPREPLY=( $(compgen -W '--sum' -- ${cur}) )
            return 0
            ;;

        '--v')
            COMPREPLY=( $(compgen -W '--version' -- ${cur}) )
            return 0
            ;;

        'xlin' | 'xline' | 'xlines')
            COMPREPLY=( $(compgen -W "${commands} ${options}" -- ${cur}) )
            return 0
            ;;

    esac

    case "${prev}" in

        '--help' | '--exclusions' | '--version')
            return 0
            ;;

        '--configure')
            return 0
            ;;

        '--sum')
            _pathopt
            return 0
            ;;

        '--multiprocess' | '--no-whitespace' | '--debug')
            ##
            ##  Return compreply with any of the 5 comp_words that
            ##  not already present on the command line
            ##
            declare -a horsemen
            horsemen=(  '--multiprocess' '--no-whitespace' '--sum' '--debug' )
            subcommands=$(_parse_compwords COMP_WORDS[@] horsemen[@])
            numargs=$(_numargs "$subcommands")

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
                _complete_4_horsemen_subcommands "${subcommands}"
            else
                COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
            fi
            return 0
            ;;

        'xlines')
            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then

                _complete_xlines_commands "${commands} ${options}"
                return 0

            fi
            ;;

        *)
            _pathopt
            return 0
            ;;

    esac

    COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )

} && complete -F _xlines_completions xlines
