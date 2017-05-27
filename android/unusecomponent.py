#!/usr/bin/env python
# coding= utf-8
import os
import sys
import commands


# 脚本用途：用于检查在manifest中注册了没有实现的android组件
# 使用方法：第一个参数指定manifest文件，第二个参数指定code目录

def package_name(manifest_content):
    manifest_tag = False
    original_tag = False
    for l in manifest_content:
        trim = l.strip()

        if trim.startswith("<manifest"):
            manifest_tag = True

        if manifest_tag and "package" in l:
            r_package_name = l.split("\"")[1]

        if trim.startswith("<original-package"):
            original_tag = True

        if original_tag and "android:name" in l:
            r_package_name = l.split("\"")[1]
    return r_package_name


def full_components(manifest_content):
    r_components = []
    is_tag = False
    for l in manifest_content:
        trim = l.strip()
        if trim.startswith("<activity") \
                or trim.startswith("<service") \
                or trim.startswith("<provider") \
                or trim.startswith("<receiver"):
            is_tag = True

        if is_tag and "android:name" in l:
            r_components.append(l.split("\"")[1])

        if trim.endswith(">") or trim.endswith("/>"):
            is_tag = False
    return r_components


def components(c_package_name, full_component):
    self_components = []
    for com in full_component:
        if com.startswith(c_package_name) or com.startswith("."):
            self_components.append(com.split(".")[-1])
    return self_components


def un_use_components(self_components, code):
    r_un_use_component = []
    for com in self_components:
        status, result = commands.getstatusoutput("find " + code + " -name *" + com + "*")
        if not result and status == 0:
            r_un_use_component.append(com)
    return r_un_use_component


def verify_args():
    if len(sys.argv) < 3:
        sys.exit(1)

    manifest_file = os.path.abspath(sys.argv[1])
    code_dir = os.path.abspath(sys.argv[2])

    if os.path.exists(manifest_file) and os.path.isfile(manifest_file) and manifest_file.endswith(
            'AndroidManifest.xml'):
        print manifest_file
    else:
        sys.exit(1)

    if os.path.exists(code_dir) and os.path.isdir(code_dir):
        print code_dir
    else:
        sys.exit(1)
    return manifest_file, code_dir


def main():
    manifest, code = verify_args()
    with open(manifest) as f:
        content = f.readlines()
    self_components = components(package_name(content), full_components(content))
    un_use_component = un_use_components(self_components, code)
    if len(un_use_component):
        print "查找到非法注册的组件:{}".format(un_use_component)
        sys.exit(1)
    else:
        print "恭喜你，没有找到非法注册的组件!!!"
        sys.exit(0)


if __name__ == '__main__':
    main()
