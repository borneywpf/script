#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Author:borney
# Date:2017-01-16

# slint.py <super lint>

"""
脚本用途:在终端使用android的lint工具时,结果展示很不友好,这个脚步就是为了方便展示和查看
缺点：目前是对目录进行全局检查，也没有设置配置选项等
使用方法:将slint.py copy到你的bin目录下,修改为可执行权限;slint.py <你想lint检查的目录>
"""

from subprocess import call, STDOUT
from tempfile import mkstemp
import sys, os, re

import traceback

_DEBUG = False
_DEBUG_DATA = False


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


def print_except_trace():
    """
    print except trace if debug

    :return:
    """
    if _DEBUG:
        traceback.print_exc()


def issues_list(fname):
    """
    Analysis issue list from file

    :param fname:
    :return:
    """
    try:
        is_first = True
        one_issue = []
        issues = []
        flint = open(fname)
        is_begin_parse = False  # 过滤文件头部无用的信息,是否开始解析
        while True:
            line = flint.readline()
            if not line:
                break

            # 最后一行匹配
            end_match = re.match('[0-9]*\serrors,\s[0-9]*\swarnings', line)
            is_tag_line = "Warning:" in line or "Error:" in line or end_match is not None

            if not is_begin_parse and is_tag_line:
                is_begin_parse = True

            if is_begin_parse:
                one_issue.append(line)

                if is_tag_line:
                    if is_first:
                        is_first = False
                    else:
                        one_issue.pop()
                        flint.seek(flint.tell() - len(line))
                        issues.append(one_issue)
                        one_issue = []
                        is_first = True
    except Exception, e:
        print e
    finally:
        flint.close()

    return issues


def issues_dict_list(issues):
    """
    Analysis issue list and store by dict to list

    :param issues:
    :return:
    """
    issues_d_l = []
    for i in range(len(issues)):
        issues_d = {'which': []}
        issue = issues[i]
        for j in range(len(issue)):
            if j == 0:
                if "Warning:" in issue[j] or "Error:" in issue[j]:
                    splits = issue[j].split(' ')
                    issues_d['file'] = splits[0].split(':')[0]
                    issues_d['line'] = splits[0].split(':')[1]
                    issues_d['issue'] = splits[1][0:len(splits[1]) - 1]
                    issues_d['summary'] = ' '.join(splits[2:len(splits) - 1])
                    category = splits[len(splits) - 1]
                    issues_d['category'] = category[1:len(category) - 2]
            else:
                issues_d['which'].append(issue[j])

        if len(issues_d) == 6:
            issues_d_l.append(issues_d)

    return issues_d_l


def print_issues_dict_list(issues_d_l, lint_id_dict):
    """
    print issues dict of list to screen

    :param lint_id_dict:
    :param issues_d_l:
    :return:
    """
    for d in issues_d_l:
        if d.get('issue') == "Warning":
            print '-' * 45, "[" + bcolors.WARNING + d.get('issue') + bcolors.ENDC + "]", '-' * 45
        elif d.get('issue') == "Error":
            print '-' * 45, "[" + bcolors.ERROR + d.get('issue') + bcolors.ENDC + "]", '-' * 45
        print '[%s][%s][%s](%s)' % (
            bcolors.OKBLUE + d.get('category') + bcolors.ENDC,
            bcolors.OKGREEN + d.get('file') + bcolors.ENDC,
            d.get('line'),
            lint_id_dict.get(d.get('category')))
        print d.get('summary')
        for s in d.get('which'):
            try:
                match_first = re.match('\s*~+', s).group(0)
                if d.get('issue') == 'Warning':
                    print bcolors.WARNING + match_first + bcolors.ENDC
                elif d.get('issue') == 'Error':
                    print bcolors.ERROR + match_first + bcolors.ENDC
                else:
                    print bcolors.OKBLUE + match_first + bcolors.ENDC
            except:
                print s,
    print '-' * 102


def lookup_by_category(issues_d_l, lint_id_dict):
    """
    lookup and display by issue category

    :param lint_id_dict:
    :param issues_d_l: issues dict list
    :return:
    """
    while True:
        clear_screen()
        categories = []
        try:
            '''
            lookup category list in issues dict list
            '''
            for d in issues_d_l:
                if d.get('category') not in categories:
                    categories.append(d.get('category'))
            print "检查结果中有如下问题类型:"

            for i in range(len(categories)):  # show category list
                print "%-2d %s (%s)" % (i + 1, categories[i], lint_id_dict.get(categories[i]))
            category_d_l = []
            index = int(raw_input('请输入要查看的问题类型:'))
            for d in issues_d_l:
                if d.get('category') == categories[index - 1]:
                    category_d_l.append(d)
            print bcolors.OKGREEN + '共有%d个[%s]' % (len(category_d_l), categories[index - 1]) + bcolors.ENDC
            print_issues_dict_list(category_d_l, lint_id_dict)
            co = raw_input('是否继续查看?(Y/N):')
            if co != 'Y' and co != 'y':
                break
        except:
            print_except_trace()
            break


def lookup_by_issue(issues_d_l, lint_id_dict):
    """
    lookup and display by issue

    :param lint_id_dict:
    :param issues_d_l: issues dict list
    :return:
    """
    while True:
        clear_screen()
        issues = []
        try:
            '''
            lookup issue list in issues dict list
            '''
            for d in issues_d_l:
                if d.get('issue') not in issues:
                    issues.append(d.get('issue'))
            print "检查结果中有如下分类:"

            for i in range(len(issues)):  # show issue list
                print "%-2d %s" % (i + 1, issues[i])
            issue_d_l = []
            index = int(raw_input('请输入要查看的分类:'))
            for d in issues_d_l:
                if d.get('issue') == issues[index - 1]:
                    issue_d_l.append(d)
            print bcolors.OKGREEN + '共有%d个[%s]' % (len(issue_d_l), issues[index - 1]) + bcolors.ENDC
            print_issues_dict_list(issue_d_l, lint_id_dict)
            co = raw_input('是否继续查看?(Y/N):')
            if co != 'Y' and co != 'y':
                break
        except:
            print_except_trace()
            break


def lookup_by_file_type(issues_d_l, lint_id_dict):
    """
        lookup and display by file type

        :param lint_id_dict:
        :param issues_d_l: issues dict list
        :return:
        """
    while True:
        clear_screen()
        file_types = []
        try:
            '''
            lookup file type list in issues dict list
            '''
            for d in issues_d_l:
                if d.get('file').endswith('AndroidManifest.xml') and 'AndroidManifest.xml' not in file_types:
                    file_types.append('AndroidManifest.xml')
                elif d.get('file').endswith('xml') and 'xml' not in file_types:
                    file_types.append('xml')
                elif d.get('file').endswith('java') and 'java' not in file_types:
                    file_types.append('java')
                elif 'other' not in file_types:
                    file_types.append('other')

            print "检查结果中有如下项目文件分类:"

            for i in range(len(file_types)):  # show issue list
                print "%-2d %s" % (i + 1, file_types[i])
            issue_file_type_d_l = []
            index = int(raw_input('请输入要查看的文件分类:'))
            for d in issues_d_l:
                file_type = file_types[index - 1]
                if d.get('file').endswith(file_type):
                    if file_type == 'AndroidManifest.xml':
                        issue_file_type_d_l.append(d)
                    elif file_type == 'xml':
                        if not d.get('file').endswith('AndroidManifest.xml'):
                            issue_file_type_d_l.append(d)
                    elif file_type == 'java':
                        issue_file_type_d_l.append(d)
                elif file_type == 'other':
                    if not d.get('file').endswith('AndroidManifest.xml') and not d.get('file').endswith(
                            'xml') and not d.get('file').endswith('java'):
                        issue_file_type_d_l.append(d)

            print_issues_dict_list(issue_file_type_d_l, lint_id_dict)
            co = raw_input('是否继续查看?(Y/N):')
            if co != 'Y' and co != 'y':
                break
        except:
            print_except_trace()
            break


def del_unused_resource(abs_dir, issues_d_l):
    """
    delete unused resource from your set dir

    :param abs_dir: lint work absolute path
    :param issues_d_l: issues dict list
    :return:
    """
    del_file_line_dict = {}  # 用于存储非文件类资源,但包括drawable图片
    del_file_count = 0
    del_value_count = 0
    for d in issues_d_l:
        if d.get('category') == 'UnusedResources':
            res_file = abs_dir + os.sep + d.get('file')
            is_unused_file = False
            for w in d.get('which'):  # 如果描述信息中包含'^'字符说明这个文件是多余的,需要删除
                if '^' in w:
                    is_unused_file = True
                    break
            if is_unused_file:
                print 'del file[%s]' % res_file
                del_file_count += 1
                os.remove(res_file)
            else:
                if res_file in del_file_line_dict.keys():
                    del_file_line_dict[res_file].append(int(d.get('line')))
                else:
                    try:
                        del_file_line_dict[res_file] = [int(d.get('line'))]
                    except:
                        del_file_line_dict[res_file] = list(d.get('line'))

    for (k, v) in del_file_line_dict.items():
        if len(v) == 0:  # 刪除多余的drawable图片
            print 'del file[%s]' % k
            del_file_count += 1
            os.remove(k)
        else:
            print "del file[{}] line {}".format(k, v)
            v.sort(reverse = True)
            with open(k) as res_read:
                res_read_lines = res_read.readlines()
                res_write_lines = []

                line_tag = ''  # 删除资源的tag
                is_end_line_tag = True  # 如果某个标签跨行需要进行标记删除

                for i in range(len(res_read_lines)):
                    line = i + 1
                    line_strip = res_read_lines[i].strip()

                    if line in v:
                        tag = line_strip.split()[0]
                        line_tag = tag[1:len(tag)]
                        if line_strip.endswith('/>') or line_strip.endswith('/' + line_tag + '>'):
                            is_end_line_tag = True
                        else:
                            is_end_line_tag = False
                        # print 'del file[%s][%d] values' % (k, line)
                        del_value_count += 1
                    else:
                        if is_end_line_tag:
                            res_write_lines.append(res_read_lines[i])

                        if line_strip.endswith('/>') or line_strip.endswith('/' + line_tag + '>'):
                            is_end_line_tag = True

                with open(k, 'w+') as res_write:
                    res_write.writelines(res_write_lines)

    del_total_count = del_file_count + del_value_count
    if del_total_count != 0:
        print bcolors.OKGREEN + '删除完成,总共删除%d个资源，其中文件资源%d个,值资源%d个.(回车继续)' % ( \
            del_total_count, del_file_count, del_value_count) + bcolors.ENDC
    else:
        print bcolors.OKGREEN + "没有可删除的资源啦！" + bcolors.ENDC
    return del_total_count


def clear_screen():
    """
    clear screen history which show

    :return:
    """
    os.system('clear')


def check_by_lint(is_first = True):
    """
    check dir for you set, return dir and issues dict for list

    :param is_first: is first check
    :return:
    """
    clear_screen()
    work_path_dir = os.path.abspath(sys.argv[1])
    if is_first:
        print "正在对目录[%s]进行lint检查,请等待片刻..." % work_path_dir
    else:
        print "数据发生变化,正在对[%s]重新检查,请等待片刻..." % work_path_dir

    temp = mkstemp(text = True)[1]  # make temp file, which store lint result

    # write lint check result to temp file
    with open(temp, 'w+') as tmp:
        call(["lint", work_path_dir], stderr = STDOUT, stdout = tmp)

    issues = issues_list(temp)
    issues_f_d_l = issues_dict_list(issues)

    if not _DEBUG_DATA:
        os.remove(temp)  # delete temp file
    else:
        from pprint import pprint
        pprint(issues)

    print bcolors.OKGREEN + "检查完成..." + bcolors.ENDC

    if len(issues_f_d_l) == 0:
        print '你代码写的太牛了,没有检查出一个错误和警告!!!'

    return work_path_dir, issues_f_d_l


def generate_lint_dict():
    """
    get lint Valid issue ids dict

    :return:
    """
    temp = mkstemp(text = True)[1]  # make temp file, which store lint result

    with open(temp, 'w+') as tmp:
        call(["lint", "--list"], stderr = STDOUT, stdout = tmp)

    # parse temp file and generate id list
    ids = []
    with open(temp) as tmp:
        lines = tmp.readlines()
        is_begin_ids = False  # 是否开始记录id
        for line in lines:
            if is_begin_ids:
                if line.startswith('\"'):
                    ids.append(line.strip())
                else:
                    ids[-1] += line.strip()
            if line.startswith("Valid issue id\'s:"):
                is_begin_ids = True
    os.remove(temp)

    # parse id list and generate id dict
    ids_dict = {}
    for id_l in ids:
        sp = id_l.split(':')
        ids_dict[sp[0][1:len(sp[0]) - 1]] = sp[1].strip()
    return ids_dict


def s_help():
    print bcolors.HEADER + \
          "脚本用途:在终端使用android的lint工具时,结果展示很不友好,这个脚步就是为了方便展示和查看" \
          "\n使用方法:将slint.py copy到你的bin目录下,修改为可执行权限" \
          "\nslint.py <lint检查的目录>" \
          + bcolors.ENDC


def error_and_warning_count(issues_d_l):
    """
    return error count and warning count and other count from issues dict list

    :param issues_d_l: issues dict list
    :return:
    """
    error_count = 0
    warning_count = 0
    other_count = 0
    for d in issues_d_l:
        if d.get('issue') == 'Warning':
            warning_count += 1
        elif d.get('issue') == 'Error':
            error_count += 1
        else:
            other_count += 1

    return error_count, warning_count


def main():
    """
    main method

    :return:
    """
    if len(sys.argv) <= 1:
        s_help()
        return
    if not os.path.isdir(sys.argv[1]):
        print 'ERROR:输入的参数不是目录...'
        return

    lint_dict = generate_lint_dict()
    work_path, issues_d_l = check_by_lint()  # lint check

    if _DEBUG_DATA:
        return

    while True:
        ew_count = error_and_warning_count(issues_d_l)
        print "*" * 15 + bcolors.BOLD + bcolors.OKGREEN + "[Super Lint]" + bcolors.ENDC + bcolors.ENDC + "*" * 15
        print "检查到错误:" + bcolors.ERROR + "%d" % ew_count[0] + bcolors.ENDC + \
              "个，警告:" + bcolors.WARNING + "%d" % ew_count[1] + bcolors.ENDC + "个"
        print '-' * 42
        print '1 根据问题类型查询(like UnusedResources)'
        print '2 根据分类查询(Warning or Error)'
        print '3 根据项目文件类型查询(java,xml... etc)'
        print '4 查看所有(all)'
        print '5 删除没有使用的资源'
        print '-' * 42
        print bcolors.BOLD + bcolors.OKGREEN + 'r' + bcolors.ENDC + bcolors.ENDC + ' 重新检查(recheck)'
        print bcolors.BOLD + bcolors.OKGREEN + 'q' + bcolors.ENDC + bcolors.ENDC + ' 退出'
        print '*' * 42
        try:
            choice = raw_input('请输入操作类型编号(如 q 退出):')
            if choice == 'q':  # quit
                break;
            elif choice == 'r':
                work_path, issues_d_l = check_by_lint()
            elif choice == '1':  # show by issue category
                lookup_by_category(issues_d_l, lint_dict)
            elif choice == '2':  # show by issue
                lookup_by_issue(issues_d_l, lint_dict)
            elif choice == '3':
                lookup_by_file_type(issues_d_l, lint_dict)
            elif choice == '4':  # show all
                print_issues_dict_list(issues_d_l, lint_dict)
                raw_input("按任意键继续...")
            elif choice == '5':
                del_unused_resource(work_path, issues_d_l)
                raw_input()
                work_path, issues_d_l = check_by_lint(False)  # recheck when delete unused resource
        except Exception:
            print_except_trace()  # print error trace
            break
        else:
            clear_screen()


if __name__ == '__main__':
    try:
        main()
    except:
        print_except_trace()
        print '程序中断...'
