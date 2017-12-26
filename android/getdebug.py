#!/usr/bin/env python

# -*- coding:utf-8 -*-

'''
@author borney
@date 2017-12-25
smali&baksmali:https://bitbucket.org/JesusFreke/smali/downloads/
apktool:http://ibotpeaches.github.io/Apktool/
'''
import os
import sys
import getopt
import commands
import zipfile
import shutil
from optparse import OptionParser
from xml.dom import minidom

DEBUG = False

def printerror(msg):
    print '\033[31m' + msg + '\033[0m'

def printsuccess(msg):
    print '\033[92m' + msg + '\033[0m'

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def parser_args():
    parser = OptionParser(description='Generate debug apk by packageName or apk file.', usage="getdebug.py -a <apksigner jar> --pk8=<pk8 file> --pem=<pem file> arg1 arg2...")
    parser.add_option("--apksigner", dest="apksigner", metavar="<file>", help="the apksigner file")
    parser.add_option("--pk8", dest="pk8", metavar="<file>", help="the pk8 sign file")
    parser.add_option("--pem", dest="pem", metavar="<file>", help="the pem sign file")
    parser.add_option("--arm", dest="arm", metavar="<32|64>", default="32", help="the arm type")
    parser.add_option("-a", dest="aversion", metavar="<android version code>", default="23", help="the android version code")
    parser.add_option("-d", dest="debug", action="store_true", default=False, help="debug this script")

    print "parsering args..."
    return parser.parse_args(sys.argv[1:])

def verify_args(options, args):
    if len(args) <= 0:
        printerror("Error:No package or apk found!!!")
        sys.exit(2)
    if options.apksigner == None:
        printerror("Error:Not specified apksigner!!!")
        sys.exit(2)
    if options.pk8 == None:
        printerror("Error:Not specified pk8 file!!!")
        sys.exit(2)
    if options.pem == None:
        printerror("Error:Not specified pem file!!!")
        sys.exit(2)

    global DEBUG
    DEBUG = options.debug

def exe_command(cmd):
    if DEBUG == True:
        print cmd
    return commands.getstatusoutput(cmd)

"""
check adb and apktool is install
"""
def verify_tools(options):
    print "check adb command..."
    adb = which("adb")
    if adb == None:
        printerror("Error:adb command not found in your environment PATH, please set it.")
        sys.exit(3)

    print "check apktool command..."
    apktool = which("apktool")
    if apktool == None:
        printerror("Error:apktool command not found in your environment PATH, please set it.")
        print "\nAdditional info, see: http://ibotpeaches.github.io/Apktool/"
        sys.exit(3)

    if options.aversion >= "23":
        print "check baksmali/smali command..."
        baksmali = which("baksmali")
        smali = which("smali")
        if baksmali == None or smali == None:
            printerror("Error:baksmali/smali command not found in your environment PATH, please set it.")
            print "\nFor additional info, see: http://ibotpeaches.github.io/Apktool/"
            print "\nFor smali/baksmali info, see: https://github.com/JesusFreke/smali"
            sys.exit(3)

    printsuccess("Environment set success!!!")

"""
check one device connect adb
"""
def check_devices():
    print "check devices..."
    status, result = commands.getstatusoutput("adb devices")
    if status == 0:
        device_count = 0
        for d in result.split('\n'):
            if d.endswith("device"):
                device_count += 1

        if device_count == 0:
            printerror("Error:No devices on connected.")
            sys.exit(4)
        if device_count > 1:
            printerror("Error:More devices on connected.")
            sys.exit(5)
        else:
            printsuccess("Devices connected success!!!")
    else:
        printerror("error for 'adb devices' commands.")
        sys.exit(6)

"""
get apk path in phone

Args:
package: package name
"""
def associated_package_apk(package):
    cmds = "adb shell dumpsys package " + package
    status, packageLines = commands.getstatusoutput(cmds)
    afile = None
    if status == 0 and packageLines != None:
        for line in packageLines.split('\n'):
            if "codePath=" in line and "data" not in line:
                afile = line[line.index('=') + 1:]
                break
    else:
        printerror("error for {}.".format(cmds))
        sys.exit(7)

    return afile

"""
set framework environment
"""
def set_framework_environment():
    framework = "framework"
    apktool_framework = "framework_apktool"

    if not os.path.exists(apktool_framework):
        print "Create '{}' file.".format(apktool_framework)
        os.mkdir(apktool_framework)

    if not os.path.exists(framework):
        print "Setting framework environment..."
        status, result = exe_command("adb pull /system/framework {}".format(framework))
        if status != 0:
            printerror("Error for pull framework...")
            sys.exit(8)

    if os.path.exists(apktool_framework):
        exe_command("apktool if -p {} {}/framework-res.apk".format(apktool_framework, framework))

    printsuccess("Set framework resources success!!!")
    return framework, apktool_framework

def decode_apk(apk, outdir, apktool_framework):
    print "decode apk '{}'".format(apk)
    cmd = "apktool d -p " + apktool_framework + " -o " + outdir + " " + apk
    status, result = exe_command(cmd)
    if status == 0:
        printsuccess("Decode apk file success!!!")
        return True
    else:
        printerror("Error:decode apk error!!!")
        sys.exit(9)

"""
add 'android:debuggable=true' to AndroidManifest.xml
"""
def modify_manifest(manifest):
    print "modify debuggable attribute in AndroidManifest.xml."
    xml = minidom.parse(manifest)
    root = xml.documentElement
    applications = root.getElementsByTagName('application')
    for application in applications:
        application.setAttribute('android:debuggable', "true")

    f=open(manifest,'w')
    f.write(xml.toprettyxml(encoding='utf-8'))
    f.close()
    printsuccess("Modify manifest file success!!!")

"""
build apk file
"""
def build_apk(apk, indir, apktool_framework):
    apk = apk.split('/')[-1]
    d_index = apk.index('.')
    debugapk = apk[:d_index] + "_debug" + apk[d_index:]
    print "build and generate apk '{}'".format(debugapk)
    cmd = "apktool b -p " + apktool_framework + " -o " + debugapk + " " + indir
    status, result = exe_command(cmd)
    if status == 0:
        printsuccess("Build apk file success!!!")
        return debugapk
    else:
        printerror("Error:build apk error!!!")
        sys.exit(10)

"""
sign apk file
"""
def apksigner(apk, apksigner, pk8, pem):
    print "sign apk '{}'".format(apk)
    command = "bash " + apksigner + " sign --key " + pk8 + " --cert " + pem + " " + apk
    status, result = exe_command(command)
    if status == 0:
        printsuccess("Sign apk file success!!!")
        return True
    else:
        printerror("Error:sign apk error!!!")
        sys.exit(11)

"""
generate debug apk for exist apk

Args:
apk: apk file
"""
def generate_debug_apk(options, apk, apkdex, apktool_framework):
    print "generate debug apk for \"{}\"".format(apk)

    tmp_apk = "apktmp"

    if os.path.exists(tmp_apk):
        print "delete exists '{}' file.".format(tmp_apk)
        shutil.rmtree(tmp_apk)

    decode_apk(apk, tmp_apk, apktool_framework)

    modify_manifest(os.path.abspath(tmp_apk + "/AndroidManifest.xml"))

    if apkdex != None:
        print "Move exist dex '{}'".format(apkdex)
        exe_command("mv {} {}".format(apkdex, tmp_apk))

    buildapk = build_apk(apk, tmp_apk, apktool_framework)

    apksigner(buildapk, options.apksigner, options.pk8, options.pem)

"""
generate classes.dex by odex file
"""
def generate_dex_by_odex(arm, apk_odex, framework):
    print "Generate arm={} dex by '{}'".format(arm, apk_odex)

    tmp_odex = "odextmp"
    if os.path.exists(tmp_odex):
        print "delete exists '{}' file.".format(tmp_odex)
        shutil.rmtree(tmp_odex)

    baksmali_cmds = "baksmali deodex " + apk_odex + " -b " + framework + "/arm/boot.oat -o " + tmp_odex
    if arm == "64":
        baksmali_cmds = "baksmali deodex " + apk_odex + " -b " + framework + "/arm64/boot.oat -o " + tmp_odex
    status, result = exe_command(baksmali_cmds)

    dex = "classes.dex"
    if os.path.exists(dex):
        print "delete exists '{}' file.".format(dex)
        shutil.rmtree(dex)
    if status == 0:
        printsuccess("baksmali {} success!!!".format(apk_odex))
        status, result = exe_command("smali assemble " + tmp_odex + " -o " + dex)
        if status == 0:
            printsuccess("smali {} success!!!".format(tmp_odex))
        else:
            printerror("smali {} fail.".format(tmp_odex))
    else:
        printerror("baksmali {} fail.".format(apk_odex))

    return dex

"""
generate debug apk for pacakge
"""
def generate_package_apk(options, package):
    framekwork, apktool_framework = set_framework_environment()

    print "generate for package \"{}\"".format(package)
    pakcage_apk = associated_package_apk(package)
    if pakcage_apk != None:
        apk_name = pakcage_apk.split('/')[-1]
        status, result = exe_command("adb pull " + pakcage_apk + " " + apk_name)

        apk_file = apk_name + "/" + apk_name + ".apk"
        apk_dex = None

        if options.aversion >= "23":
            apk_odex = None
            if options.arm == "32":
                apk_odex = apk_name + "/oat/arm/" + apk_name + ".odex"
            elif options.arm == "64":
                apk_odex = apk_name + "/oat/arm64/" + apk_name + ".odex"
            else:
                printerror("Can't find odex file for {}...".format(options.arm))
                sys.exit(11)
            if apk_odex != None:
                apk_dex = generate_dex_by_odex(options.arm, apk_odex, framekwork)
            else:
                printerror("Can't find odex file...")
                sys.exit(11)

        if status == 0:
            generate_debug_apk(options, apk_file, apk_dex, apktool_framework)
        else:
            printerror("Can't pull apk '{}'.".format(package))
    else:
        printerror("Can't find package \"{}\" in device.".format(package))

def generate_packages_apk(options, args):
    for package in args:
        if os.path.exists(package) and os.path.isfile(package) and zipfile.is_zipfile(package):
            framekwork, apktool_framework = set_framework_environment()
            generate_debug_apk(options, package, None, apktool_framework)
        else:
            generate_package_apk(options, package)

def main():
    options, args = parser_args()
    verify_args(options, args)
    verify_tools(options)
    check_devices()
    generate_packages_apk(options, args)

if __name__ == "__main__":
    try:
        main()
    except BaseException as err:
        if DEBUG == True:
            print err
