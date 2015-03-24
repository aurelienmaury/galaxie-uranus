#! /bin/bash

# Write by Tuxa <tuxa galaxie.eu.org>
# It script it publish on GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html

# This script search in TVHeadend log directory a file it contain a patern
# With it patterh , the script found the log file and extract the Video path attached
# It re-encode the video file to mkv contener and update the log file with the new mkv path file.
# The re-encoded file is store at the same place as the original file by with .mkv extention

# It script fixe brocken Index, It's require for have "Avance Rapide" , comskip, or openshot it work.
# By use a external encode script it convert to mkv contener and save lot of space on you PVR

# It can be use as TVHeadend Post-Script like that:
# /full/path/to/tvh-cleanlogfiles.sh %f

SCRIPTNAME="tvh-cleanlogfiles.sh"
VERION="0.2"

HTSHOME=$(eval echo ~"$(whoami)")
LOGDIR="$HTSHOME/.hts/tvheadend/dvr/log"

RSYNC_PATH=`which rsync`
if [ ! $RSYNC_PATH ]; then
    echo "Rsync should be install,\`which rsync\` return nothing"
    echo " Please consider to install \"rsync\" or verify it is aviable on your \$PATH env var"
    echo " $SCRIPTNAME will use \"cp\" for copy files"
fi

HANDBRAKECLI_PATH=`which HandBrakeCLI`
if [ ! $HANDBRAKECLI_PATH ]; then
    echo "HandBrakeCLI is require,\`which HandBrakeCLI\` return nothing"
    echo " Please install \"HandBrakeCLI\" or verify it is aviable on your \$PATH env var"
    echo " $SCRIPTNAME will abort..."
    exit 1
fi

MEDIAINFO_PATH=`which mediainfo`
if [ ! $MEDIAINFO_PATH ]; then
    echo "Mediainfo is require,\`which mediainfo\` return nothing"
    echo " Please install \"mediainfo\" or verify it is aviable on your \$PATH env var"
    echo " $SCRIPTNAME will abort..."
    exit 1
fi

COMSKIP_PATH=`which comskip`
if [ ! $COMSKIP_PATH ]; then
    echo "Comskip should be install,\`which comskip\` return nothing"
    echo " Please consider to install \"comskip\" for enable comercial detection"
    echo " $SCRIPTNAME will continue without commercial skip..."
    exit 1
fi


#The script must accept a parameter for the full path of the video to encode
#ENCODE_SCRIPT="$HTSHOME/Transcode/encode.sh"
ENCODE_SCRIPT="$HTSHOME/Transcode/tvh-transcoder.sh"

TARGET_EXT='mkv'

#Check if a parameter is all ready present
if [ $# -eq 0 ]; then
    echo "Please, invoke it script with patern you searching for"
    echo "Exemple: $SCRIPTNAME Hangar-1-_-les-dossiers-ovni.E08.Les-points-chauds-de-l_Am__rique.ts"
    exit 1
fi
if [ ! "$1" ]; then
    echo "Please, invoke it script with patern you searching for"
    echo "Exemple: $SCRIPTNAME Hangar-1-_-les-dossiers-ovni.E08.Les-points-chauds-de-l_Am__rique.ts"
    exit 1
fi
# Take the first and unic parameter and consider it as the pattern to search
readonly SEARCHING="$1"

# Verify TVHeadend Log dir exist
if [ -d "$LOGDIR" ]; then
    # Parse each files contain inside Log dir
    for LOGFILE in $LOGDIR/*; do
        # Test if the $SEARCHING  pattern is found inside a Log file
        if grep -q $SEARCHING "$LOGFILE"; then
            echo "Found motif: $SEARCHING"
            echo "Inside: $(ls -h $LOGFILE)"
            VIDEO_FILENAME=$(cat $LOGFILE | grep -Po '(?<="filename": ")[^"]*')
	        VIDEO_FILENAME_EXT=${VIDEO_FILENAME##*.}
            TBR="`basename "$VIDEO_FILENAME" ".$VIDEO_FILENAME_EXT"`"
            WORKINGDIR=`dirname "$VIDEO_FILENAME"`
            echo "Filename: $(ls -sh $VIDEO_FILENAME)"
            if [ ! $VIDEO_FILENAME_EXT = $TARGET_EXT ]; then
                echo "Starting encoding..."
                $ENCODE_SCRIPT $VIDEO_FILENAME          
                if [ $? != 0 ]; then
                    echo "Error: The encode script have exit with errors..."
                    echo " The programm will abort..."
                    exit 1
                else
                    if [ -f "$WORKINGDIR/$TBR.$TARGET_EXT" ]; then
                        echo "Compare movies general duration"
                        DURATION_ORIGINE=`expr $($MEDIAINFO_PATH --Inform='General;%Duration%' $VIDEO_FILENAME | cut -d '.' -f1) / 1000 / 60`
                        DURATION_ENCODED=`expr $($MEDIAINFO_PATH --Inform='General;%Duration%' $WORKINGDIR/$TBR.$TARGET_EXT | cut -d '.' -f1) / 1000 / 60`
                        echo "Origin video duration: $DURATION_ORIGINE minutes ; Encoded video duration: $DURATION_ENCODED minutes"
                        if [ $DURATION_ORIGINE -eq $DURATION_ENCODED ]; then
                            #That a good news with they checks we are sure about the Transcoding have work
                            echo "Transcode Run successfull..."

                            echo "Update TVHeadend Log file ..."
                            sed -i.bak "s/$TBR.$VIDEO_FILENAME_EXT/$TBR.$TARGET_EXT/g" $LOGFILE && rm -f "$LOGFILE.bak"
                            if [ $COMSKIP_PATH ]; then
                                #Copy the encoded file inside $HTSHOME/Transcode/ for permit future thing
                                if [ ! -d "$HTSHOME/Transcode/$TBR" ]; then
                                    mkdir -p "$HTSHOME/Transcode/$TBR"
                                fi
                                if [ $RSYNC_PATH ]; then
                                    echo "Rsync $TBR.$TARGET_EXT to $HTSHOME/Transcode/$TBR/ for future comskip"
                                    $RSYNC_PATH -P -av "$WORKINGDIR/$TBR.$TARGET_EXT" "$HTSHOME/Transcode/$TBR/"
                                else
                                    echo "Copy $TBR.$TARGET_EXT to $HTSHOME/Transcode/$TBR/ for future comskip"
                                    cp "$WORKINGDIR/$TBR.$TARGET_EXT" "$HTSHOME/Transcode/$TBR/"
                                fi
                                $COMSKIP_PATH "$HTSHOME/Transcode/$TBR/$TBR.$TARGET_EXT"
                            fi
                            # Here we are 99.9% sure about the original .ts file is not require anymore
                            echo "Remove original mpeg2 .ts file"
                            rm $VIDEO_FILENAME
                            rm $WORKINGDIR/$TBR.log
                        else
                            echo "Error: Source file and encoded file haven't the same duration..."
                            echo " The programm will abort..."
                            exit 1                        
                        fi
                    else
                        echo "Error: File $WORKINGDIR/$TBR.$TARGET_EXT/ don't exist..."
                        echo " The programm will abort..."
                        exit 1
                    fi
                fi
            else
                echo "The video file is all ready a MKV video, nothing to do..."
                exit 0
            fi
        fi
    done
else
    echo "$LOGDIR don't exist , can't search anything"
    echo " The programm will abort..."
    exit 1
fi
