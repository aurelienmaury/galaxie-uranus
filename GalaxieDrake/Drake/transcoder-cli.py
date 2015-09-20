#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import os.path
import sys
import io

from subprocess import call, check_output, Popen, STDOUT, PIPE
import string

import time
from operator import itemgetter
import subprocess
import tempfile
import re


class HandBrake(object):
    def __init__(self, filename, max_height=720, enable_multi_language=0, lang1='fra', lang2='eng'):
        self.handbrakecli_path = self.check_handbrake()
        # Source file and output file name
        video_file_name = filename
        video_filename_ext = os.path.splitext(video_file_name)[1]
        video_short_name = os.path.basename(os.path.splitext(video_file_name)[0])

        working_dir = os.path.dirname(filename)
        self.working_dir = os.path.realpath(working_dir)
        self.video_short_name = video_short_name

        if enable_multi_language is not None:
            self.enable_multi_language = enable_multi_language
        else:
            self.enable_multi_language = None

        if lang1 is not None:
            self.lang1 = lang1
        else:
            self.lang1 = None

        if lang1 is not None:
            self.lang2 = lang2
        else:
            self.lang2 = None

        self.video_target_ext = "mkv"
        self.max_height = max_height
        self.max_width = int(self.get_std_max_size(int(self.max_height)))
        self.primary_language = self.lang1
        self.secondary_language = self.lang2
        self.video_name_def = " - " + str(self.max_height) + "p"
        self.video_short_name = string.replace(self.video_short_name,self.video_name_def, "")

        self.input_file = str(os.path.join(self.working_dir, self.video_short_name) + video_filename_ext)
        self.output_file = str(os.path.join(self.working_dir, self.video_short_name) + self.video_name_def + "." + self.video_target_ext)

        if os.path.exists(self.output_file):
            i = 1
            while os.path.exists(os.path.join(self.working_dir, self.video_short_name) + "-" + str(i) + " - " + str(self.max_height) + "p." + self.video_target_ext):
                i += 1
            self.output_file = os.path.join(self.working_dir, self.video_short_name) + "-" + str(i) + " - " + str(self.max_height) + "p." + self.video_target_ext

        #Common Setting
        self.file_title = self.video_short_name
        self.detected_audio = 0
        self.detected_subtitle = 0
        #Initial Scan
        # Start by a initial scan
        self.scan_result = self.get_scan()
        #Audio Setting
        if self.detected_audio:
            #Audio Creation list
            count = 1
            for track_info in self.scan_result[11]:
                if count == 1:
                    self.AUDIO_ARG = str(track_info[0])
                    self.AUDIO_ANAME = str(track_info[1])
                    if (track_info[2] == "AAC") or (track_info[2] == "aac"):
                        self.AUDIO_ENCODER_ARG = "copy:aac"
                        self.AUDIO_BITRATE_ARG = "Auto"
                        self.AUDIO_SAMPLERATE_ARG = "Auto"
                        self.AUDIO_MIXDOWN_ARG = "none"
                    elif (track_info[2] == "AC3") or (track_info[2] == "ac3"):
                        self.AUDIO_ENCODER_ARG = "copy:ac3"
                        self.AUDIO_BITRATE_ARG = "Auto"
                        self.AUDIO_SAMPLERATE_ARG = "Auto"
                        self.AUDIO_MIXDOWN_ARG = "none"
                    elif (track_info[2] == "DTS") or (track_info[2] == "dts"):
                        self.AUDIO_ENCODER_ARG = "copy:dts"
                        self.AUDIO_BITRATE_ARG = "Auto"
                        self.AUDIO_SAMPLERATE_ARG = "Auto"
                        self.AUDIO_MIXDOWN_ARG = "none"
                    elif (track_info[2] == "DTSHD") or (track_info[2] == "dtshd"):
                        self.AUDIO_ENCODER_ARG = "copy:dtshd"
                        self.AUDIO_BITRATE_ARG = "Auto"
                        self.AUDIO_SAMPLERATE_ARG = "Auto"
                        self.AUDIO_MIXDOWN_ARG = "none"
                    elif (track_info[2] == "MP3") or (track_info[2] == "mp3"):
                        self.AUDIO_ENCODER_ARG = "copy:mp3"
                        self.AUDIO_BITRATE_ARG = "Auto"
                        self.AUDIO_SAMPLERATE_ARG = "Auto"
                        self.AUDIO_MIXDOWN_ARG = "none"
                    else:
                        if track_info[3] == "2.0ch":
                            self.AUDIO_ENCODER_ARG = "faac"
                            self.AUDIO_BITRATE_ARG = "128"
                            self.AUDIO_SAMPLERATE_ARG = "Auto"
                            self.AUDIO_MIXDOWN_ARG = "dpl2"
                        if track_info[3] == "5.1ch":
                            self.AUDIO_ENCODER_ARG = "faac"
                            self.AUDIO_BITRATE_ARG = "384"
                            self.AUDIO_SAMPLERATE_ARG = "Auto"
                            self.AUDIO_MIXDOWN_ARG = "6ch"
                elif not count == 1:
                    self.AUDIO_ARG = str(self.AUDIO_ARG + "," + str(track_info[0]))
                    self.AUDIO_ANAME = str(self.AUDIO_ANAME) + "," + str(track_info[1])
                    if (track_info[2] == "AAC") or (track_info[2] == "aac"):
                        self.AUDIO_ENCODER_ARG = str(self.AUDIO_ENCODER_ARG) + "," + "copy:aac"
                        self.AUDIO_BITRATE_ARG = str(self.AUDIO_BITRATE_ARG) + "," + "Auto"
                        self.AUDIO_SAMPLERATE_ARG = str(self.AUDIO_SAMPLERATE_ARG) + "," + "Auto"
                        self.AUDIO_MIXDOWN_ARG = str(self.AUDIO_MIXDOWN_ARG) + "," + "none"
                    elif (track_info[2] == "AC3") or (track_info[2] == "ac3"):
                        self.AUDIO_ENCODER_ARG = str(self.AUDIO_ENCODER_ARG) + "," + "copy:ac3"
                        self.AUDIO_BITRATE_ARG = str(self.AUDIO_BITRATE_ARG) + "," + "Auto"
                        self.AUDIO_SAMPLERATE_ARG = str(self.AUDIO_SAMPLERATE_ARG) + "," + "Auto"
                        self.AUDIO_MIXDOWN_ARG = str(self.AUDIO_MIXDOWN_ARG) + "," + "none"
                    elif (track_info[2] == "DTS") or (track_info[2] == "dts"):
                        self.AUDIO_ENCODER_ARG = str(self.AUDIO_ENCODER_ARG) + "," + "copy:dts"
                        self.AUDIO_BITRATE_ARG = str(self.AUDIO_BITRATE_ARG) + "," + "Auto"
                        self.AUDIO_SAMPLERATE_ARG = str(self.AUDIO_SAMPLERATE_ARG) + "," + "Auto"
                        self.AUDIO_MIXDOWN_ARG = str(self.AUDIO_MIXDOWN_ARG) + "," + "none"
                    elif (track_info[2] == "DTSHD") or (track_info[2] == "dtshd"):
                        self.AUDIO_ENCODER_ARG = str(self.AUDIO_ENCODER_ARG) + "," + "copy:dtshd"
                        self.AUDIO_BITRATE_ARG = str(self.AUDIO_BITRATE_ARG) + "," + "Auto"
                        self.AUDIO_SAMPLERATE_ARG = str(self.AUDIO_SAMPLERATE_ARG) + "," + "Auto"
                        self.AUDIO_MIXDOWN_ARG = str(self.AUDIO_MIXDOWN_ARG) + "," + "none"
                    elif (track_info[2] == "MP3") or (track_info[2] == "mp3"):
                        self.AUDIO_ENCODER_ARG = str(self.AUDIO_ENCODER_ARG) + "," + "copy:mp3"
                        self.AUDIO_BITRATE_ARG = str(self.AUDIO_BITRATE_ARG) + "," + "Auto"
                        self.AUDIO_SAMPLERATE_ARG = str(self.AUDIO_SAMPLERATE_ARG) + "," + "Auto"
                        self.AUDIO_MIXDOWN_ARG = str(self.AUDIO_MIXDOWN_ARG) + "," + "none"
                    else:
                        if track_info[3] == "2.0ch":
                            self.AUDIO_ENCODER_ARG = str(self.AUDIO_ENCODER_ARG) + "," + "faac"
                            self.AUDIO_BITRATE_ARG = str(self.AUDIO_BITRATE_ARG) + "," + "128"
                            self.AUDIO_SAMPLERATE_ARG = str(self.AUDIO_SAMPLERATE_ARG) + "," + "Auto"
                            self.AUDIO_MIXDOWN_ARG = str(self.AUDIO_MIXDOWN_ARG) + "," + "dpl2"
                        elif track_info[3] == "5.1ch":
                            self.AUDIO_ENCODER_ARG = str(self.AUDIO_ENCODER_ARG) + "," + "faac"
                            self.AUDIO_BITRATE_ARG = str(self.AUDIO_BITRATE_ARG) + "," + "384"
                            self.AUDIO_SAMPLERATE_ARG = str(self.AUDIO_SAMPLERATE_ARG) + "," + "Auto"
                            self.AUDIO_MIXDOWN_ARG = str(self.AUDIO_MIXDOWN_ARG) + "," + "6ch"

                count += 1
            #print "self.AUDIO_ARG = " + str(self.AUDIO_ARG)
            #print "self.AUDIO_ENCODER_ARG = " + str(self.AUDIO_ENCODER_ARG)
            #print "self.AUDIO_BITRATE_ARG = " + str(self.AUDIO_BITRATE_ARG)
            #print "self.AUDIO_SAMPLERATE_ARG = " + str(self.AUDIO_SAMPLERATE_ARG)
            #print "self.AUDIO_MIXDOWN_ARG = " + str(self.AUDIO_MIXDOWN_ARG)
            #print "self.AUDIO_ANAME = " + str(self.AUDIO_ANAME)
        #Subtitle Creation  list
        if self.detected_subtitle:
            count = 1
            for track_info in self.scan_result[12]:
                if count == 1:
                    self.SUBTITLE = str(track_info[0])
                elif not count == 1:
                    self.SUBTITLE = str(self.SUBTITLE + "," + str(track_info[0]))
                count += 1
            self.SUBTITLE_FORCED = "1"
            self.SUBTITLE_DEFAULT = "1"

        #Video Setting
        self.VIDEO_FPS = float(self.scan_result[6])
        self.X264_OPTS = "open_gop=0:rc-lookahead=50:ref=6:bframes=6:me=umh:subme=8:trellis=0:analyse=all:b-adapt=2:nal_hrd=none:fast_pskip=0:bframes=6:direct=auto:weightb=1:weightp=2:vbv-bufsize=24000:vbv-maxrate=24000"
        # Video Picture size
        self.vcodec = self.scan_result[9]

        size = self.scan_result[3].split('x')
        self.video_width = int(size[0])
        self.video_height = int(size[1])

        if int(self.video_height) > int(self.max_height):
            self.video_height = int(self.max_height)
            self.video_width = int(round(int(self.video_height) * float(self.scan_result[5])))
        else:
            autocrop = self.scan_result[7].split('/')
            substract_to_w = int(autocrop[2]) + int(autocrop[3])
            substract_to_h = int(autocrop[0]) + int(autocrop[0])
            self.video_height = int(self.video_height - substract_to_h)
            self.video_width = int(self.video_width - substract_to_w)

        if int(self.video_width) > int(self.max_width):
            self.video_width = int(self.max_width)
            self.video_height = int(round(int(self.video_width) / float(self.scan_result[5])))

        self.VIDEO_RESOLUTION = self.chose_optimal_res(self.video_width)
        megapixels = ("%.2f" % float(float(int(self.video_height * self.video_width) / 1000) / 1000))

        if self.VIDEO_RESOLUTION == 4320:
            self.bpf = 0.020
            self.video_res_txt = str(megapixels) + "Mpx  Close Format: 4320p, 7680×4320, 33.18Mpx, UHDTV2 or 8K"
            self.x264_preset = "slower"
            self.h264_profile = "high"
            self.h264_level = "5.1"
            self.max_height = 4320
            self.max_width = 7680

        if self.VIDEO_RESOLUTION == 2160:
            self.bpf = 0.040
            self.video_res_txt = str(megapixels) + "Mpx  Close Format: 2160p, 3840×2160, 8.00Mpx, UHDTV1 or 4K"
            self.x264_preset = "slower"
            self.h264_profile = "high"
            self.h264_level = "5.1"
            self.max_height = 2160
            self.max_width = 3840

        if self.VIDEO_RESOLUTION == 1080:
            self.bpf = 0.066
            self.video_res_txt = str(megapixels) + "Mpx  Close Format: 1080p, 1920x1080, 2.07Mpx, Full HD"
            self.x264_preset = "slower"
            self.h264_profile = "high"
            self.h264_level = "4.1"
            self.max_height = 1080
            self.max_width = 1920

        if self.VIDEO_RESOLUTION == 720:
            self.bpf = 0.082
            self.video_res_txt = str(megapixels) + "Mpx  Close Format: 720p, 1280x720, 0.92Mpx, HD"
            self.x264_preset = "slow"
            self.h264_profile = "high"
            self.h264_level = "4.1"
            self.max_height = 720
            self.max_width = 1280

        if self.VIDEO_RESOLUTION == 576:
            self.bpf = 0.082
            self.video_res_txt = str(megapixels) + "Mpx  Close Format: 576p, 1024x576, 0.59Mpx, PAL widescreen"
            self.x264_preset = "slow"
            self.h264_profile = "high"
            self.h264_level = "3.1"
            self.max_height = 576
            self.max_width = 1024

        if self.VIDEO_RESOLUTION == 480:
            self.bpf = 0.100
            self.video_res_txt = str(megapixels) + "Mpx  Close Format: 480p, 848x480, 0.41Mpx, NTSC widescreen"
            self.x264_preset = "medium"
            self.h264_profile = "main"
            self.h264_level = "3.1"
            self.max_height = 480
            self.max_width = 848

        if self.VIDEO_RESOLUTION == 432:
            self.bpf = 0.100
            self.video_res_txt = str(megapixels) + "Mpx  Close Format: 432p, 768x432, 0.33Mpx"
            self.x264_preset = "fast"
            self.h264_profile = "main"
            self.h264_level = "3.1"
            self.max_height = 432
            self.max_width = 768

        if self.VIDEO_RESOLUTION == 360:
            self.bpf = 0.125
            self.video_res_txt = str(megapixels) + "Mpx  Close Format: 360p, 640x360, 0.23Mpx"
            self.x264_preset = "fast"
            self.h264_profile = "baseline"
            self.h264_level = "3.1"
            self.max_height = 360
            self.max_width = 640

        if self.VIDEO_RESOLUTION == 240:
            self.bpf = 0.150
            self.video_res_txt = str(megapixels) + "Mpx  Close Format: 240p, 424x240, 0.10Mpx"
            self.x264_preset = "fast"
            self.h264_profile = "baseline"
            self.h264_level = "3.0"
            self.max_height = 240
            self.max_width = 424

        # Final Formula
        self.video_bitrate = int((((self.video_width * self.video_height) * self.VIDEO_FPS) * self.bpf) / 1000)

    def encode(self):
        cmd = list()

        cmd.append(self.handbrakecli_path)

        cmd.append('--input')
        cmd.append(str(self.input_file))

        cmd.append('--output')
        cmd.append(str(self.output_file))

        # Source Options
        cmd.append('--format')
        cmd.append(str(self.video_target_ext))

        cmd.append('--markers')
        #cmd.append('--chapters')

        cmd.append('--large-file')

        # Video
        cmd.append('--encoder')
        cmd.append('x264')

        cmd.append('--x264-preset')
        cmd.append(str(self.x264_preset))

        cmd.append('--h264-profile')
        cmd.append(str(self.h264_profile))

        cmd.append('--h264-level')
        cmd.append(str(self.h264_level))

        cmd.append('--vb')
        cmd.append(str(self.video_bitrate))

        cmd.append('--encopts')
        cmd.append(str(self.X264_OPTS))

        cmd.append('--cfr')

        cmd.append('--two-pass')
        cmd.append('--turbo')

        cmd.append('--rate')
        cmd.append(str(self.VIDEO_FPS))

        # Audio
        if self.detected_audio:
            #cmd.append('--native-language')
            #cmd.append(str(self.PRIMARY_LANGUAGE))

            #cmd.append('--native-dub')

            cmd.append('--audio')
            cmd.append(str(self.AUDIO_ARG))

            cmd.append('--aencoder')
            cmd.append(str(self.AUDIO_ENCODER_ARG))

            cmd.append('--ab')
            cmd.append(str(self.AUDIO_BITRATE_ARG))

            cmd.append('--mixdown')
            cmd.append(str(self.AUDIO_MIXDOWN_ARG))

            cmd.append('--arate')
            cmd.append(str(self.AUDIO_SAMPLERATE_ARG))

            cmd.append('--drc')
            cmd.append('0.0,0.0')

            cmd.append('--audio-copy-mask')
            cmd.append('aac,ac3,dtshd,dts,mp3')

            cmd.append('--audio-fallback')
            cmd.append('ffac3')

            cmd.append('--aname')
            cmd.append(str(self.AUDIO_ANAME))

        #SubTitles
        if self.detected_subtitle:
            cmd.append('--subtitle')
            cmd.append(str(self.SUBTITLE))

            cmd.append('--subtitle-forced')
            #cmd.append(str(self.SUBTITLE_FORCED))

            cmd.append('--subtitle-default')
            #cmd.append(str(self.SUBTITLE_DEFAULT))

        # Picture Settings
        cmd.append('--maxHeight')
        cmd.append(str(self.video_height))

        cmd.append('--maxWidth')
        cmd.append(str(self.video_width))

        cmd.append('--loose-anamorphic')
        cmd.append('--modulus')
        cmd.append('2')

        # Filters
        cmd.append('--decomb')

        #Execute the CMD
        #filename = tempfile.mktemp("", prefix=self.VIDEO_SHORTNAME + ".tmp.", dir=self.WORKINGDIR)
        filename = tempfile.mktemp("", "hb.", dir=self.working_dir)
        os.environ["TMPDIR"] = self.working_dir
        environment = os.environ
        with io.open(filename, 'wb') as writer, io.open(filename, 'rb', 1) as reader:
            process = subprocess.Popen(cmd, stdout=writer, stderr=writer, env=environment)
            # time.sleep(1)
            while process.poll() is None:
                time.sleep(0.3)
                last_line = open(filename).readlines()
                if len(last_line) == 0:
                    continue
                last_line = last_line[-1]
                match_it = re.search(".*Encoding:\s+(.*)", str(last_line), re.U | re.I)
                if not match_it:
                    continue
                sys.stdout.write("\x1b[2K")
                sys.stdout.write("\r")
                sys.stdout.write(match_it.group(1))
                sys.stdout.flush()

    def get_std_max_size(self, height):
        if height == 4320:
            return int(7680)
        elif height == 2160:
            return int(3840)
        elif height == 1080:
            return int(1920)
        elif height == 720:
            return int(1280)
        elif height == 576:
            return int(1024)
        elif height == 480:
            return int(848)
        elif height == 432:
            return int(768)
        elif height == 360:
            return int(640)
        elif height == 240:
            return int(424)

    def get_fps_infos(self, fps):
        if fps == "23.976":
            return str("23.976 (NTSC Film)")
        elif fps == "25.000" or fps == "25.00" or fps == "25.0" or "25":
            return str("25 (PAL Film/Video)")
        elif fps == "29.970" or fps == "29.97":
            return str("29.97 (NTSC Video)")
        else:
            return str(fps)

    def get_display_aspect_infos(self, ratio):
        if ratio == "1.25":
            return str("(5:4) Early television & large-format computer monitors")
        elif ratio == "1.33":
            return str("(4:3) Traditional television & computer monitor standard")
        elif ratio == "1.375":
            return str("Academy standard film aspect ratio")
        elif ratio == "1.41" or ratio == 1.4142:
            return str("ISO 216 paper sizes (A4)")
        elif ratio == "1.43":
            return str("IMAX motion picture film format")
        elif ratio == "1.5":
            return str("(3:2) Classic 35 mm still photographic film")
        elif ratio == "1.6":
            return str("(8:5) (aka 16:10) Common computer screen ratio")
        elif ratio == "1.6180":
            return str("(16.18:10) The golden ratio")
        elif ratio == "1.6667":
            return str("(5:3) European Widescreen std. Native Super 16 mm film")
        elif ratio == "1.77" or ratio == "1.78":
            return str("(16:9) HD video std. U.S. digital broadcast TV std.")
        elif ratio == "1.85":
            return str("U.S. Widescreen cinema standard")
        elif ratio == "2.39":
            return str("Current widescreen cinema standard")
        else:
            return str(ratio)

    def chose_optimal_res(self, video_width):

        resolutions = list()
        resolutions.append(424)
        resolutions.append(640)
        resolutions.append(768)
        resolutions.append(848)
        resolutions.append(1024)
        resolutions.append(1280)
        resolutions.append(1920)
        resolutions.append(3840)
        resolutions.append(7680)

        names = list()
        names.append(240)
        names.append(360)
        names.append(432)
        names.append(480)
        names.append(576)
        names.append(720)
        names.append(1080)
        names.append(2160)
        names.append(4320)

        width = video_width
        best_guess = -1
        index = 0
        maxi = len(resolutions)

        while not best_guess == index:
            if index < maxi:
                res_gap = resolutions[index + 1] - resolutions[index]
                step_threshold = res_gap / 2
                cur_res = resolutions[index]
                width_gap = int(width) - cur_res
                best_guess = index
                if width_gap > step_threshold:
                    index += 1
            else:
                best_guess = index

        return names[best_guess]

    def get_scan(self):
        output = check_output([self.handbrakecli_path,
                               '--scan',
                               '--main-feature',
                               '--input', self.input_file],
                              stderr=STDOUT)
        #Search for Video Codec information
        if re.search("Video PIDS : \n\[\d+:\d+:\d+\]\s+.*?\stype\s(.*?)\s\(", output, re.U | re.I):
            vcodec = re.search("Video PIDS : \n\[\d+:\d+:\d+\]\s+.*?\stype\s(.*?)\s\(", output, re.U | re.I)
        elif re.search("Stream\s.*Video:\s(.*?),\s", output, re.U | re.I):
            vcodec = re.search("Stream\s.*Video:\s(.*?),\s", output, re.U | re.I)
        elif re.search("Video Streams : \n\[\d+:\d+:\d+\]\s+.*?\stype\s(.*?)\s\(", output, re.U | re.I):
            vcodec = re.search("Video Streams : \n\[\d+:\d+:\d+\]\s+.*?\stype\s(.*?)\s\(", output, re.U | re.I)
        else:
            vcodec = "Unknown"

        #Search for common informations
        #+ title 1:
        #  + stream: ./Matrix1.mkv
        #  + duration: 02:16:19
        #  + size: 1920x1080, pixel aspect: 1/1, display aspect: 1.78, 23.976 fps
        #  + autocrop: 142/142/0/0
        #  + support opencl: no
        #  + support hwd: not built-in
        #  + chapters:
        #    + 1: cells 0->0, 0 blocks, duration 02:16:19
        #  + audio tracks:
        #    + 1, Francais (AC3) (5.1 ch) (iso639-2: fra), 48000Hz, 640000bps
        #    + 2, English (AC3) (5.1 ch) (iso639-2: eng), 48000Hz, 640000bps
        #  + subtitle tracks:
        #    + 1, French (iso639-2: fra) (Text)(UTF-8)
        #    + 2, English (iso639-2: eng) (Text)(UTF-8)
        #
        #HandBrake has exited.
        #+ title 1:
        #  + stream: /home/hts/Transcode/Alien_theory/alien-theory-_-les-catastrophes-climatiques.2014-01-26.01-24.ts
        #  + duration: 00:56:44
        #  + size: 1920x1080, pixel aspect: 1/1, display aspect: 1.78, 25.000 fps
        #  + autocrop: 2/0/0/0
        #  + support opencl: no
        #  + support hwd: not built-in
        #  + chapters:
        #    + 1: cells 0->0, 0 blocks, duration 00:56:44
        #  + audio tracks:
        #    + 1, Francais (E-AC3) (2.0 ch) (Dolby Surround) (iso639-2: fra)
        #    + 2, Unknown (E-AC3) (2.0 ch) (Dolby Surround) (iso639-2: und)
        #    + 3, Unknown (E-AC3) (2.0 ch) (Dolby Surround) (iso639-2: und)
        #  + subtitle tracks:
        #
        #HandBrake has exited.
        title = re.search('\+ title (\d+):', output, re.U | re.I)
        stream = re.search('  \+ stream: (.*?)\n', output, re.U | re.I)
        duration = re.search('  \+ duration: (\d+:\d+:\d+)', output, re.U | re.I)
        size = re.search('  \+ size: (.*?),', output, re.U | re.I)
        pixel_aspect = re.search('pixel aspect: (.*?),', output, re.U | re.I)
        display_aspect = re.search('display aspect: (.*?),', output, re.U | re.I)
        fps = re.search(', (\d+|\d+.\d+) fps\n', output, re.U | re.I)
        autocrop = re.search('autocrop: (\d+/\d+/\d+/\d+)', output, re.U | re.I)

        #Audio Tracks detection and short by Language
        audio_tracks_motif = "\+ audio tracks:\\n.*?\+([\w|\W]+)  \+ subtitle tracks:"
        if re.search(audio_tracks_motif, output, re.U | re.I):
            self.detected_audio =1
            audio_tracks = re.search(audio_tracks_motif, output, re.U | re.I)
            audio_tracks = str(audio_tracks.group(1))
            audio_tracks = string.replace(audio_tracks, "\n", "")
            audio_tracks = string.replace(audio_tracks, " ", "")
            audio_tracks = string.replace(audio_tracks, ")(", ",")
            audio_tracks = string.replace(audio_tracks, "(", ",")
            audio_tracks = string.replace(audio_tracks, ")", "")
            tmp_audio_tracks_list = audio_tracks.split("+")
            audio_tracks_list = list()
            for I in tmp_audio_tracks_list:
                audio_tracks_list.append(I.split(","))
            #Shorted Audio Track
            audio_tracks_list_shorted = list()

            if self.enable_multi_language:
                #Add Native Language
                if self.primary_language:
                    for I in audio_tracks_list:
                        if len(I) == 5:
                            if I[4] == str("iso639-2:" + self.primary_language):
                                audio_tracks_list_shorted.append(I)
                        if len(I) == 6:
                            if I[5] == str("iso639-2:" + self.primary_language):
                                audio_tracks_list_shorted.append(I)
                        if len(I) == 7:
                            if I[6] == str("iso639-2:" + self.primary_language):
                                audio_tracks_list_shorted.append(I)
                #Add Secondary Language
                if self.secondary_language:
                    for I in audio_tracks_list:
                        if len(I) == 5:
                            if I[4] == str("iso639-2:" + self.secondary_language):
                                audio_tracks_list_shorted.append(I)
                        if len(I) == 6:
                            if I[5] == str("iso639-2:" + self.secondary_language):
                                audio_tracks_list_shorted.append(I)
                        if len(I) == 7:
                            if I[6] == str("iso639-2:" + self.secondary_language):
                                audio_tracks_list_shorted.append(I)
                #Add the rest
                for I in audio_tracks_list:
                    if len(I) == 5:
                        if not (I[4] == str("iso639-2:" + self.primary_language) or I[4] == str("iso639-2:" + self.secondary_language)):
                            audio_tracks_list_shorted.append(I)
                    if len(I) == 6:
                        if not (I[5] == str("iso639-2:" + self.primary_language) or I[5] == str("iso639-2:" + self.secondary_language)):
                            audio_tracks_list_shorted.append(I)
                    if len(I) == 7:
                        if not (I[6] == str("iso639-2:" + self.primary_language) or I[6] == str("iso639-2:" + self.secondary_language)):
                            audio_tracks_list_shorted.append(I)
            else:
                #Here Multi Language is disable but we test if a particular language have to be select
                #Add Native Language
                if self.primary_language:
                    for I in audio_tracks_list:
                        if len(I) == 5:
                            if I[4] == str("iso639-2:" + self.primary_language):
                                audio_tracks_list_shorted.append(I)
                        if len(I) == 6:
                            if I[5] == str("iso639-2:" + self.primary_language):
                                audio_tracks_list_shorted.append(I)
                        if len(I) == 7:
                            if I[6] == str("iso639-2:" + self.primary_language):
                                audio_tracks_list_shorted.append(I)
                    #In case where the the Native Language is not detect use the frist track
                    if len(audio_tracks_list_shorted) == 0:
                        audio_tracks_list_shorted.append(audio_tracks_list[0])
                else:
                    audio_tracks_list_shorted.append(audio_tracks_list[0])

        else:
            audio_tracks_list = list()
            audio_tracks_list.append(0)
            audio_tracks_list_shorted = list()
            audio_tracks_list_shorted.append(0)

        #SubTitle detection and shorted y language
        subtitle_tracks_motif = "\+ subtitle tracks:\\n.*?\+([\w|\W]+)HandBrake has exited."
        if re.search(subtitle_tracks_motif, output, re.U | re.I):
            self.detected_subtitle = 1
            subtitle_tracks = re.search(subtitle_tracks_motif, output, re.U | re.I)
            subtitle_tracks = str(subtitle_tracks.group(1))
            subtitle_tracks = string.replace(subtitle_tracks, "\n", "")
            subtitle_tracks = string.replace(subtitle_tracks, " ", "")
            subtitle_tracks = string.replace(subtitle_tracks, ")(", ",")
            subtitle_tracks = string.replace(subtitle_tracks, "(", ",")
            subtitle_tracks = string.replace(subtitle_tracks, ")", "")
            tmp_subtitle_tracks_list = subtitle_tracks.split("+")
            subtitle_tracks_list = list()
            for I in tmp_subtitle_tracks_list:
                subtitle_tracks_list.append(I.split(","))
            #Shorted Subtitle Track
            subtitle_tracks_list_shorted = list()
            #Add Native Language
            for I in subtitle_tracks_list:
                if I[2] == str("iso639-2:" + self.primary_language):
                    subtitle_tracks_list_shorted.append(I)
            if self.enable_multi_language:
                #Add Secondary Language
                for I in subtitle_tracks_list:
                    if I[2] == str("iso639-2:" + self.secondary_language):
                        subtitle_tracks_list_shorted.append(I)
                #Add the rest
                for I in subtitle_tracks_list:
                    if not (I[2] == str("iso639-2:" + self.primary_language) or I[2] == str("iso639-2:" + self.secondary_language)):
                        subtitle_tracks_list_shorted.append(I)
        else:
            subtitle_tracks_list = list()
            subtitle_tracks_list.append(0)
            subtitle_tracks_list_shorted = list()
            subtitle_tracks_list_shorted.append(0)
        #Return Scan Informations
        return [title.group(1),
                stream.group(1),
                duration.group(1),
                size.group(1),
                pixel_aspect.group(1),
                display_aspect.group(1),
                fps.group(1),
                autocrop.group(1),
                audio_tracks_list,
                vcodec.group(1),
                subtitle_tracks_list,
                audio_tracks_list_shorted,
                subtitle_tracks_list_shorted
                ]

    def check_handbrake(self):
        if not self.which("HandBrakeCLI"):
            print "HandBrakeCLI is require,"
            print " Please install \"HandBrakeCLI\" or verify it is aviable on your $PATH env var"
            print " " + scriptname_title + " will abort..."
            exit(1)
        else:
            return self.which("HandBrakeCLI")

    def handbrakecli_get_version(self):
        cmd = list()
        output = list()
        tmp_output = list()
        tmp_line = list()
        cmd.append(unicode(self.handbrakecli_path,'utf-8'))
        cmd.append(unicode("-u",'utf-8'))
        output.append(subprocess.check_output(cmd,stderr=STDOUT))
        if output:
            tmp_output = re.split(r'\n', output[0])
            for I in tmp_output:
                if fnmatch.fnmatch(I, 'HandBrake *'):
                    tmp_line = re.split(r' ', I)
                    return tmp_line[0] + " " + tmp_line[1] + " " + tmp_line[2]
        else:
            return "HandBrake v(unknow)"

    def which(self, program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None

    def dur2sec(self, duration):
        (hours,minutes,seconds) = duration.split(':')
        seconds = (int(hours) * 3600) + (int(minutes) * 60) + int(seconds)
        return seconds


#######################################
######DEFINE SOME BASIC VARIABLES######
#######################################
scriptname = "transcoder-cli.py"
version = "0.6"

######Check if a parameter is all ready present######
#####################################################
if len(sys.argv) < 2:
    print scriptname + " Version: " + version
    print "Please, invoke it script with the path of a movie"
    print "Fews Exemples: "
    print "./" + scriptname + " ./my_super_movie.ts"
    print "./" + scriptname + " ../a/other/directory/my_super_movie.ts"
    print "./" + scriptname + " /full/path/to/the/directory/my_super_movie.ts"
    print "./" + scriptname + " \"/full/path/to/the/directory/With space name.ts\""
    exit(1)

######SOURCE FILE CHECK######
############################
if not os.path.isfile(sys.argv[1]):
    print scriptname + " Version: " + version
    # source file does not exist
    print "Error: Source file not found "
    print "Maybe wrong path or missing permissions?"
    print "Please, invoke it script with the path of a movie"
    print "Fews Exemples: "
    print "./" + scriptname + " ./my_super_movie.ts"
    print "./" + scriptname + " ../a/other/directory/my_super_movie.ts"
    print "./" + scriptname + " /full/path/to/the/directory/my_super_movie.ts"
    print "./" + scriptname + " \"/full/path/to/the/directory/With space name.ts\""
    exit(1)

# Take the first and unic parameter and consider it as the file to encode
video_filename = sys.argv[1]

######USUAL FONCTION######
##########################

# def optimal_res():

# scan the dvd for the titles
print "Running: " + scriptname + " Version: " + version
print "Scaning ..."
hb = HandBrake(video_filename)
print ""
#hb.get_scan()

# print hb.VIDEO_WIDTH
# print hb.VIDEO_HEIGHT



# File
#print hb.HANDBRAKECLI_PATH
#print "--input " + str(hb.INPUT_FILE)
#print "--output " + str(hb.OUTPUT_FILE)
# Source Options
#print "--format " + hb.VIDEO_TARGET_EXT
#print "--markers"
#print "--large-file"
# Video
#print "--encoder x264"
#print "--x264-preset " + str(hb.X264_PRESET)
#print "--h264-profile " + str(hb.H264_PROFILE)
#print "--h264-level " + str(hb.H264_LEVEL)
#print "--vb " + str(hb.VIDEO_BITRATE)
#print "--encopts " + str(hb.X264_OPTS)
#print "--cfr"
#print "--two-pass --turbo"
#print "--rate " + str(hb.VIDEO_FPS)
# Audio
#print "--audio " + str(hb.AUDIO_ARG)
#print "--aencoder " + str(hb.AUDIO_ENCODER_ARG)
#print "--ab " + str(hb.AUDIO_BITRATE_ARG)
#print "--mixdown " + str(hb.AUDIO_MIXDOWN_ARG)
#print "--arate " + str(hb.AUDIO_SAMPLERATE_ARG)
#print "--drc 0.0,0.0"
#print "--audio-copy-mask aac,ac3,dtshd,dts"
#print "--audio-fallback ffac3"
#print "--normalize-mix 1"
# Picture Settings
#print "--maxHeight " + str(hb.VIDEO_HEIGHT)
#print "--loose-anamorphic --modulus 2"
# Filters
#print "--decomb"

input_file = hb.INPUT_FILE
output_file = hb.OUTPUT_FILE
video_title = hb.FILE_TITLE
duration = hb.SCAN_RESULT[2]
size = hb.SCAN_RESULT[3]
pixel_aspect = hb.SCAN_RESULT[4]
display_aspect = hb.SCAN_RESULT[5]
display_aspect_infos = hb.get_display_aspect_infos(str(display_aspect))
fps = hb.SCAN_RESULT[6]
fps_infos = hb.get_fps_infos(fps)
fps_target_infos = hb.get_fps_infos(hb.VIDEO_FPS)
autocrop = hb.SCAN_RESULT[7]
audio_track_list = hb.SCAN_RESULT[8]
audio_info_list = hb.audio_info_list
vcodec = hb.VCODEC
width = hb.VIDEO_WIDTH
height = hb.VIDEO_HEIGHT
res_txt = hb.VIDEO_RES_TXT
bit_rate = hb.VIDEO_BITRATE
x264_preset = hb.X264_PRESET
h264_profile = hb.H264_PROFILE
h264_level = hb.H264_LEVEL
bpf = ("%.3f" % float(hb.BPF))

#list_element_num = int(hb.AUDIO_ARG[2:]) - 1
list_element_num = int(hb.AUDIO_ARG) - 1
found_language = hb.FOUND_LANGUAGE

print "Title:        : \"" + str(video_title) + "\"  Duration: " + str(duration)
print ""
print "Source        : " + str(input_file)
print "Dimensions    : " + str(size)
print "Video Codec   : " + str(vcodec.title())
print "Autocrop      : " + str(autocrop)
print "Pixel Aspect  : " + str(pixel_aspect)
print "Display Aspect: " + str(display_aspect) + ":1 " + str(display_aspect_infos)
print "Frame Rate    : " + str(fps_infos)
print "Audio Track(s): "
count = 0
for track_info in audio_track_list:
    print " "+str(audio_info_list[count])
    count += 1
print ""
print "Destination   : " + str(output_file)
print "Dimensions    : " + str(width)+"x"+str(height)+" "+ str(res_txt)
print "Bitrate       : " + str(bit_rate)+" kbps  BPF: "+str(bpf)
print "x264 Preset   : " + str(x264_preset.title())
print "H.264 Profile : " + str(h264_profile.title())
print "H.264 Level   : " + str(h264_level)
print "Display Aspect: " + str(display_aspect) + ":1 " + str(display_aspect_infos)
print "Frame Rate    : " + str(fps_target_infos)
print "Audio Track(s): "
#print " 1 <- " + str(hb.AUDIO_ARG[2:]) + " faac rate=44100Hz bitrate=128000 "+str(found_language)+" (DPL-2) (2.0 ch)"
print " 1 <- "+str(audio_info_list[list_element_num])
print "Trancoding:"

hb.encode()

print ""
