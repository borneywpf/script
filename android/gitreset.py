#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git Returns to the specified historical version
使用方法:将脚步copy到自己的bin目录下,修改文件执行去权限
       如果不带数字参数,则表示默认恢复到上个版本
       如果带数字参数,表示要浏览多少个历史版本(如gitreset.py 5,表示看5个历史版本)
"""

import os, sys
from subprocess import call, STDOUT
from tempfile import mkstemp
from types import FileType


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


_git_log_size = 3  # default show history version size


def readlines(file):
    """
    :param file:the file which need to read
    :return:
    """
    r = []
    isstartcommit = False
    if isinstance(file, FileType):
        while True:
            line = file.readline()
            r.append(line.strip())
            if line.startswith('commit'):
                if not isstartcommit:
                    isstartcommit = True  # 第一次出现commit
                else:
                    r.pop()  # 第二次出现commit 从列表中移除最后一行
                    file.seek(file.tell() - len(line))  # 第二次出现commit 将文件指针后移
                    break
    return r


def writelogtotemp(tmpfile):
    """
    Writes git log to a temporary file

    :param tmpfile:The name of the temporary file
    :return:
    """
    with open(tmpfile, 'w') as tmp:
        call(["git", "log"], stderr = STDOUT, stdout = tmp)


def infolist(tmpfile):
    """
    Parses git log from the temporary file and returns a list of messages

    :param tmpfile:The name of the temporary file
    :return:
    """
    global _git_log_size
    des = []
    with open(tmpfile, 'r') as tmp:
        for i in range(_git_log_size):

            lines = readlines(tmp)
            commit = {}
            for line in lines:
                if line.startswith('commit '):
                    commit['id'] = i
                    commit['commit'] = line.split()[1]
                elif line.startswith('Author:'):
                    commit['author'] = ' '.join(line.split()[1:])
                elif line.startswith('Date:'):
                    commit['date'] = ' '.join(line.split()[1:])
                elif line.startswith('Change-Id:'):
                    commit['changeId'] = line.split()[1]
                elif line.startswith('Merge:'):
                    commit['merge'] = line.split()[1]
                elif line:
                    commit['des'] = line
            des.append(commit)
    return des


def printinfotable(infos):
    """
    print history versions to screen

    :param infos: which history versions to print
    :return:
    """

    print '历史版本记录:'
    print '-' * 55
    for info in infos:
        print 'Id       : ', bcolors.WARNING + str(info['id']) + bcolors.ENDC
        print 'Commit   : ', info.get('commit')
        print 'Author   : ', info.get('author')
        print 'Date     : ', info.get('date')
        print 'Change-Id: ', info.get('changeId')
        print 'Des      : ', bcolors.OKGREEN + info.get('des') + bcolors.ENDC

        print '-' * 55


def gitresetversion(infos, show_log_size):
    """
    Reverts to the specified historical version

    :param infos: history versions
    :param show_log_size:是否有显示log size 参数
    :return:
    """
    if show_log_size:
        try:
            id = int(raw_input('请输入你要恢复代码的Id:'))
            if 0 <= id < len(infos):
                for info in infos:
                    if info['id'] == id:
                        os.system('git reset ' + info.get('commit') + ' --soft')
                        os.system('git reset HEAD')
            else:
                print "超出范围的id..."
        except ValueError:
            print "v_v 输入了错误的id"
    else:
        print "恢复到最新的版本..."
        os.system('git reset ' + infos[1].get('commit') + ' --soft')
        os.system('git reset HEAD')


def main():
    show_log_size = False
    if len(sys.argv) > 1:
        global _git_log_size
        try:
            _git_log_size = int(sys.argv[1])
        except:
            pass
        show_log_size = True

    if call(["git", "branch"], stderr = STDOUT, stdout = open(os.devnull, 'w')) != 0:
        print("Error:没有在git工作目录....")
    else:
        print("Yup!")

    temp = mkstemp(text = True)[1]  # 创建临时数据文件

    writelogtotemp(temp)
    infos = infolist(temp)
    if show_log_size:
        printinfotable(infos)
    os.remove(temp)
    gitresetversion(infos, show_log_size)


if __name__ == "__main__":
    main()
