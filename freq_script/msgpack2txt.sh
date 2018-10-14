#!/bin/sh

# folders to use
workdir="temp/"
finaldir="freq_dict/"

# create them if they do not exists
mkdir "$workdir"
mkdir "$finaldir"

# this function is called for any .msgpack.gz file
function convertmp {
  unzip="/c/Program Files/7-Zip/7z"
  conv="./msgpack-cli.exe"
  echo ==============================;
  filename="${1##*/}"
  filename="${filename%.gz}"
  echo "${1} ==> "${workdir}${filename}" ==> ${workdir}${filename%.msgpack}.json ==> ${finaldir}${filename%.msgpack}.txt"
  "$unzip" e -aoa "$1" -o"$workdir"
  "$conv" decode "${workdir}${filename}" --out="${workdir}${filename%.msgpack}.json"
  grep -oE '\[".*' "${workdir}${filename%.msgpack}.json" | grep -oE '"[^0-9[]*"' | sed 's/","/\n/g' | sed 's/"//g' | sed -r '/^.{,4}$/d' > "${finaldir}${filename%.msgpack}.txt"
}

# export some variables to use them inside sub bash process
export -f convertmp
export workdir
export finaldir

# clone the original frequecy files in a subfolder wordfreq
git clone --depth=1 https://github.com/LuminosoInsight/wordfreq.git wordfreq

# loop over all .msgpack.gz files
find . -type f -name *.msgpack.gz -exec bash -c 'convertmp "$0"' {} \;

# remove the temporary data
rm -r "$workdir"
