# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import os
import os.path as op

from fontTools.ttLib import TTFont
from bakery_cli.scripts.vmet import metricview
from bakery_cli.fixers import Vmet
from bakery_cli.utils import shutil
from bakery_cli.utils import UpstreamDirectory


def replace_licenseurl(testcase):
    font = TTFont(testcase.operator.path)

    for nameRecord in font['name'].names:
        if nameRecord.nameID == 14:
            if nameRecord.isUnicode():
                nameRecord.string = testcase.placeholderUrlText.encode('utf-16-be')
            else:
                nameRecord.string = testcase.placeholderUrlText
    font.save(testcase.operator.path + '.fix')
    replace_origfont(testcase)


def replace_license_with_short(testcase):
    font = TTFont(testcase.operator.path)

    for nameRecord in font['name'].names:
        if nameRecord.nameID == 13:
            if nameRecord.isUnicode():
                nameRecord.string = testcase.placeholderText.encode('utf-16-be')
            else:
                nameRecord.string = testcase.placeholderText

    testcase.operator.debug('SETTING UP: {}'.format(testcase.placeholderText))
    font.save(testcase.operator.path + '.fix')
    replace_origfont(testcase)


def replace_origfont(testcase):
    targetpath = testcase.operator.path
    command = "$ mv {0}.fix {0}".format(targetpath)
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)
    fixed_font_path = '{}.fix'.format(targetpath)
    if op.exists(fixed_font_path):
        shutil.move(fixed_font_path, targetpath)


def fix_metrics(testcase):
    """ Fix vmet table with actual min and max values """
    targetpath = os.path.dirname(testcase.operator.path)
    SCRIPTPATH = 'fontbakery-fix-vertical-metrics.py'

    directory = UpstreamDirectory(targetpath)

    paths = []
    for f in directory.BIN:
        path = op.join(targetpath, f)
        paths.append(path)

    command = "$ {0} --autofix {1}"
    command = command.format(SCRIPTPATH, ' '.join(paths))
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)

    Vmet.fix(paths)

    for path in paths:
        try:
            shutil.move(path + '.fix', path, log=testcase.operator.logger)
        except IOError:
            pass

    command = "$ {0} {1}".format(SCRIPTPATH, ' '.join(paths))
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)
        testcase.operator.debug(metricview(paths))


def rename(testcase):
    targetpath = testcase.operator.path

    new_targetpath = op.join(op.dirname(targetpath),
                             testcase.expectedfilename)
    shutil.move(targetpath, new_targetpath, log=testcase.operator.logger)

    testcase.operator.path = new_targetpath
