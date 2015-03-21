#$! /bin/bash
#Write by Tuxa <tuxa galaxie.eu.org>
# It script it publish on GNU GENERAL PUBLIC LICENSE
#http://www.gnu.org/licenses/gpl-3.0.en.html

######DEFINE SOME BASIC VARIABLES######
#######################################
SCRIPTNAME="tvh-transcoder.sh"
VERION="0.3"

######HANDBRAKECLI CHECK######
###########################
HANDBRAKECLI_PATH=`which HandBrakeCLI`
if [ ! $HANDBRAKECLI_PATH ]; then
    echo "HandBrakeCLI is require,\`which HandBrakeCLI\` return nothing"
    echo " Please install \"HandBrakeCLI\" or verify it is aviable on your \$PATH env var"
    echo " $SCRIPTNAME will abort..."
    exit 1
fi

######MEDIAINFO CHECK######
###########################
MEDIAINFO_PATH=`which mediainfo`
if [ ! $MEDIAINFO_PATH ]; then
    echo "Mediainfo is require,\`which mediainfo\` return nothing"
    echo " Please install \"mediainfo\" or verify it is aviable on your \$PATH env var"
    echo " $SCRIPTNAME will abort..."
    exit 1
fi

######Check if a parameter is all ready present######
#####################################################
if [ $# -eq 0 ]; then
    echo "Please, invoke it script with patern you searching for"
    echo "Exemple: $SCRIPTNAME ./Hangar-1-_-les-dossiers-ovni.E08.Les-points-chauds-de-l_Am__rique.ts"
    exit 1
fi
if [ ! "$1" ]; then
    echo "Please, invoke it script with patern you searching for"
    echo "Exemple: $SCRIPTNAME ./Hangar-1-_-les-dossiers-ovni.E08.Les-points-chauds-de-l_Am__rique.ts"
    exit 1
fi

######SOURCE FILE CHECK######
############################
if [ ! -f "$1" ]; then
    #source file does not exist
    echo "Error: Source file not found "
    echo "Maybe wrong path or missing permissions?"
    exit 1
fi

######DEFINE SOME BASIC VARIABLES######
#######################################
# Take the first and unic parameter and consider it as the file to encode
readonly VIDEO_FILENAME="$1"
VIDEO_FILENAME_EXT=${VIDEO_FILENAME##*.}
VIDEO_SHORTNAME="`basename "$VIDEO_FILENAME" ".$VIDEO_FILENAME_EXT"`"
WORKINGDIR=`dirname "$VIDEO_FILENAME"`

HTSHOME=$(eval echo ~"$(whoami)")
LOGDIR="$HTSHOME/.hts/tvheadend/dvr/log"

FAVORITE_LANGUAGE="French"
VIDEO_TARGET_EXT="mkv"
X264_OPTS="open_gop=0:rc-lookahead=50:ref=6:bframes=6:me=umh:subme=8:trellis=0:analyse=all:b-adapt=2:vbv_maxrate=24000:vbv_bufsize=24000:nal_hrd=none:vbv-bufsize=24000:vbv-maxrate=24000:fast_pskip=0:decimate=1:bframes=6:direct=auto:weightb=1:weightp=2"

######USUAL FONCTION######
##########################
function optimal_res() {
    RESOLUTIONS[0]=424
    RESOLUTIONS[1]=640
    RESOLUTIONS[2]=768
    RESOLUTIONS[3]=848
    RESOLUTIONS[4]=1024
    RESOLUTIONS[5]=1280
    RESOLUTIONS[6]=1920

    NAMES[0]=240
    NAMES[1]=360
    NAMES[2]=432
    NAMES[3]=480
    NAMES[4]=576
    NAMES[5]=720
    NAMES[6]=1080

    WIDTH=$1
    BEST_GUESS=-1
    INDEX=0

    MAX=${#RESOLUTIONS[@]}

    while [ "$BEST_GUESS" -ne "$INDEX" ]; do

        if [ "$INDEX" -lt "$((MAX - 1))" ]; then

            RES_GAP=$(( ${RESOLUTIONS[$(( $INDEX + 1 ))]} - ${RESOLUTIONS[$INDEX]} ))

            STEP_THRESHOLD=$(( $RES_GAP / 2 ))

            CUR_RES=${RESOLUTIONS[$INDEX]}

            WIDTH_GAP=$(( $WIDTH - $CUR_RES ))

            BEST_GUESS=$INDEX

            if [ "$WIDTH_GAP" -gt "$STEP_THRESHOLD" ]; then
                INDEX=$(( $INDEX + 1 ))
            fi
        else
            BEST_GUESS=$INDEX
        fi
    done

    echo "${NAMES[$BEST_GUESS]}"
}



######MEDIAINFO CHECK######
###########################
FULLMEDIAINFO=$($MEDIAINFO_PATH "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT")
if [ $? != 0 ]; then
    # There were errors with Mediainfo. 
    echo "Mediainfo encountered an error."
        exit 1
    else
        echo "Starting Media analyse..."
  fi

#######ANALAYZE AUDIO TRACKS AND DO LANGUAGE SELECTION######
############################################################

#AUDIO_TRACK_COUNT=$($MEDIAINFO_PATH --Inform="General;%AudioCount%" "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT")
SCAN_RESULT=$($HANDBRAKECLI_PATH --scan --input "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT" 2>&1)

AUDIO_TRACK_LIST=${SCAN_RESULT#*+\ audio\ tracks:}
AUDIO_TRACK_LIST=${AUDIO_TRACK_LIST%+\ subtitle\ tracks:*}
AUDIO_TRACK_LIST=${AUDIO_TRACK_LIST// /} # replace " " with ""
AUDIO_TRACK_COUNT=0
for I in $(echo $AUDIO_TRACK_LIST | sed -e 's/+/\n/g'); do
    echo $I
    
    ((AUDIO_TRACK_COUNT++))

done

#echo "it have $AUDIO_TRACK_COUNT tracks"
#exit

#AUDIO_TRACK_COUNT=number of audio tracks present in source file
#-a or --audio 1,1
#Read all values into arrays
AUDIO_BITRATE="$($MEDIAINFO_PATH --Inform="Audio;:%BitRate%" "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT")"
IFS=':' read -ra ARBITR <<< "$AUDIO_BITRATE"
AUDIO_LANGUAGE="$($MEDIAINFO_PATH --Inform="Audio;:%Language/String%" "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT")"
IFS=':' read -ra ARLANG <<< "$AUDIO_LANGUAGE"
AUDIO_CHANNELS="$($MEDIAINFO_PATH --Inform="Audio;:%Channel(s)%" "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT")"
IFS=':' read -ra ARCHAN <<< "$AUDIO_CHANNELS"
#Finished building arrays

#By default the Media Audio Track number 1 is use 
T1=1
for (( I=1; I <= "$AUDIO_TRACK_COUNT"; I++ )); do
    #In case of multi audio track it Detect if FAVORITE_LANGUAGE can be put on Track number 1
    if [ "$FAVORITE_LANGUAGE" == "${ARLANG[$I]}" ]; then
        T1=$I
    fi
done
#If the Track 1 or Language found , have more as 2 audio channels like 5.1 a second channel will be creat with all in copy inside
#The frist audio channel is everytime re-encoded
if [ ${ARCHAN[$T1]} -gt 2 ]; then
    #--audio
    AUDIO_ARG="$T1,$T1"
    #-E or --aencoder
    AUDIO_ENCODER_ARG="av_aac,copy:*"
    AUDIO_SAMPLERATE_ARG="44.1,auto"
    #-R or --arate
    AUDIO_BITRATE_ARG="128,$((${ARBITR[$T1]}/1000))"
    #-6 or --mixdown
    AUDIO_MIXDOWN_ARG="dpl2,none"
fi
if (( ${ARCHAN[$T1]} <= 2)) ; then
    #--audio
    AUDIO_ARG="$T1"
    #-E or --aencoder
    AUDIO_ENCODER_ARG="av_aac"
    AUDIO_SAMPLERATE_ARG="44.1"
    #-R or --arate
    AUDIO_BITRATE_ARG="128"
    #-6 or --mixdown
    AUDIO_MIXDOWN_ARG="dpl2"
fi

#######ANALAYZE VIDEO ######
############################

VIDEO_WIDTH=$(mediainfo --Inform="Video;%Width%" "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT")
VIDEO_HEIGHT=$(mediainfo --Inform="Video;%Height%" "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT")

# Calcul of the bit rate, hooooo magic !
#BIT*(pixel/frame)
VIDEO_FPS="25"
BPF=0.082
VIDEO_BITRATE=$(echo "((($VIDEO_WIDTH*$VIDEO_HEIGHT)*$VIDEO_FPS)*$BPF)/1000" | bc)

#Apply different template by Resolution Type
VIDEO_RESOLUTION=$(optimal_res $VIDEO_WIDTH)
if [ $VIDEO_RESOLUTION == "1080" ]; then
    VIDEO_RES_TXT="1080p, 1920x1080, 2.07 megapixels, Full HD"
    X264_PRESET="slow"
    H264_PROFILE="high"
    H264_LEVEL="4.1"
fi
if [ $VIDEO_RESOLUTION == "720" ]; then
    VIDEO_RES_TXT="720p, 1280x720, 0.92 megapixels, HD"
    X264_PRESET="slow"
    H264_PROFILE="high"
    H264_LEVEL="3.1"
fi
if [ $VIDEO_RESOLUTION == "576" ]; then
    VIDEO_RES_TXT="576p, 1024x576, 0.59 megapixels, PAL widescreen"
    X264_PRESET="medium"
    H264_PROFILE="high"
    H264_LEVEL="3.1" 
fi
if [ $VIDEO_RESOLUTION == "480" ]; then
    VIDEO_RES_TXT="480p, 848x480, 0.41 megapixels, NTSC widescreen"
    X264_PRESET="medium"
    H264_PROFILE="main"
    H264_LEVEL="3.1"
fi
if [ $VIDEO_RESOLUTION == "432" ]; then
    VIDEO_RES_TXT="432p, 768x432, 0.33 megapixels"
    X264_PRESET="fast"
    H264_PROFILE="main"
    H264_LEVEL="3.1"
fi
if [ $VIDEO_RESOLUTION == "360" ]; then
    VIDEO_RES_TXT="360p, 640x360, 0.23 megapixels"
    X264_PRESET="fast"
    H264_PROFILE="baseline"
    H264_LEVEL="3.1"
fi
if [ $VIDEO_RESOLUTION == "240" ]; then
    VIDEO_RES_TXT="240p, 424x240, 0.10 megapixels"
    X264_PRESET="fast"
    H264_PROFILE="baseline"
    H264_LEVEL="3.0"
fi

#### PRINT A SUMMARY ####
#########################
echo "There are $AUDIO_TRACK_COUNT audio tracks:"
if [ $AUDIO_TRACK_COUNT -gt 1 ]; then
    for (( I=1; I <= "$AUDIO_TRACK_COUNT"; I++ )); do
        echo "Track $I: ${ARLANG[$I]}, ${ARCHAN[$I]}"
    done
fi
echo "It will be reoganize as:"
echo "--audio $AUDIO_ARG"
echo "--aencoder $AUDIO_ENCODER_ARG"
echo "--ab $AUDIO_BITRATE_ARG"
echo "--mixdown $AUDIO_MIXDOWN_ARG"
echo "--arate $AUDIO_SAMPLERATE_ARG"
echo "For a width of $VIDEO_WIDTH px, the better format name is $VIDEO_RES_TXT"
echo "The calculed video bitrate is $VIDEO_BITRATE kbps"

#### Creat HandBrakeCLI commande line ####
##########################################
#https://trac.handbrake.fr/wiki/CLIGuide

#Source Options
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --format $VIDEO_TARGET_EXT"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --markers"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --large-file"
#Video
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --encoder x264"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --x264-preset $X264_PRESET"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --h264-profile $H264_PROFILE"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --h264-level $H264_LEVEL"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --vb $VIDEO_BITRATE"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --encopts $X264_OPTS"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --cfr"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --two-pass --turbo"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --rate $VIDEO_FPS"
#Audio
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --audio $AUDIO_ARG"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --aencoder $AUDIO_ENCODER_ARG"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --ab $AUDIO_BITRATE_ARG"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --mixdown $AUDIO_MIXDOWN_ARG"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --arate $AUDIO_SAMPLERATE_ARG"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --drc 0.0,0.0"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --audio-copy-mask aac,ac3,dtshd,dts,mp3"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --audio-fallback ffac3"
#Picture Settings
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --loose-anamorphic --modulus 2"
#Filters
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --deinterlace 2"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --decomb"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --detelecine"

#### Execute the HandBrakeCLI commande line ####
################################################
echo "$HANDBRAKECLI_PATH $HANDBRAKE_ARGVS --input \"$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT\" --output \"$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_TARGET_EXT\""

time "$HANDBRAKECLI_PATH" $HANDBRAKE_ARGVS \
    --input "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT" \
    --output "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_TARGET_EXT" \
    2>&1 | tee -a "$WORKINGDIR/$VIDEO_SHORTNAME.log"

if [ $? != 0 ]; then
    echo "Error: The encode script have exit with errors..."
    echo " The programm will abort..."
    exit 1
else
    if [ -f "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_TARGET_EXT" ]; then
        echo "Compare movies general duration"
        DURATION_ORIGINE=`expr $($MEDIAINFO_PATH --Inform='General;%Duration%' "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT" | cut -d '.' -f1) / 1000 / 60`
        DURATION_ENCODED=`expr $($MEDIAINFO_PATH --Inform='General;%Duration%' "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_TARGET_EXT" | cut -d '.' -f1) / 1000 / 60`
        echo "Origin video duration: $DURATION_ORIGINE minutes ; Encoded video duration: $DURATION_ENCODED minutes"
        if [ $DURATION_ORIGINE -eq $DURATION_ENCODED ]; then
            #That a good news with they checks we are sure about the Transcoding have work
            echo "Transcode Run successfull..."
            #Theorically-you could delete the source video
            #It script is make for let a other script do it delete, that because the TVH PVR database should be informe about the new filename path
            #In case you really want to delete the source file uncomment the line below, you sure 99.99% the Media file is OK
            #rm "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT"
        else
            echo "Error: Source file and encoded file haven't the same duration..."
            echo " The programm will abort..."
            exit 1                        
        fi
    else
        echo "Error: File \"$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_TARGET_EXT\" don't exist..."
        echo " The programm will abort..."
        exit 1
    fi
fi
exit 0











