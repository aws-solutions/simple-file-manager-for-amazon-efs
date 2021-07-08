#!/bin/bash
######################################################################################################################
#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                #
#                                                                                                                    #
#  Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    #
#  with the License. A copy of the License is located at                                                             #
#                                                                                                                    #
#      http://www.apache.org/licenses/LICENSE-2.0                                                                    #
#                                                                                                                    #
#  or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES #
#  OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    #
#  and limitations under the License.                                                                                #
######################################################################################################################


###############################################################################
# PURPOSE:
#   Build cloud formation templates for the %%%%%%%%
# USAGE:
#  ./build-s3-dist.sh [-h] [-v] [--no-layer] --template-bucket {TEMPLATE_BUCKET} --code-bucket {CODE_BUCKET} --version {VERSION} --region {REGION}
#    TEMPLATE_BUCKET should be the name for the S3 bucket location where %%%%
#      cloud formation templates should be saved.
#    CODE_BUCKET should be the name for the S3 bucket location where cloud
#      formation templates should find Lambda source code packages.
#    VERSION should be in a format like v1.0.0
#    REGION needs to be in a format like us-east-1
#
#    The following options are available:
#
#     -h | --help       Print usage
#     -v | --verbose    Print script debug info
#
###############################################################################

trap cleanup_and_die SIGINT SIGTERM ERR

usage() {
  msg "$msg"
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-v] --template-bucket TEMPLATE_BUCKET --code-bucket CODE_BUCKET --version VERSION --region REGION
Available options:
-h, --help        Print this help and exit (optional)
-v, --verbose     Print script debug info (optional)
--template-bucket S3 bucket to put cloud formation templates
--code-bucket     S3 bucket to put Lambda code packages
--version         Arbitrary string indicating build version
--region          AWS Region, formatted like us-west-2
EOF
  exit 1
}

cleanup_and_die() {
  trap - SIGINT SIGTERM ERR
  echo "Trapped signal."
  cleanup
  die 1
}

cleanup() {
  # Deactivate and remove the temporary python virtualenv used to run this script
  if [[ "$VIRTUAL_ENV" != "" ]];
  then
    deactivate
    #rm -rf "$VENV"
    echo "------------------------------------------------------------------------------"
    echo "Cleaning up complete"
    echo "------------------------------------------------------------------------------"
  fi
}

msg() {
  echo >&2 -e "${1-}"
}

die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  msg "$msg"
  exit "$code"
}

parse_params() {
  # default values of variables set from params
  flag=0
  param=''

  while :; do
    case "${1-}" in
    -h | --help) usage ;;
    -v | --verbose) set -x ;;
    --template-bucket)
      global_bucket="${2}"
      shift
      ;;
    --code-bucket)
      regional_bucket="${2}"
      shift
      ;;
    --version)
      version="${2}"
      shift
      ;;
    --region)
      region="${2}"
      shift
      ;;
    -?*) die "Unknown option: $1" ;;
    *) break ;;
    esac
    shift
  done

  args=("$@")

  # check required params and arguments
  [[ -z "${global_bucket}" ]] && usage "Missing required parameter: template-bucket"
  [[ -z "${regional_bucket}" ]] && usage "Missing required parameter: code-bucket"
  [[ -z "${version}" ]] && usage "Missing required parameter: version"
  [[ -z "${region}" ]] && usage "Missing required parameter: region"

  return 0
}

parse_params "$@"
msg "Build parameters:"
msg "- Template bucket: ${global_bucket}"
msg "- Code bucket: ${regional_bucket}-${region}"
msg "- Version: ${version}"
msg "- Region: ${region}"


echo ""
sleep 3
s3domain="s3.$region.amazonaws.com"

# Check if region is supported:
if [ "$region" != "us-east-1" ] &&
   [ "$region" != "us-east-2" ] &&
   [ "$region" != "us-west-1" ] &&
   [ "$region" != "us-west-2" ] &&
   [ "$region" != "eu-west-1" ] &&
   [ "$region" != "eu-west-2" ] &&
   [ "$region" != "eu-central-1" ] &&
   [ "$region" != "ap-south-1" ] &&
   [ "$region" != "ap-northeast-1" ] &&
   [ "$region" != "ap-southeast-1" ] &&
   [ "$region" != "ap-southeast-2" ] &&
   [ "$region" != "ap-northeast-1" ] &&
   [ "$region" != "ap-northeast-2" ]; then
   echo "ERROR. Not not supported in region $region"
   exit 1
fi

# Build source S3 Bucket
if [[ ! -x "$(command -v aws)" ]]; then
echo "ERROR: This script requires the AWS CLI to be installed. Please install it then run again."
exit 1
fi

# Get reference for all important folders
build_dir="$PWD"
global_dist_dir="$build_dir/global-s3-assets"
regional_dist_dir="$build_dir/regional-s3-assets"
dist_dir="$build_dir/dist"
source_dir="$build_dir/../source"
helper_dir="$build_dir/../source/helper"
website_dir="$build_dir/../source/web"

# Create and activate a temporary Python environment for this script.
echo "------------------------------------------------------------------------------"
echo "Creating a temporary Python virtualenv for this script"
echo "------------------------------------------------------------------------------"
python -c "import os; print (os.getenv('VIRTUAL_ENV'))" | grep -q None
if [ $? -ne 0 ]; then
    echo "ERROR: Do not run this script inside Virtualenv. Type \`deactivate\` and run again.";
    exit 1;
fi
echo "Using virtual python environment:"
VENV=$(mktemp -d) && echo "$VENV"
command -v python3 > /dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: install Python3 before running this script"
    exit 1
fi

command -v node > /dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: install node before running this script"
    exit 1
fi

python3 -m venv "$VENV"
source "$VENV"/bin/activate
pip3 install wheel
pip3 install --quiet boto3 chalice requests_toolbelt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install required Python libraries."
    exit 1
fi

echo "------------------------------------------------------------------------------"
echo "Create distribution directory"
echo "------------------------------------------------------------------------------"

# Setting up directories
echo "rm -rf $global_dist_dir"
rm -rf "$global_dist_dir"
echo "mkdir -p $global_dist_dir"
mkdir -p "$global_dist_dir"
echo "mkdir -p $global_dist_dir/website"
mkdir -p "$global_dist_dir"/website
echo "rm -rf $regional_dist_dir"
rm -rf "$regional_dist_dir"
echo "mkdir -p $regional_dist_dir"
mkdir -p "$regional_dist_dir"

echo "------------------------------------------------------------------------------"
echo "CloudFormation Templates"
echo "------------------------------------------------------------------------------"

echo "Preparing template files:"
cp "$build_dir/simple-file-manager-for-amazon-efs.yaml" "$global_dist_dir/simple-file-manager-for-amazon-efs.template"
cp "$build_dir/efs-file-manager-web.yaml" "$global_dist_dir/efs-file-manager-web.template"
cp "$build_dir/efs-file-manager-auth.yaml" "$global_dist_dir/efs-file-manager-auth.template"

find "$global_dist_dir"
echo "Updating template source bucket in template files with '$global_bucket'"
echo "Updating code source bucket in template files with '$regional_bucket'"
echo "Updating solution version in template files with '$version'"
new_global_bucket="s/%%GLOBAL_BUCKET_NAME%%/$global_bucket/g"
new_regional_bucket="s/%%REGIONAL_BUCKET_NAME%%/$regional_bucket/g"
new_version="s/%%VERSION%%/$version/g"
# Update templates in place. Copy originals to [filename].orig
sed -i.orig -e "$new_global_bucket" "$global_dist_dir/simple-file-manager-for-amazon-efs.template"
sed -i.orig -e "$new_regional_bucket" "$global_dist_dir/simple-file-manager-for-amazon-efs.template"
sed -i.orig -e "$new_version" "$global_dist_dir/simple-file-manager-for-amazon-efs.template"

# Update templates in place. Copy originals to [filename].orig
sed -i.orig -e "$new_global_bucket" "$global_dist_dir/efs-file-manager-web.template"
sed -i.orig -e "$new_regional_bucket" "$global_dist_dir/efs-file-manager-web.template"
sed -i.orig -e "$new_version" "$global_dist_dir/efs-file-manager-web.template"

# Update templates in place. Copy originals to [filename].orig
sed -i.orig -e "$new_global_bucket" "$global_dist_dir/efs-file-manager-auth.template"
sed -i.orig -e "$new_regional_bucket" "$global_dist_dir/efs-file-manager-auth.template"
sed -i.orig -e "$new_version" "$global_dist_dir/efs-file-manager-auth.template"


echo "------------------------------------------------------------------------------"
echo "Build API"
echo "------------------------------------------------------------------------------"

echo "Building API Lambda function"
cd "$source_dir/api" || exit 1
[ -e dist ] && rm -rf dist
mkdir -p dist
if ! [ -x "$(command -v chalice)" ]; then
  echo 'Chalice is not installed. It is required for this solution. Exiting.'
  exit 1
fi

# Remove chalice deployments to force redeploy when there are changes to configuration only
# Otherwise, chalice will use the existing deployment package
[ -e .chalice/deployments ] && rm -rf .chalice/deployments

echo "running chalice..."
chalice --debug package --merge-template external_resources.json dist
echo "...chalice done"
echo "cp ./dist/sam.json $global_dist_dir/file-manager-api-stack.template"
cp dist/sam.json "$global_dist_dir"/file-manager-api-stack.template
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to build api template"
  exit 1
fi
echo "cp ./dist/deployment.zip $regional_dist_dir/filemanagerapi.zip"
cp ./dist/deployment.zip "$regional_dist_dir"/filemanagerapi.zip
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to build api package"
  exit 1
fi
rm -rf ./dist

#
#echo "------------------------------------------------------------------------------"
#echo "Website"
#echo "------------------------------------------------------------------------------"
#
#echo "Building Vue.js website"
#cd "$source_dir/web" || exit 1
#echo "Installing node dependencies"
#npm install
#echo "Compiling the vue app"
#npm run build
#echo "Built demo webapp"


echo "------------------------------------------------------------------------------"
echo "Building VueJS Website"
echo "------------------------------------------------------------------------------"

cd "$website_dir" || exit 1
[ -e dist ] && rm -r dist
mkdir -p dist
echo "Installing node dependencies"
npm install
echo "Compiling the vue app"
npm run build
echo "Built demo webapp"
# Remove old website
rm -rf "$regional_dist_dir/website"
# Now we have a dist directory in web that we can move to dist_dir
mv "./dist/" "$regional_dist_dir/website"


echo "------------------------------------------------------------------------------"
echo "Generate webapp manifest file"
echo "------------------------------------------------------------------------------"
# This manifest file contains a list of all the webapp files. It is necessary in
# order to use the least privileges for deploying the webapp.
#
# Details: The website_helper.py Lambda function needs this list in order to copy
# files from $regional_dist_dir/website to the SimpleFileManagerWebsiteBucket (see efs-file-manager-web.yaml).  Since the manifest file is computed during build
# time, the website_helper.py Lambda can use that to figure out what files to copy
# instead of doing a list bucket operation, which would require ListBucket permission.
# Furthermore, the S3 bucket used to host AWS solutions (s3://solutions-reference)
# disallows ListBucket access, so the only way to copy files from
# s3://solutions-reference/simple-file-manager-for-amazon-efs/latest/website to
# SimpleFileManagerWebsiteBucket is to use said manifest file.
#
cd $regional_dist_dir"/website/" || exit 1
manifest=(`find . -type f | sed 's|^./||'`)
manifest_json=$(IFS=,;printf "%s" "${manifest[*]}")
echo "[\"$manifest_json\"]" | sed 's/,/","/g' > $helper_dir/webapp-manifest.json
cat $helper_dir/webapp-manifest.json

echo "------------------------------------------------------------------------------"
echo "Build website helper function"
echo "------------------------------------------------------------------------------"

echo "Building website helper function"
cd "$helper_dir" || exit 1
[ -e dist ] && rm -r dist
mkdir -p dist
zip -q -g ./dist/websitehelper.zip ./website_helper.py webapp-manifest.json

cp "./dist/websitehelper.zip" "$regional_dist_dir/websitehelper.zip"
echo "Cleaning up website helper function"
rm -rf ./dist


# Skip copy dist to S3 if building for solution builder because
# that pipeline takes care of copying the dist in another script.
if [ "$global_bucket" != "solutions-features-reference" ] && [ "$global_bucket" != "solutions-reference" ] && [ "$global_bucket" != "solutions-test-reference" ]; then
    
    echo "------------------------------------------------------------------------------"
    echo "Validate user is valid owner of S3 bucket"
    echo "------------------------------------------------------------------------------"
    # Get account id
    account_id=$(aws sts get-caller-identity --query Account --output text)
    if [ $? -ne 0 ]; then
        msg "ERROR: Failed to get AWS account ID"
        exit 1
    fi
    # Validate user is valid owner of S3 bucket
    aws s3api head-bucket --bucket ${regional_bucket}-${region} --expected-bucket-owner $account_id

    echo "------------------------------------------------------------------------------"
    echo "Copy dist to S3"
    echo "------------------------------------------------------------------------------"
    cd "$build_dir"/ || exit 1
    echo "Copying the prepared distribution to:"
    echo "s3://$global_bucket/simple-file-manager-for-amazon-efs/$version/"
    echo "s3://${regional_bucket}-${region}/simple-file-manager-for-amazon-efs/$version/"
    set -x
    aws s3 sync $global_dist_dir s3://$global_bucket/simple-file-manager-for-amazon-efs/$version/
    aws s3 sync $regional_dist_dir s3://${regional_bucket}-${region}/simple-file-manager-for-amazon-efs/$version/
    set +x

    echo "------------------------------------------------------------------------------"
    echo "S3 packaging complete"
    echo "------------------------------------------------------------------------------"

    echo ""
    echo "Template to deploy:"
    echo "TEMPLATE='"https://"$global_bucket"."$s3domain"/simple-file-manager-for-amazon-efs/"$version"/simple-file-manager-for-amazon-efs.template"'"
fi 

cleanup
echo "Done"
exit 0