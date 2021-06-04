#! /usr/bin/env bash

set -Eeuo pipefail

usage() {
    cat <<EOF
Usage: $(basename "${0}") [-h] [-p]

Disable network card offload features: tso off gso off gro.

Available options

-h, --help     Print help message
-p, --prefix   Only apply to network with parm as prefix
EOF
    exit
}

msg() {
    echo >&2 -e "${1-}"
}

die() {
    local msg=${1}
    local code=${2-1}
    msg "${msg}"
    exit "${code}"
}

parse_params() {
    flag=0
    prefix=''

    while :; do
        case "${1-}" in
        -h | --help) usage ;;
        -p | --prefix)
            prefix="${2-}"
            shift
            ;;
        -?*) die "Unknown option: ${1}" ;;
        *) break ;;
        esac
        shift
    done

    args=("$@")
    return 0
}

parse_params "${@}"

if [ ${prefix-} ]; then
    Active_netcard=$(ip addr show | awk '/inet.*brd/{print $NF}' | awk "/^${prefix}*/{print}")
else
    Active_netcard=$(ip addr show | awk '/inet.*brd/{print $NF}')
fi
echo $Active_netcard
ethtool -K $Active_netcard tso off gso off gro off
