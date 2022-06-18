## Android内存相关

1、dump_meminfo.py

每隔1s读取目标包名的meminfo，并输出到命令行和文件，用于分析和统计一段时间内目标进程的内存占用情况

2、dump_smaps.py

分析原理可见我的博客[Android meminfo 分析](https://dddjjq.github.io/2022/06/15/Android%E5%86%85%E5%AD%98%E5%88%86%E6%9E%90-Code.html)。

主要是读取/proc/{pid}/smaps文件，然后从中读取中Code部分占用的内存分布情况。

