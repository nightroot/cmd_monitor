# cmd_monitor
Windows下监控bat执行脚本


## 打包
```bash
pip install pyinstaller
pyinstaller -F -c -i mirror.ico cmd_monitor.py (图标+本脚本)
pyinstaller -F -c cmd_monitor.py
```

## help
```bash
usage: Sangfor RDP Scan Client [-h] [-m MONITOR_DIR] [-c CWD] [-i INPUT_EXT] [-o OUTPUT_EXT]

optional arguments:
  -h, --help            show this help message and exit
  -m MONITOR_DIR, --monitor_dir MONITOR_DIR
                        监控文件目录
  -c CWD, --cwd CWD     执行目录
  -i INPUT_EXT, --input_ext INPUT_EXT
                        输入脚本文件扩展
  -o OUTPUT_EXT, --output_ext OUTPUT_EXT
                        输出结果文件扩展
```

## 说明
> 在监控目录下复制进去bat脚本（在执行之后会被删除）、会自动执行并生成结果回显文件

## 运行
```
./cmd_monitor.exe -m c:\path
```

