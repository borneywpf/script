#!/usr/bin/env python

# -*- coding:utf-8 -*-

# Author:borney
# Date:2017-06-6

import os
import sys
import re
import xml.etree.ElementTree as ET

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[31m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
    
def print_compont(com):
    print "=" * 99
    print "%-14s: %s" % ("Type", com["tag"])
    print "%-14s: %s" % ("Name", com["name"])
        
    if com["exported"] != None:
        print "%-14s: %s" % ("Exported", com["exported"])
        
    if com["illegal"] == True:
        print (bcolors.ERROR + "%-14s: %s" + bcolors.ENDC) % ("Illegal", com["illegal"])
    else:
        print (bcolors.OKGREEN + "%-14s: %s" + bcolors.ENDC) % ("Illegal", com["illegal"])
        
    if com["permission"] != None:
        print "%-14s: %s" % ("Permission", com["permission"])
        
    if com["target_activity"] != None:
        print "%-14s: %s" % ("targetActivity", com["target_activity"])
        
    filters = com["filter"]
    if len(filters):
        print "%-14s:" % ("Filters")
        for f in filters:
            print "%-14s: %s" % ("", "-" * 83)
            if len(f["action"]):
                print "%-14s: %-14s: %s" % ("", "action", f["action"])
            if len(f["category"]):
                print "%-14s: %-14s: %s" % ("", "category", f["category"])
            if len(f["data"]):
                print "%-14s: %-14s: %s" % ("", "data", f["data"])

def print_componts(componts, tags):
    for com in componts:
        if len(tags) and com["tag"] not in tags:
            continue
        print_compont(com)
        

def verify_args():
    if len(sys.argv) < 2:
        sys.exit(1)

    manifest_file = os.path.abspath(sys.argv[1])
    
    tags = []
    if len(sys.argv) is 3:
        tags.extend(sys.argv[2].split(','))

    if os.path.exists(manifest_file) and os.path.isfile(manifest_file) and manifest_file.endswith(
            'AndroidManifest.xml'):
        print "%-14s> %s" % ("Manifest", manifest_file)
    else:
        sys.exit(1)
    
    print "%-14s> %s" % ("Types", tags)

    return manifest_file, tags

def main():
    manifest, tags = verify_args()
    
    tree = ET.ElementTree(file=manifest)
    
    print_componts(componts(tree, package_name(tree)), tags)

if __name__ == '__main__':
    main()
