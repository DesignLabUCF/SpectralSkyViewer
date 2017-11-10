#!/usr/bin/python
# -*- coding: utf-8 -*-
# ====================================================================
# Copyright (c) 2017 University of Central Florida
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ====================================================================
# @author: Joe Del Rocco
# @since: 11/02/2017
# @summary: A module that handles loading/checking sky data from the data directory.
# ====================================================================
import os
import csv
from datetime import datetime
import numpy as np
import exifread


HDRRawExts = ['.cr2', '.raw', '.dng']

'''
Function to extract the "DateTimeOriginal" EXIF value of an image.
:param filepath: Path to image
'''
def imageEXIFDateTime(filepath):
    strDateTime = imageEXIFTag(filepath, "EXIF DateTimeOriginal")
    if strDateTime is None or len(strDateTime) <= 0:
        return datetime.min
    return datetime.strptime(strDateTime, '%Y:%m:%d %H:%M:%S')

'''
Function to extract the EXIF value of a particular tag.
:param filepath: Path to image
:param tag: EXIF tagname (not code) provided by module exifread
'''
def imageEXIFTag(filepath, tag):
    result = None
    with open(filepath, 'rb') as f:
        tags = exifread.process_file(f, details=False, stop_tag=tag)
        if tag in tags.keys():
            result = tags[tag]
    return str(result) if result is not None else None

'''
Function to extract all important EXIF data from an image.
:param filepath: Path to image
'''
def imageEXIF(filepath):
    data = {}
    with open(filepath, 'rb') as f:
        data = exifread.process_file(f, details=False)
    return data

'''
'''
def loadSunPath(filepath, isDir=True):
    # format should be a csv with the following columns:
    # Date, Time, Topocentric zenith angle, Topocentric azimuth angle (eastward from N)

    if (isDir):
        filepath = os.path.join(filepath, 'spa.csv')
    if (not os.path.exists(filepath)):
        return []

    # we will swap the order of (zenith, azimuth) to be consistent with rest of program (theta, phi)
    # theta = solar azimuth
    # phi = solar altitude (90 - solar zenith)

    sunpath = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)
        for row in reader:
            # we only care about rows with a valid timestamp
            dt = datetime.min
            try:
                dts = row[0] + " " + row[1]
                dt = datetime.strptime(dts, "%m/%d/%Y %H:%M:%S")
            except ValueError:
                continue
            point = [float(row[3]), 90-float(row[2]), dt]
            # we only care about phi when sun is visible (not on other side of Earth)
            if (point[1] >=0 and point[1] <= 90):
                sunpath.append(point)
    return sunpath

'''
Function to check if a raw data photo is available, given a path to an existing photo.
:param hdrImgpath: Path to a photo in the HDR folder of a capture date in the data directory.
:note: This assumes the raw data file is the same name (but different extension) of given file.
'''
def isHDRRawAvailable(hdrImgPath):
    if (not os.path.exists(hdrImgPath)):
        return False
    pathSplit = os.path.splitext(hdrImgPath.lower())
    for ext in HDRRawExts:
        if (pathSplit[1] == ext):
            return True
        elif (os.path.exists(pathSplit[0] + ext)):
            return True
    return False

'''
'''
def loadASDFile(filepath):
    if (not os.path.exists(filepath)):
        return [], []
    xdata, ydata = np.loadtxt(filepath, skiprows=1, unpack=True)
    return xdata, ydata