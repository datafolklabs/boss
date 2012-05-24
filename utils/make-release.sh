#!/bin/bash

if [ -z $1 ]; then
    echo 'a version argument is required.'
    exit 1
fi

SOURCES="src/boss"

version=$1

res=$(git tag | grep $version)
if [ $? != 0 ]; then
    echo "Git tag ${version} does not exist."
    exit
fi

short=$(echo $version | awk -F . {' print $1"."$2 '})
dir=~/cement2-${version}
tmpdir=$(mktemp -d -t cement-$version)

#if [ "${status}" != "" ]; then
#    echo
#    echo "WARNING: not all changes committed"
#fi

mkdir ${dir}
mkdir ${dir}/doc
mkdir ${dir}/source
mkdir ${dir}/pypi

# all
git archive ${version} --prefix=boss-${version}/ | gzip > ${dir}/source/boss-${version}.tar.gz
cp -a ${dir}/source/boss-${version}.tar.gz $tmpdir/

# individual
for i in $SOURCES; do
    pushd $i
    git archive ${version} --prefix=${i}-${version}/ | gzip > ${dir}/pypi/${i}-${version}.tar.gz
    popd
done

pushd $tmpdir
    tar -zxvf boss-${version}.tar.gz
    pushd boss-${version}/
        sphinx-build doc/source ${dir}/doc
    popd
popd

