#!/bin/bash

# su ec2-user
sudo pip3 install git-remote-codecommit

# Check if the directory exists.
if [ -d ~/fd-worker ]; then
    # If the directory exists, clone the Git repository.
    echo "Directory exists. Doing nothing"
    sudo git pull
else
    # If the directory does not exist, you can choose to take some other action or simply ignore.
    echo "Directory does not exist. Cloning repository..."
    cd ~
    sudo git clone codecommit::us-east-1://fd-worker
    cd fd-worker
    sudo chown -R ec2-user fd-worker 
    echo "Git repository cloned successfully."
fi
cd ~/fd-worker
pip3 install -r requirements.txt


# Set the S3 bucket and folder path
ARTIFACT_BUCKET=s3://fd-ml-artifacts
LOCAL_DIR=~/fd-worker/resource/bin

RCF_ARTIFACT_PATH="$ARTIFACT_BUCKET/rcf/"
XGB_ARTIFACT_PATH="$ARTIFACT_BUCKET/xgb/"
RCF_LOCAL_DIR="$LOCAL_DIR/rcf"
XGB_LOCAL_DIR="$LOCAL_DIR/xgb"

# Create the local directory if it doesn't exist
mkdir -p "$RCF_LOCAL_DIR"
mkdir -p "$XGB_LOCAL_DIR"

# Use the AWS CLI to sync the S3 bucket with the local directory
aws s3 sync "$RCF_ARTIFACT_PATH" "$RCF_LOCAL_DIR"
aws s3 sync "$XGB_ARTIFACT_PATH" "$XGB_LOCAL_DIR"

# Check if the sync command was successful
if [ $? -eq 0 ]; then
  echo "Download completed successfully."
else
  echo "Download failed. Check your AWS CLI configuration and permissions."
fi
