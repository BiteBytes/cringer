#!/usr/bin/env bash

eval `ssh-agent -s`
chmod 600 resources/install/cringer2
ssh-add resources/install/cringer2
git pull
pip install -r requirements.txt
