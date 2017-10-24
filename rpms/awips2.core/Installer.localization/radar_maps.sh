#!/bin/bash
UHOME=/Users/mjames
BUILD_DIR=$UHOME/awips2-builds/rpms/awips2.core/Installer.localization/
CAVE_DIR=$BUILD_DIR/utility/cave_static/bundles/scales/radar/
mkdir -p $CAVE_DIR
rm -rf $CAVE_DIR/*
file=$BUILD_DIR/coords_wsr88d.dat

for site in $(cat $file |cut -c -4)
do
   lat=$(cat $file   |grep $site | cut -d"," -f2  | tr -d '[[:space:]]')
   lon=$(cat $file   |grep $site | cut -d"," -f3  | tr -d '[[:space:]]')
   lowx=$(cat $file  |grep $site | cut -d"," -f4  | tr -d '[[:space:]]')
   highx=$(cat $file |grep $site | cut -d"," -f5  | tr -d '[[:space:]]')
   lowy=$(cat $file  |grep $site | cut -d"," -f6  | tr -d '[[:space:]]')
   highy=$(cat $file |grep $site | cut -d"," -f7  | tr -d '[[:space:]]')
   minx=$(cat $file  |grep $site | cut -d"," -f8  | tr -d '[[:space:]]')
   maxx=$(cat $file  |grep $site | cut -d"," -f9  | tr -d '[[:space:]]')
   miny=$(cat $file  |grep $site | cut -d"," -f10 | tr -d '[[:space:]]')
   maxy=$(cat $file  |grep $site | cut -d"," -f11 | tr -d '[[:space:]]')

   sitell=$(echo $site | tr '[:upper:]' '[:lower:]')
   cp -R $BUILD_DIR/RadarTwoPanel.xml $CAVE_DIR/Radar_$sitell.xml
   grep -rl 'LOWX'  $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/LOWX/'$lowx'/g'
   grep -rl 'HIGHX' $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/HIGHX/'$highx'/g'
   grep -rl 'LOWY'  $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/LOWY/'$lowy'/g'
   grep -rl 'HIGHY' $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/HIGHY/'$highy'/g'
   grep -rl 'MINX'  $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/MINX/'$minx'/g'
   grep -rl 'MAXX'  $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/MAXX/'$maxx'/g'
   grep -rl 'MINY'  $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/MINY/'$miny'/g'
   grep -rl 'MAXY'  $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/MAXY/'$maxy'/g'
   grep -rl 'XXX'   $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/XXX/'$site'/g'
   grep -rl 'xxx'   $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/xxx/'$sitell'/g'
   grep -rl 'LATITUDE'  $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/LATITUDE/'$lat'/g'
   grep -rl 'LONGITUDE' $CAVE_DIR/Radar_$sitell.xml | xargs sed -i.bak 's/LONGITUDE/'$lon'/g'
   
   cp $CAVE_DIR/Radar_$sitell.xml $UHOME/awips2-core/viz/com.raytheon.uf.viz.core.maps/localization/bundles/scales/WSR88D/

done


cp $CAVE_DIR/* $UHOME/awips2-builds/cave/com.raytheon.viz.radar/localization/bundles/site/
rm -rf $UHOME/awips2-builds/cave/com.raytheon.viz.radar/localization/bundles/site/Radar_comp.xml
rm -rf $UHOME/awips2-builds/cave/com.raytheon.viz.radar/localization/bundles/site/Radar_info.xml
rm -rf $UHOME/awips2-builds/cave/com.raytheon.viz.radar/localization/bundles/site/Radar_proc.xml

#	com.raytheon.viz.radar/localization/bundles/site/Radar_comp.xml
#	com.raytheon.viz.radar/localization/bundles/site/Radar_info.xml
#	com.raytheon.viz.radar/localization/bundles/site/Radar_proc.xml

