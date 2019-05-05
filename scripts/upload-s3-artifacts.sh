#!/usr/bin/env bash

PROFILE='gcreds-da-atos'
BUCKET='http-imagestore'
KEY='xlines'



function _git_root(){
    ##
    ##  determines full path to current git project root
    ##
    echo "$(git rev-parse --show-toplevel 2>/dev/null)"
}




ROOT=$(_git_root)

if [[ "$(gcreds -s | grep $PROFILE)" ]] && [[ ! "$(gcreds -s | grep expired)" ]]; then

    cd "$ROOT/assets"

    for i in $(ls .); do

        # upload object
        aws --profile $PROFILE s3 cp ./$i s3://$BUCKET/$KEY/$i
        echo "s3 object $i uploaded..."

        aws --profile $PROFILE s3api put-object-acl --acl 'public-read' --bucket $BUCKET --key $KEY/$i
        echo "s3 object acl applied to $i..."

    done
    cd "$ROOT" || true

else
    echo "You must rerun gcreds to generate temporary credentials for $(PROFILE)"
fi
