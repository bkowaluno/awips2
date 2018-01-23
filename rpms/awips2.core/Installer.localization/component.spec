#
# AWIPS II Localization Spec File
#
Name: %{_component_name}
Summary: AWIPS II Localization Installation
Version: %{_component_version}
Release: %{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: /tmp
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Provides: %{_component_name}
Requires: awips2-edex
Requires: awips2-edex-shapefiles
Obsoletes: awips2-localization-OAX < 16.1.4

%description
AWIPS II Site Localization.

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "${RPM_BUILD_ROOT}" = "/tmp" ]
then
   echo "An Actual BuildRoot Must Be Specified. Use The --buildroot Parameter."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

if [ -d ${RPM_BUILD_ROOT} ]; then
   rm -rf ${RPM_BUILD_ROOT}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

%build

# Build all WFO site localization Map Scales (Regional.xml and WFO.xml)
BUILD_DIR=%{_baseline_workspace}/rpms/awips2.core/Installer.localization/
UTIL=%{_baseline_workspace}/localization/utility
#file=$BUILD_DIR/wfo.dat
file=$BUILD_DIR/coords.dat
regional=$BUILD_DIR/coords_regional.dat
#<gridGeometry rangeX="LOWX HIGHX" rangeY="LOWY HIGHY" envelopeMinX="MINX" envelopeMaxX="MAXX" envelopeMinY="MINY" envelopeMaxY="MAXY">

for site in $(cat $file |cut -c -3)
do
   lat=$(cat $file   |grep $site | cut -d"," -f2  | tr -d '[[:space:]]')
   lon=$(cat $file   |grep $site | cut -d"," -f3  | tr -d '[[:space:]]')

   # <gridGeometry rangeX="LOWX HIGHX" rangeY="LOWY HIGHY" envelopeMinX="MINX" envelopeMaxX="MAXX" envelopeMinY="MINY" envelopeMaxY="MAXY">
   lowx=$(cat $file  |grep $site | cut -d"," -f4  | tr -d '[[:space:]]')
   highx=$(cat $file |grep $site | cut -d"," -f5  | tr -d '[[:space:]]')
   lowy=$(cat $file  |grep $site | cut -d"," -f6  | tr -d '[[:space:]]')
   highy=$(cat $file |grep $site | cut -d"," -f7  | tr -d '[[:space:]]')
   minx=$(cat $file  |grep $site | cut -d"," -f8  | tr -d '[[:space:]]')
   maxx=$(cat $file  |grep $site | cut -d"," -f9  | tr -d '[[:space:]]')
   miny=$(cat $file  |grep $site | cut -d"," -f10 | tr -d '[[:space:]]')
   maxy=$(cat $file  |grep $site | cut -d"," -f11 | tr -d '[[:space:]]')

   # CAVE
   CAVE_DIR=$UTIL/cave_static/site/$site
   mkdir -p $CAVE_DIR
   cp -R $BUILD_DIR/utility/cave_static/* $CAVE_DIR
   mkdir -p ~/awips2-builds/localization/localization/utility/cave_static/site/$site
   cp -R $BUILD_DIR/utility/cave_static/* ~/awips2-builds/localization/localization/utility/cave_static/site/$site
   grep -rl 'LOWX'  $CAVE_DIR/bundles/scales/WFO.xml | xargs sed -i 's/LOWX/'$lowx'/g'
   grep -rl 'HIGHX' $CAVE_DIR/bundles/scales/WFO.xml | xargs sed -i 's/HIGHX/'$highx'/g'
   grep -rl 'LOWY'  $CAVE_DIR/bundles/scales/WFO.xml | xargs sed -i 's/LOWY/'$lowy'/g'
   grep -rl 'HIGHY' $CAVE_DIR/bundles/scales/WFO.xml | xargs sed -i 's/HIGHY/'$highy'/g'
   grep -rl 'MINX'  $CAVE_DIR/bundles/scales/WFO.xml | xargs sed -i 's/MINX/'$minx'/g'
   grep -rl 'MAXX'  $CAVE_DIR/bundles/scales/WFO.xml | xargs sed -i 's/MAXX/'$maxx'/g'
   grep -rl 'MINY'  $CAVE_DIR/bundles/scales/WFO.xml | xargs sed -i 's/MINY/'$miny'/g'
   grep -rl 'MAXY'  $CAVE_DIR/bundles/scales/WFO.xml | xargs sed -i 's/MAXY/'$maxy'/g'

   #cp $CAVE_DIR/bundles/scales/WFO.xml ~/awips2-core/viz/com.raytheon.uf.viz.core.maps/localization/bundles/scales/WFO/$site.xml

   lowx=$(cat $regional  |grep $site | cut -d"," -f4  | tr -d '[[:space:]]')
   highx=$(cat $regional |grep $site | cut -d"," -f5  | tr -d '[[:space:]]')
   lowy=$(cat $regional  |grep $site | cut -d"," -f6  | tr -d '[[:space:]]')
   highy=$(cat $regional |grep $site | cut -d"," -f7  | tr -d '[[:space:]]')
   minx=$(cat $regional  |grep $site | cut -d"," -f8  | tr -d '[[:space:]]')
   maxx=$(cat $regional  |grep $site | cut -d"," -f9  | tr -d '[[:space:]]')
   miny=$(cat $regional  |grep $site | cut -d"," -f10 | tr -d '[[:space:]]')
   maxy=$(cat $regional  |grep $site | cut -d"," -f11 | tr -d '[[:space:]]')

   grep -rl 'LOWX'  $CAVE_DIR/bundles/scales/Regional.xml | xargs sed -i 's/LOWX/'$lowx'/g'
   grep -rl 'HIGHX' $CAVE_DIR/bundles/scales/Regional.xml | xargs sed -i 's/HIGHX/'$highx'/g'
   grep -rl 'LOWY'  $CAVE_DIR/bundles/scales/Regional.xml | xargs sed -i 's/LOWY/'$lowy'/g'
   grep -rl 'HIGHY' $CAVE_DIR/bundles/scales/Regional.xml | xargs sed -i 's/HIGHY/'$highy'/g'
   grep -rl 'MINX'  $CAVE_DIR/bundles/scales/Regional.xml | xargs sed -i 's/MINX/'$minx'/g'
   grep -rl 'MAXX'  $CAVE_DIR/bundles/scales/Regional.xml | xargs sed -i 's/MAXX/'$maxx'/g'
   grep -rl 'MINY'  $CAVE_DIR/bundles/scales/Regional.xml | xargs sed -i 's/MINY/'$miny'/g'
   grep -rl 'MAXY'  $CAVE_DIR/bundles/scales/Regional.xml | xargs sed -i 's/MAXY/'$maxy'/g'

   grep -rl 'XXX' $CAVE_DIR | xargs sed -i 's/XXX/'$site'/g'
   grep -rl 'LATITUDE' $CAVE_DIR | xargs sed -i 's/LATITUDE/'$lat'/g'
   grep -rl 'LONGITUDE' $CAVE_DIR | xargs sed -i 's/LONGITUDE/'$lon'/g'
   # EDEX
   EDEX_DIR=$UTIL/common_static/site/$site
   mkdir -p $EDEX_DIR
   cp -R $BUILD_DIR/utility/siteconfig/* $EDEX_DIR/
   grep -rl 'XXX' $EDEX_DIR | xargs sed -i 's/XXX/'$site'/g'
done

# Copy existing (default) OAX and TBW map scales
cp -R %{_baseline_workspace}/localization.OAX/utility/cave_static/site/* %{_baseline_workspace}/localization/utility/cave_static/site/
cp -R %{_baseline_workspace}/localization.TBW/utility/cave_static/site/* %{_baseline_workspace}/localization/utility/cave_static/site/
#cp %{_baseline_workspace}/localization.TBW/utility/cave_static/site/TBW/bundles/scales/WFO.xml ~/awips2-core/viz/com.raytheon.uf.viz.core.maps/localization/bundles/scales/WFO/TBW.xml
#cp %{_baseline_workspace}/localization.OAX/utility/cave_static/site/OAX/bundles/scales/WFO.xml ~/awips2-core/viz/com.raytheon.uf.viz.core.maps/localization/bundles/scales/WFO/OAX.xml

# COMMON
COMMON_DIR=$UTIL/common_static
mkdir -p $COMMON_DIR
cp -R $BUILD_DIR/utility/common_static/* $COMMON_DIR/


%install
if [ ! -d %{_baseline_workspace}/%{_localization_directory} ]; then
   echo "ERROR: The specified localization directory does not exist - %{_localization_directory}."
   exit 1
fi

mkdir -p ${RPM_BUILD_ROOT}/awips2/edex/data/utility
if [ $? -ne 0 ]; then
   exit 1
fi

# Copy the localization files
cp -rv %{_baseline_workspace}/localization/utility/* \
   ${RPM_BUILD_ROOT}/awips2/edex/data/utility
if [ $? -ne 0 ]; then
   exit 1
fi

%pre

%post
# verify the following exists:
if [ ! -d /awips2/data/maps ] ||
   [ ! -f /awips2/postgresql/bin/postmaster ] ||
   [ ! -f /awips2/postgresql/bin/pg_ctl ] ||
   [ ! -f /awips2/psql/bin/psql ] ||
   [ ! -f /awips2/database/sqlScripts/share/sql/maps/importShapeFile.sh ] ||
   [ ! -f /awips2/postgresql/bin/pg_restore ]; then
   # we are missing a file or directory, exit
   exit 0
fi

log_file="/awips2/database/sqlScripts/share/sql/localization_db.log"
if [ -f ${log_file} ]; then
   /bin/rm -f ${log_file}
fi
/bin/touch ${log_file}
chmod 666 ${log_file}

edex_utility="/awips2/edex/data/utility"
I_STARTED_POSTGRESQL="NO"
POSTGRESQL_RUNNING="NO"

function prepare()
{
   if [ "${POSTGRESQL_RUNNING}" = "YES" ]; then
      return 0
   fi
   local a2_postmaster="/awips2/postgresql/bin/postmaster"
   local a2_pg_ctl="/awips2/postgresql/bin/pg_ctl"
   DB_OWNER=`ls -l /awips2/ | grep -w 'data' | awk '{print $3}'`
   I_STARTED_POSTGRESQL="NO"
   su - ${DB_OWNER} -c \
      "${a2_pg_ctl} status -D /awips2/data &" > /dev/null 2>&1
   RC=$?
   if [ ${RC} -ne 0 ]; then
      echo "Starting PostgreSQL as user: ${DB_OWNER} ..."
      su - ${DB_OWNER} -c \
         "${a2_postmaster} -D /awips2/data &" > /dev/null 2>&1
      if [ $? -ne 0 ]; then
         echo "FATAL: Failed to start PostgreSQL."
         return 0
      fi
      # give PostgreSQL time to start.
      /bin/sleep 10
      I_STARTED_POSTGRESQL="YES"
   fi
   POSTGRESQL_RUNNING="YES"
   return 0  
}

function restartPostgreSQL()
{
   if [ "${POSTGRESQL_RUNNING}" = "NO" ]; then
      return 0
   fi
   local a2_pg_ctl="/awips2/postgresql/bin/pg_ctl"
   DB_OWNER=`ls -l /awips2/ | grep -w 'data' | awk '{print $3}'`
   echo "Restarting PostgreSQL ..." 
   su - ${DB_OWNER} -c \
      "${a2_pg_ctl} restart -D /awips2/data &" 
   sleep 20
   echo "PostgreSQL restart complete ..." 
}

function importShapefiles()
{   
   local site_directory="${edex_utility}/common_static/site/OAX"
   local ffmp_shp_directory="${site_directory}/shapefiles/FFMP"
   if [ ! -d ${ffmp_shp_directory} ]; then
      return 0
   fi
   prepare
   if [ ! -f ${ffmp_shp_directory}/FFMP_aggr_basins.shp ] ||
      [ ! -f ${ffmp_shp_directory}/FFMP_ref_sl.shp ]; then
      return 0
   fi
   if [ ! -f ${ffmp_shp_directory}/FFMP_aggr_basins.dbf ] ||
      [ ! -f ${ffmp_shp_directory}/FFMP_aggr_basins.shx ] ||
      [ ! -f ${ffmp_shp_directory}/FFMP_ref_sl.dbf ] ||
      [ ! -f ${ffmp_shp_directory}/FFMP_ref_sl.shx ]; then
      return 0
   fi
   local a2_shp_script="/awips2/database/sqlScripts/share/sql/maps/importShapeFile.sh"
   echo "Importing the FFMP Shapefiles ... Please Wait."
   echo "Preparing to import the FFMP shapefiles ..." 

   /bin/bash ${a2_shp_script} \
      ${ffmp_shp_directory}/FFMP_aggr_basins.shp \
      mapdata ffmp_basins 0.064,0.016,0.004,0.001 \
      awips 5432 /awips2 
   if [ $? -ne 0 ]; then
      echo "FATAL: failed to import the FFMP basins."
      return 0
   fi
   
   /bin/bash ${a2_shp_script} \
      ${ffmp_shp_directory}/FFMP_ref_sl.shp \
      mapdata ffmp_streams 0.064,0.016,0.004,0.001 \
      awips 5432 /awips2 
   if [ $? -ne 0 ]; then
      echo "FATAL: failed to import the FFMP streams." 
      return 0
   fi
   echo "INFO: The FFMP shapefiles were successfully imported." 
}

function removeHydroDbDirectory()
{
   # remove the hydro db directory since it is not officially part of the localization.
   local site_directory="${edex_utility}/common_static/site/OAX"
   local hydro_db_directory="${site_directory}/hydro/db"
   
   if [ -d ${hydro_db_directory} ]; then
      rm -rf ${hydro_db_directory}
      if [ $? -ne 0 ]; then
         echo "WARNING: Failed to remove hydro db directory from localization."
         echo "         Please remove directory manually: ${hydro_db_directory}."
      fi
   fi
   
   return 0
}

function restoreHydroDb()
{
   local site_directory="${edex_utility}/common_static/site/OAX"
   
   # determine if we include the hydro databases
   local hydro_db_directory="${site_directory}/hydro/db"
   
   # if we do not, halt
   if [ ! -d ${hydro_db_directory} ]; then
      return 0
   fi
   
   # hydro databases exist
   prepare   
   
   # verify that the hydro database definition is present
   if [ ! -f ${hydro_db_directory}/hydroDatabases.sh ]; then
      return 0
   fi
   
   # discover the hydro databases
   source ${hydro_db_directory}/hydroDatabases.sh
   
   # ensure that the expected information has been provided
   if [ "${DAMCAT_DATABASE}" = "" ] ||
      [ "${DAMCAT_SQL_DUMP}" = "" ] ||
      [ "${IHFS_DATABASE}" = "" ] ||
      [ "${IHFS_SQL_DUMP}" = "" ]; then
      echo "Sufficient information has not been provided for the Hydro Restoration!"
      return 0
   fi
   
   # ensure that the specified databases are available for import
   if [ ! -f ${hydro_db_directory}/${DAMCAT_DATABASE} ] ||
      [ ! -f ${hydro_db_directory}/${IHFS_DATABASE} ]; then
      echo "The expected Hydro Database Exports are not present!"
      return 0
   fi
   
   # update pg_hba.conf
   
   local default_damcat="dc_ob7oax"
   local default_ihfs="hd_ob92oax"
   local pg_hba_conf="/awips2/data/pg_hba.conf"
   
   # update the entry for the damcat database
   perl -p -i -e "s/${default_damcat}/${DAMCAT_DATABASE}/g" ${pg_hba_conf}
   if [ $? -ne 0 ]; then
      echo "Failed to update damcat database in ${pg_hba_conf}!" 
      return 0
   fi
   
   # update the entry for the ihfs database
   perl -p -i -e "s/${default_ihfs}/${IHFS_DATABASE}/g" ${pg_hba_conf}
   if [ $? -ne 0 ]; then
      echo "Failed to update ihfs database in ${pg_hba_conf}!" 
      return 0
   fi
   
   # prepare PostgreSQL
   restartPostgreSQL
   
   echo "Restoring the Hydro Databases ... Please Wait."
   echo "Preparing to restore the Hydro databases ..." 
   
   local a2_pg_restore="/awips2/postgresql/bin/pg_restore"
   
   # perform the restoration
   echo "Restoring Database ${DAMCAT_DATABASE} ..." 
   ${a2_pg_restore} -U awips -C -d postgres ${hydro_db_directory}/${DAMCAT_DATABASE}
   # do not check the return code because any errors encountered during
   # the restoration may cause the return code to indicate a failure even
   # though the database was successfully restored.
   
   echo "Restoring Database ${IHFS_DATABASE} ..." 
   ${a2_pg_restore} -U awips -C -d postgres ${hydro_db_directory}/${IHFS_DATABASE}
   # do not check the return code because any errors encountered during
   # the restoration may cause the return code to indicate a failure even
   # though the database was successfully restored.
   
   # indicate success
   echo "INFO: The Hydro databases were successfully restored."
}

importShapefiles
#restoreHydroDb
#removeHydroDbDirectory

a2_pg_ctl="/awips2/postgresql/bin/pg_ctl"
# if we started PostgreSQL, shutdown PostgreSQL
if [ "${I_STARTED_POSTGRESQL}" = "YES" ]; then
   su - ${DB_OWNER} -c \
      "${a2_pg_ctl} stop -D /awips2/data &" 
   if [ $? -ne 0 ]; then
      echo "WARNING: Failed to shutdown PostgreSQL." 
      echo "         PostgreSQL will need to manually be shutdown." 
   else
      # Give PostgreSQL time to shutdown.
      /bin/sleep 10
   fi
fi
exit 0

%preun

%postun

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(755,awips,fxalpha,755)
%dir /awips2/edex/data/utility
/awips2/edex/data/utility/*
