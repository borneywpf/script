#!/usr/bin/env bash

if [ $# -eq 2 ]; then
	src_str=$1
	tar_str=$2
	echo "将\"$src_str\"替换成\"$tar_str\""
	grep -rl "$src_str" ./ | grep -v svn |xargs sed -i 's/'$src_str'/'$tar_str'/g'
else
	echo "用法: $0 被替换字符串 替换字符串"
	echo "例如 $0 abc bcd"
fi
