#!/bin/bash

if [ -z $1 ]; then
    echo 'a version argument is required.'
    exit 1
fi

version=$1

res=$(git tag | grep $version)
if [ $? != 0 ]; then
    echo "Git tag ${version} does not exist."
    exit
fi

short=$(echo $version | awk -F . {' print $1"."$2 '})
dir=~/boss-${version}
tmpdir=$(mktemp -d -t boss-$version)

mkdir ${dir}
mkdir ${dir}/doc
mkdir ${dir}/source

# all
git archive ${version} --prefix=boss-${version}/ | gzip > ${dir}/source/boss-${version}.tar.gz
cp -a ${dir}/source/boss-${version}.tar.gz $tmpdir/

pushd $tmpdir
    tar -zxvf boss-${version}.tar.gz
    pushd boss-${version}/
        sphinx-build doc/source ${dir}/doc
    popd
popd

