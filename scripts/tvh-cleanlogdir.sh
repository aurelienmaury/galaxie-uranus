#! /bin/bash

# Write by Tuxa <tuxa galaxie.eu.org>
# It script it publish on GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html

# It script convert and clean the entire TVHeadend log directory
# It is not a recording post-script
# The script verify if every video link inside de log directory is all ready convert to MKV
# If a log file is found with a reference to a no existing movies file it delete the un-valide log file
# In case the script verify of the file is found as mkv and do nothing :)

SCRIPTNAME="tvh-cleanlogdir.sh"
VERION="0.2"

HTSHOME=$(eval echo ~"$(whoami)")
LOGDIR="$HTSHOME/.hts/tvheadend/dvr/log/"

TARGET_EXT='mkv'
SCRIPTORUN="$HTSHOME/Transcode/tvh-cleanlogfiles.sh"

TASK_SPOOLER_PATH=`which tsp`
if [ ! $TASK_SPOOLER_PATH ]; then
    echo "Task Spooler is welcome,\`which tsp\` return nothing"
    echo " Please consider to install \"tsp\" or verify it is aviable on your \$PATH env var"
    echo " $SCRIPTNAME will continue and not use a Task SPooler..."
    exit 1
fi
# Verify TVHeadend Log dir exist
if [ -d "$LOGDIR" ]; then
    # Parse each files contain inside Log dir
    for LOGFILE in $LOGDIR/*; do
            VIDEO_FILENAME=$(cat $LOGFILE | grep -Po '(?<="filename": ")[^"]*')
	        VIDEO_FILENAME_EXT=${VIDEO_FILENAME##*.}
            TBR="`basename "$VIDEO_FILENAME" ".$VIDEO_FILENAME_EXT"`"
            WORKINGDIR=`dirname "$VIDEO_FILENAME"`
            if [ ! $VIDEO_FILENAME_EXT = $TARGET_EXT ]; then
                if [ -f $VIDEO_FILENAME ]; then
                    if [ ! $TASK_SPOOLER_PATH ]; then
                        #echo "$TASK_SPOOLER_PATH $SCRIPTORUN $VIDEO_FILENAME"
                        $TASK_SPOOLER_PATH $SCRIPTORUN $VIDEO_FILENAME
                    else
                        #echo "$SCRIPTORUN $VIDEO_FILENAME"
                        $SCRIPTORUN $VIDEO_FILENAME
                    fi
                else
                    #echo "$LOGFILE have reference for:"
                    #echo "but $VIDEO_FILENAME don't exist"
                    if [ ! -f $WORKINGDIR/$TBR.$TARGET_EXT ]; then
                        rm $LOGFILE
                    fi 
                fi
            fi
    done
else
  echo "$LOGDIR don't exist , can't search anything"
  exit 1
fi
