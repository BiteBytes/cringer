#!/bin/bash
set -e

# To use this mod you have to type chmod +x Installingmods.sh

echo "Installing ElectronicStars files"
export AWS_ACCESS_KEY_ID='AKIAJGBPWCCMDPOEZ6RQ'
export AWS_SECRET_ACCESS_KEY='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'


echo "Installing sourcemod "
cd /home/steam/csgo/csgo/
echo Downloading from $1
wget $1
tar -xzf $(basename $1)
rm $(basename $1)

echo "Downloading plugins to /home/steam/csgo/csgo/addons/sourcemod/plugins"
aws s3 cp s3://electronics3/gameservers/es_plugins.tar.gz /home/steam/csgo/csgo/addons/sourcemod/plugins --region eu-west-1
cd /home/steam/csgo/csgo/addons/sourcemod/plugins
tar -vxzf es_plugins.tar.gz
cp ./es_plugins/* ./
rm -r ./es_plugins
rm -r ./es_plugins.tar.gz

echo "Downloading weapon restriction plugin"
aws s3 cp s3://electronics3/gameservers/weapon-restrict.tar.gz /home/steam/csgo/csgo/addons --region eu-west-1
cd /home/steam/csgo/csgo/addons
tar -vxzf weapon-restrict.tar.gz
rm -r ./weapon-restrict.tar.gz


echo "Installing metamod  "
cd /home/steam/csgo/csgo/
wget https://mms.alliedmods.net/mmsdrop/1.10/mmsource-1.10.7-git959-linux.tar.gz
tar -vxzf mmsource-1.10.7-git959-linux.tar.gz
rm -r mmsource-1.10.7-git959-linux.tar.gz


# echo "Downloading maps to /home/steam/csgo/csgo/maps"
# aws s3 sync s3://electronics3/csgomaps/maps /home/steam/csgo/csgo/maps --region eu-west-1

echo "Copying configs from cringer"
cp /home/steam/cringer/cs_configs/csgo/gamemode_competitive_server.cfg /home/steam/csgo/csgo/cfg
cp /home/steam/cringer/cs_configs/csgo/gamemode_deathmatch_server.cfg /home/steam/csgo/csgo/cfg
cp /home/steam/cringer/cs_configs/csgo/server.cfg /home/steam/csgo/csgo/cfg

echo "Creating home/steam/csgo/addons/metamod.vdf"
echo "\"Plugin\"

{

        \"file\"  \"../csgo/addons/metamod/bin/server\"

}"  >  /home/steam/csgo/csgo/addons/metamod.vdf


echo "Done"

exit 0