#! /bin/bash
#Write by Tuxa <tuxa galaxie.eu.org>
# It script it publish on GNU GENERAL PUBLIC LICENSE
#http://www.gnu.org/licenses/gpl-3.0.en.html

#IT SCRIPT HAVE FINAL TARGET AS 16:9 Format Ratio

#######################################
######DEFINE SOME BASIC VARIABLES######
#######################################
SCRIPTNAME="tvh-transcoder.sh"
VERION="0.5"

#######################################
###          User Settings          ###
#######################################
FAVORITE_LANGUAGE="Francais"
VIDEO_TARGET_EXT="mkv"
X264_OPTS="open_gop=0:rc-lookahead=50:ref=6:bframes=6:me=umh:subme=8:trellis=0:analyse=all:b-adapt=2:nal_hrd=none:fast_pskip=0:bframes=6:direct=auto:weightb=1:weightp=2:vbv-bufsize=24000:vbv-maxrate=24000"
VIDEO_FPS="25"

#Choose a MAX HEIGHT.
# 576p  DVD PAL  16:9
# 720p  HD Ready 16:9
# 1080p Full HD  16:9
# 2160p UHDTV1   16:9
# 4320p UHDTV2   16:9

#MAX_HEIGHT=576
MAX_HEIGHT=720
#MAX_HEIGHT=1080
#MAX_HEIGHT=2160
#MAX_HEIGHT=4320

#######################################
###         Core Script Area        ###
#######################################
######     HANDBRAKECLI CHECK    ######
#######################################
HANDBRAKECLI_PATH=`which HandBrakeCLI`
if [ ! $HANDBRAKECLI_PATH ]; then
    echo "HandBrakeCLI is require,\`which HandBrakeCLI\` return nothing"
    echo " Please install \"HandBrakeCLI\" or verify it is aviable on your \$PATH env var"
    echo " $SCRIPTNAME will abort..."
    exit 1
fi

######Check if a parameter is all ready present######
#####################################################
if ( [ ! "$1" ] || [ $# -eq 0 ] ); then
    echo "$SCRIPTNAME Version: $VERION"
    echo "Please, invoke it script with the path of a movie"
    echo "Fews Exemples: "
    echo "./$SCRIPTNAME ./my_super_movie.ts"
    echo "./$SCRIPTNAME ../a/other/directory/my_super_movie.ts"
    echo "./$SCRIPTNAME /full/path/to/the/directory/my_super_movie.ts"
    echo "./$SCRIPTNAME \"/full/path/to/the/directory/With space name.ts\""
    exit 1
fi

######SOURCE FILE CHECK######
############################
if [ ! -f "$1" ]; then
    echo "$SCRIPTNAME Version: $VERION"
    #source file does not exist
    echo "Error: Source file not found "
    echo "Maybe wrong path or missing permissions?"
    echo "Please, invoke it script with the path of a movie"
    echo "Fews Exemples: "
    echo "./$SCRIPTNAME ./my_super_movie.ts"
    echo "./$SCRIPTNAME ../a/other/directory/my_super_movie.ts"
    echo "./$SCRIPTNAME /full/path/to/the/directory/my_super_movie.ts"
    echo "./$SCRIPTNAME \"/full/path/to/the/directory/With space name.ts\""
    exit 1
fi

# Take the first and unic parameter and consider it as the file to encode
readonly VIDEO_FILENAME="$1"
VIDEO_FILENAME_EXT=${VIDEO_FILENAME##*.}
VIDEO_SHORTNAME="`basename "$VIDEO_FILENAME" ".$VIDEO_FILENAME_EXT"`"
WORKINGDIR=`dirname "$VIDEO_FILENAME"`


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
    RESOLUTIONS[7]=3840
    RESOLUTIONS[8]=7680

    NAMES[0]=240
    NAMES[1]=360
    NAMES[2]=432
    NAMES[3]=480
    NAMES[4]=576
    NAMES[5]=720
    NAMES[6]=1080
    NAMES[7]=2160
    NAMES[8]=4320

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

######MEDIA SCAN CHECK######
###########################
SCAN_RESULT=$($HANDBRAKECLI_PATH --scan --main-feature --input "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT" 2>&1)
if [ $? != 0 ]; then
    # There were errors with HandBrakeCLI scan. 
    echo "$HANDBRAKECLI_PATH --scan --main-feature --input \"$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT\" encountered an error."
    exit 1
else
    echo "Starting media analyse..."
    #######ANALAYZE AUDIO TRACKS AND DO LANGUAGE SELECTION######
    ############################################################
    AUDIO_TRACK_LIST=${SCAN_RESULT#*+\ audio\ tracks:}
    AUDIO_TRACK_LIST=${AUDIO_TRACK_LIST%+\ subtitle\ tracks:*}
    AUDIO_TRACK_LIST=${AUDIO_TRACK_LIST// /} # replace " " with ""

    #By default
    T1=1
    AUDIO_TRACK_COUNT=1
    #Search of FAVORITE_LANGUAGE
    for TRACK_INFO in $(echo $AUDIO_TRACK_LIST | sed -e 's/+/\n/g'); do
        IFS=',' read -ra TRACK_INFO_ELEMENT <<< "$TRACK_INFO"; unset IFS
        #DEBUG for control the list
        #for index in "${!TRACK_INFO_ELEMENT[@]}"; do  
            #echo "$index ${TRACK_INFO_ELEMENT[index]}"
        #done
        
        #IF that the tack number 1
        if [ ${TRACK_INFO_ELEMENT[0]} == 1 ]; then
            if $(echo ${TRACK_INFO_ELEMENT[1]} | grep -q "$FAVORITE_LANGUAGE" ); then
                #echo "Found $FAVORITE_LANGUAGE on the track number 1"
                T1=1
            fi
        else
            if $(echo ${TRACK_INFO_ELEMENT[1]} | grep -q "$FAVORITE_LANGUAGE" ); then
                #echo "Found $FAVORITE_LANGUAGE on the track number ${TRACK_INFO_ELEMENT[0]}"
                T1=${TRACK_INFO_ELEMENT[0]}
            fi
        fi
    ((AUDIO_TRACK_COUNT++))
    done

    #Store the original duration in Munites
    DURATION_ORIGINE=${SCAN_RESULT#*+\ duration:\ }
    DURATION_ORIGINE=${DURATION_ORIGINE%+\ size:*}
    IFS=':' read -ra DURATION_ORIGINE_LIST <<< "$DURATION_ORIGINE"; unset IFS
    DURATION_ORIGINE=$(echo "(${DURATION_ORIGINE_LIST[0]}*60)+${DURATION_ORIGINE_LIST[1]}" | bc)

    #######ANALAYZE VIDEO MAIN TITLE ######
    #######################################
    VIDEO_WIDTH=${SCAN_RESULT#*size:\ }
    VIDEO_WIDTH=${VIDEO_WIDTH%,\ pixel\ aspect:*}
    VIDEO_WIDTH=${VIDEO_WIDTH%x*}

    VIDEO_HEIGHT=${SCAN_RESULT#*size:\ }
    VIDEO_HEIGHT=${VIDEO_HEIGHT%,\ pixel\ aspect:*}
    VIDEO_HEIGHT=${VIDEO_HEIGHT#*x}

    #Control of if MAX_HEIGHT if touch
    if [ $VIDEO_HEIGHT ]; then
        echo "VIDEO_HEIGHT=$VIDEO_HEIGHT MAX=$MAX_HEIGHT"
        if [ $VIDEO_HEIGHT -gt $MAX_HEIGHT ]; then
            echo "VIDEO_HEIGHT=$VIDEO_HEIGHT it will be resize to VIDEO_HEIGHT=$MAX_HEIGHT"
            VIDEO_HEIGHT=$MAX_HEIGHT
            VIDEO_WIDTH=$(echo "($VIDEO_HEIGHT*16/9)" | bc)
        else
            unset MAX_HEIGHT
        fi
    fi
fi

#######AUDIO TRACKS MANAGEMENT######
####################################

AUDIO_ARG="$T1,$T1"
AUDIO_ENCODER_ARG="faac,copy:ac3"
AUDIO_BITRATE_ARG="128,Auto"
AUDIO_SAMPLERATE_ARG="44.1,Auto"
AUDIO_MIXDOWN_ARG="dpl2,none"

####### VIDEO MANAGEMENT ######
###############################

#Apply different template by Resolution Type.
#echo "Call optimal_res $VIDEO_WIDTH"
VIDEO_RESOLUTION=$(optimal_res $VIDEO_WIDTH)
if [ $VIDEO_RESOLUTION == "4320" ]; then
    BPF=0.020
    VIDEO_RES_TXT="4320p, 7680×4320, 33.18 megapixels, UHDTV2 or 8K"
    X264_PRESET="slower"
    H264_PROFILE="high"
    H264_LEVEL="5.1"
fi
if [ $VIDEO_RESOLUTION == "2160" ]; then
    BPF=0.040
    VIDEO_RES_TXT="2160p, 3840×2160, 8.00 megapixels, UHDTV1 or 4K"
    X264_PRESET="slower"
    H264_PROFILE="high"
    H264_LEVEL="5.1"
fi
if [ $VIDEO_RESOLUTION == "1080" ]; then
    BPF=0.066
    VIDEO_RES_TXT="1080p, 1920x1080, 2.07 megapixels, Full HD"
    X264_PRESET="slower"
    H264_PROFILE="high"
    H264_LEVEL="4.1"
fi
if [ $VIDEO_RESOLUTION == "720" ]; then
    BPF=0.082
    VIDEO_RES_TXT="720p, 1280x720, 0.92 megapixels, HD"
    X264_PRESET="slow"
    H264_PROFILE="high"
    H264_LEVEL="4.1"
fi
if [ $VIDEO_RESOLUTION == "576" ]; then
    BPF=0.082
    VIDEO_RES_TXT="576p, 1024x576, 0.59 megapixels, PAL widescreen"
    X264_PRESET="slow"
    H264_PROFILE="high"
    H264_LEVEL="3.1" 
fi
if [ $VIDEO_RESOLUTION == "480" ]; then
    BPF=0.100
    VIDEO_RES_TXT="480p, 848x480, 0.41 megapixels, NTSC widescreen"
    X264_PRESET="medium"
    H264_PROFILE="main"
    H264_LEVEL="3.1"
fi
if [ $VIDEO_RESOLUTION == "432" ]; then
    BPF=0.100
    VIDEO_RES_TXT="432p, 768x432, 0.33 megapixels"
    X264_PRESET="fast"
    H264_PROFILE="main"
    H264_LEVEL="3.1"
fi
if [ $VIDEO_RESOLUTION == "360" ]; then
    BPF=0.125
    VIDEO_RES_TXT="360p, 640x360, 0.23 megapixels"
    X264_PRESET="fast"
    H264_PROFILE="baseline"
    H264_LEVEL="3.1"
fi
if [ $VIDEO_RESOLUTION == "240" ]; then
    BPF=0.150
    VIDEO_RES_TXT="240p, 424x240, 0.10 megapixels"
    X264_PRESET="fast"
    H264_PROFILE="baseline"
    H264_LEVEL="3.0"
fi
#Default BIT*(pixel/frame)
#BPF=0.082
# Calcul of the bit rate, hooooo magic !
VIDEO_BITRATE=$(echo "((($VIDEO_WIDTH*$VIDEO_HEIGHT)*$VIDEO_FPS)*$BPF)/1000" | bc)

#### PRINT A SUMMARY ####
#########################
if [ $AUDIO_TRACK_COUNT -gt 1 ]; then
    for I in $(echo $AUDIO_TRACK_LIST | sed -e 's/+/\n/g'); do
        echo $I
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
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --audio-copy-mask aac,ac3,dtshd,dts"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --audio-fallback ffac3"
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --normalize-mix 1"
#Picture Settings
if [ $MAX_HEIGHT ]; then
    HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --maxHeight $VIDEO_HEIGHT"
fi
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --loose-anamorphic --modulus 2"
#Filters
HANDBRAKE_ARGVS="$HANDBRAKE_ARGVS --decomb"


#### Execute the HandBrakeCLI commande line ####
################################################
echo "$HANDBRAKECLI_PATH $HANDBRAKE_ARGVS --input \"$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_FILENAME_EXT\" --output \"$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_TARGET_EXT\""
#exit
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
        END_FILE_SCAN_RESULT=$($HANDBRAKECLI_PATH --scan --main-feature --input "$WORKINGDIR/$VIDEO_SHORTNAME.$VIDEO_TARGET_EXT" 2>&1)
        DURATION_ENCODED=${END_FILE_SCAN_RESULT#*+\ duration:\ }
        DURATION_ENCODED=${DURATION_ENCODED%+\ size:*}
        IFS=':' read -ra DURATION_ENCODED_LIST <<< "$DURATION_ENCODED"; unset IFS
        DURATION_ENCODED=$(echo "(${DURATION_ENCODED_LIST[0]}*60)+${DURATION_ENCODED_LIST[1]}" | bc)
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











