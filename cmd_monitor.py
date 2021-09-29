#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import time
import argparse
import subprocess

DEFAULT_MONITOR_DIR = ""  # 监控目录
DEFAULT_CMD_FILE_EXT = "bat"  # 执行命令后缀
DEFAULT_RESULT_EXT = "result"  # 结果后缀
DEFAULT_RESULT_CWD = "C:\\Windows\\System32"
DEFAULT_LOG_FILE = "srv_rdp.log"



def logger_config(log_path, logging_name):
    '''
    配置log
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :return:
    '''
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='utf-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger


logger = logger_config(os.path.join(DEFAULT_MONITOR_DIR, DEFAULT_LOG_FILE), DEFAULT_LOG_FILE)


class SrvRDP:
    def __init__(self):
        self.args = self.get_config()
        self.check()

    def get_config(self):
        """get_config 获取客制配置

        Returns:
            [dict]: 客制配置
        """
        parser = argparse.ArgumentParser("Sangfor RDP Scan Client")
        parser.add_argument("-m", "--monitor_dir", default=DEFAULT_MONITOR_DIR, help="监控文件目录")
        parser.add_argument("-c", "--cwd", default=DEFAULT_RESULT_CWD, help="执行目录")
        parser.add_argument("-i", "--input_ext", default=DEFAULT_CMD_FILE_EXT, help="输入脚本文件扩展")
        parser.add_argument("-o", "--output_ext", default=DEFAULT_RESULT_EXT, help="输出结果文件扩展")
        return parser.parse_args()

    def _get_files_by_ext(self, ext):
        """
        获取所有cmd执行文件内容
        :param ext: 寻找对应扩展文件
        :return:
        """
        files = list()
        for path, dir_list, file_list in os.walk(self.args.monitor_dir):
            for file_name in file_list:
                if file_name.split(".")[-1] == ext:
                    files.append(os.path.join(path, file_name))
        return files

    def get_cmd_result(self, cmd, cwd=None, retry=1, timeout=20):
        """
        命令执行：既可以判断执行是否成功，还可以获取执行结果
        :param cmd:命令
        :param cwd:命令工作目录
        :param retry:失败重试次数
        :param timeout:超时秒
        :return: 执行结果结构体 {"flag":True,"content":""}
        """
        result = dict()
        result["flag"] = False  # 执行成功标志位
        result["content"] = ""  # 执行内容
        for i in range(retry):
            p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE)  # 执行shell语句并定义输出格式
            while p.poll() is None:  # 判断进程是否结束（Popen.poll()用于检查子进程（命令）是否已经执行结束，没结束返回None，结束后返回状态码）
                if p.wait(
                        timeout=timeout) is not 0:  # 判断是否执行成功（Popen.wait()等待子进程结束，并返回状态码；如果20秒之后进程还没有结束，将会抛出一个TimeoutExpired异）
                    result["flag"] = False
                else:
                    re = p.stdout.readlines()  # 获取原始执行结果
                    content = []
                    for i in range(len(re)):  # 由于原始结果需要转换编码，所以循环转为utf8编码并且去除\n换行
                        res = re[i].decode('utf-8').strip('\r\n')
                        content = (res)
                    result["flag"] = True
                    result["content"] = "".join(content)
            if result["flag"]:  # 执行成功直接返回
                break
        return result

    def rm_file(self, file):
        if os.path.exists(file):
            os.remove(file)

    def save_result(self, file, cmds, result):
        basename = os.path.dirname(file)
        tmp_pre_name = os.path.basename(file).split(".")[0]
        flag = "true" if result["flag"] else "false"
        result_file = f"{tmp_pre_name}_{flag}.{self.args.output_ext}"
        with open(os.path.join(basename, result_file), "w", encoding="utf-8") as f:
            f.write(result["content"])
        log_cmd = "\n".join(cmds) + "\n只显示最后一条命令回显结果"
        logger.info(f"执行基线 {tmp_pre_name}\n{log_cmd}\n{result['content']}")  # 日志中打印基线内容

    def monitor(self):
        while os.path.exists(os.path.abspath(self.args.monitor_dir)):
            cmd_files = self._get_files_by_ext(self.args.input_ext)
            for file in cmd_files:
                cmds = [x for x in open(file, "r", encoding="gbk").read().split("\n") if len(x) > 0]
                self.rm_file(file)
                for cmd in cmds:  # 不过执行多少命令(有可能是交互式命令)、总是获取最后一条执行结果
                    result = self.get_cmd_result(cmd)
                self.save_result(file, cmds, result)
            time.sleep(1)  # 间隔一秒检查一次
        logger.info("执行完成")

    def check(self):
        if not os.path.exists(self.args.monitor_dir):
            logger.error(f"the dir({self.args.monitor_dir}) is not exists")
            exit()


if __name__ == '__main__':
    client = SrvRDP()
    client.monitor()
    # 打包 pyinstaller -F -c -i mirror.ico srv_rdp.py (图标+本脚本)
