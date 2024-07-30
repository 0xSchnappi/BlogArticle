# tmux 笔记

## tmux 用途

使用一般终端启动后台运行程序，命令为`./myprogram &`，这种会造成你想查看程序输出的时候就没有办法了。
tmux就是你在退出终端的时候，程序还可以继续运行，你想查看tmux的运行情况，进入到终端就可以查看。

## tmux 安装

```shell

sudo apt install tmux

```

## 基本使用实例

```shell

# 创建并进入终端名称为test
tmux new -s test

tmux split-window -h        # 划分左右两个窗格快捷键为`Ctrl+b %`

# 运行myprogram1程序
./myprogram1

# 输入快捷键`Ctrl+b ;`，光标接换到上一个窗格

./myprogram1 &

# 退出tmux 输入快捷键`Ctrl+b d`

# 查看tmux已经创建和运行的终端
tmux ls

# 从linux终端进入tmux创建的名为test的终端
tmux a -t test 或者 tmux attach -t test

# 进入当前tmux
tmux a

# 关闭并停止运行tmux创建的名为test的终端
tmux kill-session -t test

```