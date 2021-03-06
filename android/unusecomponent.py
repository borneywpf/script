#!/usr/bin/env python
# coding= utf-8
import os
import sys
import commands
from pprint import pprint  
import xml.etree.ElementTree as ET


# 脚本用途：用于检查在manifest中注册了没有实现的android组件
# 使用方法：第一个参数指定manifest文件，第二个参数指定code目录


def attrib_value(attrib_dict, attrib):
    for (k,v) in attrib_dict.items():
        if k.endswith(attrib):
            return v

def package_name(tree):
    r_package_name = []
    for elem in tree.iter(tag = 'manifest'):
        r_package_name.append(elem.attrib['package'])
    for elem in tree.iter(tag = 'original-package'):
        r_package_name.append(attrib_value(elem.attrib, "name"))
    r_package_name.append('.')
    
    return r_package_name

def in_package(package_name, name):
    for package in package_name:
       if name.startswith(package):
           return True

def parser_component(component, package_name):
    exported = attrib_value(component.attrib, "exported")
    filters = component.findall('intent-filter')
    tag = component.tag
    name = attrib_value(component.attrib, "name")
    target_activity = attrib_value(component.attrib, "targetActivity")
    permission = attrib_value(component.attrib, "permission")
    
    if len(filters) != 0 or exported == 'true':
        filter_list = []
                
        for intent_filter in filters:
            filter_dict = {}
            actions = []
            categorys = []
            datas = []
            
            for action in intent_filter.findall('action'):
                actions.append(attrib_value(action, "name"))
            filter_dict['action'] = actions

            for category in intent_filter.findall('category'):
                categorys.append(attrib_value(category, "name"))
            filter_dict['category'] = categorys
                    
            for data in intent_filter.findall('data'):
                datas.append(attrib_value(data, "name"))
            filter_dict['data'] = datas
                    
            filter_list.append(filter_dict)
        
        illegal = False
        if len(filters) != 0 and exported == 'false':
            illegal = True
        
        return {"tag":tag, "name":name, "exported":exported, "permission":permission, "filter":filter_list, "illegal":illegal, "target_activity":target_activity}
    else:
        return None

def componts(tree, package_name):
    root = tree.getroot()
    r_componts = []
    for application in root.findall('application'):
        for activity in application.findall('activity'):
            component = parser_component(activity, package_name)
            if component:
                r_componts.append(component)
        
        for activity_alias in application.findall('activity-alias'):
            component = parser_component(activity_alias, package_name)
            if component:
                r_componts.append(component)
        
        for service in application.findall('service'):
            component = parser_component(service, package_name)
            if component:
                r_componts.append(component)
                
        for provider in application.findall('provider'):
            component = parser_component(provider, package_name)
            if component:
                r_componts.append(component)
                
        for receiver in application.findall('receiver'):
            component = parser_component(receiver, package_name)
            if component:
                r_componts.append(component)

    return r_componts

def check_component(code, component):
    name = component.split('.')[-1]
    return commands.getstatusoutput("find " + code + " -name *" + name + ".*")

def unuse_activity_alias(self_components, code, package_name, target_activity):
    is_exist_target = False
    for com in self_components:
        if in_package(package_name, com["name"]):
            if com["tag"] != "activity-alias":
                if com["name"] == target_activity:
                    status, result = check_component(code, target_activity)                    
                    if result and status == 0:
                        is_exist_target = True
                else: 
                    continue
    return is_exist_target

def unuse_components(self_components, code, package_name):
    r_un_use_component = []
    for com in self_components:
        if in_package(package_name, com["name"]):
            if com["tag"] == "activity-alias":
                if com["target_activity"] != None:
                    if not unuse_activity_alias(self_components, code, package_name, com["target_activity"]):
                        r_un_use_component.append(com)
                else:
                    r_un_use_component.append(com)
            else:
                status, result = check_component(code, com["name"])

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
    
    tree = ET.ElementTree(file=manifest)
    
    package = package_name(tree)
    
    unuse_component = unuse_components(componts(tree, package), code, package)
    
    if len(unuse_component):
        print "查找到非法注册的组件:"
        pprint(unuse_component)
        sys.exit(1)
    else:
        print "恭喜你，没有找到非法注册的组件!!!"
        sys.exit(0)

if __name__ == '__main__':
    main()
