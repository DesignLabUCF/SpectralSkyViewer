#!/usr/bin/python
# -*- coding: utf-8 -*-
#====================================================================
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
#====================================================================
# @author: Joe Del Rocco
# @since: 10/25/2016
# @summary: A module with general useful functionality.
#====================================================================

__all__ = ['clamp', 'normalize', 'verifyDateTime', 'findFiles', 'cleanFolder', 'copy', 'killProcess', 'runCMD']

import os
import shutil
import subprocess
import shlex
import logging
import exifread
from datetime import datetime
from threading import Timer
from datetime import datetime


'''
Clamp a number to a range.
'''
def clamp(n, minval, maxval):
    return min(max(n, minval), maxval)

'''
Normalize a number between 0-1.
'''
def normalize(n, minval, maxval):
    return float(n-minval)/float(maxval-minval)

'''
Verify that a string is a valid date or datetime
:param datestr: String that is to be verified.
:param datefmtstr: Format datetime string (e.g. "%Y-%m-%d")
'''
def verifyDateTime(datestr, datefmtstr):
    try:
        datetime.strptime(datestr, datefmtstr)
        return True
    except ValueError:
        return False

'''
Get the modification datetime from a file.
:param filepath: Path to file to get modification time from
'''
def fileModDateTime(filepath):
    t = os.path.getmtime(filepath)
    return datetime.fromtimestamp(t)

'''
Function to extract the "DateTimeOriginal" EXIF value of an image.
:param filepath: Path to image
'''
def imageEXIFDateTime(filepath):
    strDateTime = imageEXIFTag(filepath, "EXIF DateTimeOriginal")
    if strDateTime is None or len(strDateTime) <= 0:
        return datetime(1,1,1)
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
Helper function that returns a list of all files, directories, or both, immediate or recursive.
:param mode: 0=both, 1=files, 2=dir
:param recursive: Immediate top-level list or recursive list
:param ext: File extension to filter by
'''
def findFiles(dirpath, mode=0, recursive=False, ext=""):
    stuff = []
    if len(ext) > 0:
        ext = ext.strip().lower()
        if ext[0] != ".":
            ext = "." + ext
    # immediate top-level list
    if not recursive:
        for entry in os.listdir(dirpath):
            fullpath = os.path.join(dirpath, entry)
            if mode == 1 or mode == 0:
                base, extension = os.path.splitext(fullpath.strip().lower())
                if os.path.isfile(fullpath):
                    if len(ext) > 0:
                        if extension == ext:
                            stuff.append(fullpath)
                    else:
                        stuff.append(fullpath)
            if mode == 2 or mode == 0:
                if os.path.isdir(fullpath):
                    stuff.append(fullpath)
    # recursive list
    else:
        for root, dirs, files in os.walk(dirpath):
            if mode == 1 or mode == 0:
                for file in files:
                    fullpath = os.path.join(root, file)
                    base, extension = os.path.splitext(fullpath.strip().lower())
                    if len(ext) > 0:
                        if extension == ext:
                            stuff.append(fullpath)
                    else:
                        stuff.append(fullpath)
            if mode == 2 or mode == 0:
                for dir in dirs:
                    fullpath = os.path.join(root, dir)
                    stuff.append(fullpath)
    return stuff

'''
Helper function delete all files and folders given a folder.
'''
def cleanFolder(dirpath):
    for filename in os.listdir(dirpath):
        filepath = os.path.join(dirpath, filename)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath)
        except Exception as ex:
            logging.error(ex.message)

'''
Helper function to copy a single file or filetree from one location to another.
'''
def copy(src, dest):
    try:
        if os.path.isfile(src):
            shutil.copy(src, dest)
        else:
            for filename in os.listdir(src):
                srcfile = os.path.join(src, filename)
                destfile = os.path.join(dest, filename)
                if os.path.isfile(srcfile):
                    shutil.copy(srcfile, destfile)
                else:
                    shutil.copytree(srcfile, destfile)
    except Exception as ex:
        logging.error(ex.message)

'''
Helper function to kill a process.
'''
def killProcess(process, timeout):
    timeout["value"] = True
    process.kill()

'''
Helper function to run a shell command with timeout support.
'''
def runCMD(cmd, timeout_sec):
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timeout = {"value": False}
    timer = Timer(timeout_sec, killProcess, [process, timeout])
    timer.start()
    stdout, stderr = process.communicate()
    timer.cancel()
    return process.returncode, stdout, stderr, timeout["value"]
