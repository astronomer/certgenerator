#!/usr/bin/env bash
set -ex

usage(){ echo "Usage: tag-and-push.sh <image name> <comma separated list of tags>" ; }

# Require exactly two arguments
[ $# -eq 2 ] || { usage ; exit 1 ; }

image_name="$1"
tag_list="$2"

function docker_tag_exists() {
    curl --silent -f -lSL "https://quay.io/v1/repositories/$1/tags/$2" > /dev/null
}

function tag_and_push() {
    docker tag "${image_name}" "quay.io/astronomer/${image_name}:$1"
    docker tag "${image_name}" "astronomerinc/${image_name}:$1"
    docker push "quay.io/astronomer/${image_name}:$1"
    docker push "astronomerinc/${image_name}:$1"
}

# Split tag_list by comma
for tag in ${tag_list//,/ } ; do
    # If the tag looks starts with "v" then a digit, remove the "v"
    if [[ "$tag" =~ ^(v[0-9].*) ]] ; then
        tag="${tag:1}"
    fi
    if docker_tag_exists "astronomer/${image_name}" "${tag}" ; then
        if [[ "$tag" =~ latest|main|dev|development|release-.* ]] ; then
          tag_and_push "$tag"
        else
          echo "Skipping docker push: docker tag '${image_name}:${tag}' already exists."
        fi
    else
        tag_and_push "$tag"
    fi
done