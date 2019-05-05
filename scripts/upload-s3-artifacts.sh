#!/usr/bin/env bash

PROFILE='imagestore'
BUCKET='http-imagestore'
KEY='xlines'

pkg_path=$(cd $(dirname $0); pwd -P)
source $pkg_path/colors.sh


function _git_root(){
    ##
    ##  determines full path to current git project root
    ##
    echo "$(git rev-parse --show-toplevel 2>/dev/null)"
}


function _valid_iamuser(){
    ##
    ##  use Amazon STS to validate credentials of iam user
    ##
    local iamuser="$1"

    if [[ $(aws sts get-caller-identity --profile $PROFILE 2>/dev/null) ]]; then
        return 0
    fi
    return 1
}


ROOT=$(_git_root)


if _valid_iamuser $PROFILE; then

    printf -- '\n'
    cd "$ROOT/assets"

    for i in $(ls .); do

        # upload object
        printf -- '\n%s\n' "s3 object $BOLD$i$UNBOLD uploaded..."
        aws --profile $PROFILE s3 cp ./$i s3://$BUCKET/$KEY/$i

        aws --profile $PROFILE s3api put-object-acl --acl 'public-read' --bucket $BUCKET --key $KEY/$i
        printf -- '%s\n' "s3 object acl applied to $i..."

    done

    printf -- '\n'
    cd "$ROOT" || true

else
    echo "You must ensure $PROFILE is present in the local awscli configuration"
fi
