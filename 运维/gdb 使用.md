# GDB使用

## How to debug programs with "sudo" in VSCODE

1. create a script called "gdb" in e.g. my home directory, containing: `pkexec /usr/bin/gdb "$@"`
   
   > polkit是一个授权管理器，其系统架构由授权和[身份验证](https://cloud.tencent.com/product/mfas?from=10680)代理组成，pkexec是其中polkit的其中一个工具，他的作用有点类似于sudo，允许用户以另一个用户身份执行命令
   > 
   > 所以也可以是`sudo /usr/bin/gdb "$@"`

2. make it executable

3. modify the launch.json in VSCode to call the script (obviously change *username* accordingly) by adding "miDebuggerPath":

```erlang
...
            "externalConsole": false,
            "miDebuggerPath": "/home/<username>/gdb",
            "MIMode": "gdb",
...
```

4. whilst debugging, use `top` or such like to verify the process is running as root.
