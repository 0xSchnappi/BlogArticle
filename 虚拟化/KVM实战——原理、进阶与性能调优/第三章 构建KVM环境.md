[toc]

# 第三章 构建KVM环境

## 硬件系统的配置

- BIOS打开VT功能
- 检查CPU特性

## 编译和安装KVM

### 下载 KVM 源代码‘

1. 下载kvm.git

   ```shell
   git://git.kernel.org/pub/scm/virt/kvm/kvm.git
   https://git.kernel.org/pub/scm/virt/kvm/kvm.git
   https://kernel.googlesource.com/pub/scm/virt/kvm/kvm.git
   ```

   

2. 下载linux.git

   ```shell
   git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
   https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
   https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux.git
   ```

   

3. 下载Linux的Tarball

   ```shell
   ftp://ftp.kernel.org/pub/linux/kernel
   http://www.kernel.org/pub/linux/kernel
   ```

   

4. 通过kernel.org的镜像站点下载

   ```shell
   https://mirror.tuna.tsinghua.edu.cn/kernel/
   https://mirror.bjtu.edu.cn/kernel/linux/kernel/
   http://mirrors.163.com/
   https://mirrors.sohu.com/
   ```

   

### 配置KVM

在kvm.git（Linux kernel）代码目录下，运行“make help”命令可以得到一些关于如何配置和编译kernel的帮助手册。

```shell
```

1. make config：这种方式会为每一个内核支持的特性向用户提问，如果用户回答

   - “y”，把特性编译进内核
   - “m”，把特性作为模板进行编译
   - “n”，不对该特性提供支持
   - “?”，显示该选项的帮助信息

2. make oldconfig：make oldconfig和make config类似，但是他的作用是在现有的内核设置文件基础上建立一个新的设置文件，只会向用户提供有关新内核特性的问题。在新内核升级的过程中，make oldconfig非常有用。

3. make silentoldconfig：和上面的make oldconfig一样，但不需要手动交互，而是对新选项以其默认值配置。

4. make menuconfig：基于终端的一种配置方式，提供了文本模式的图形用户界面，用户可以通过移动光标来浏览所支持的各种特性。

   - 上下键：选择不同的行，即移动到不同的（每一行的）选项上

   - 空格键：用于在 选择该选项，取消选择该选项，之间来回切换

     - 选择该（行所在的）选项：则对应的该选项前面就变成了，中括号里面一个星号，即 **[ \* ]**，表示被选中了。
   
     - 如果是取消该选项，就变成了，只有一个中括号，里面是空的，即：[  ]
   
   - 左右键：用于在Select/Exit/Help之前切换
   
   - 回车键：左右键切换到了某个键上，此时回车键，就执行相应的动作：
   
   - - Select：此时一般都是所在（的行的）选项，后面有三个短横线加上一个右箭头，即 —>，表示此项下面还有子选项，即进入子菜单
   
     - Exit：直接退出当前的配置
   
       - 所以，当你更改了一些配置，但是又没有去保存，此时一般都会询问你是否要保存当前（已修改后的最新的）配置，然后再退出。
   
     - Help：针对你当前所在某个（行的）选项，查看其帮助信息。
   
       - 一般来说，其帮助信息，都包含针对该选项的很详细的解释
       - 换句话说：如果你对某个选项的功能，不是很清楚，那么就应该认真仔细的去看看其Help，往往都会找到详细解释，以便你更加了解此配置的含义
     
     - 另外一般也会写出，此选项所对应的宏
         - 该宏，就是写出到配置文件中的那个宏
         - 对于写makefile的人来说，往往也是利用此相关的宏，在makefile中，实现对应的不同的控制

### 编译 KVM

1. 编译 kernel

   ```shell
   make vmlinux -j $(nproc)
   ```

   

2. 编译bzImage

   ```shell
   make bzImage
   ```

   

3. 编译module

   ```shell
   make moules -j $(nproc)
   ```

### 安装 KVM

1. 安装 module

   ```shell
   sudo make modules_install
   ```

   > 将编译好的module安装到相应的目录中，默认情况下module被安装到/lib/modules/$kernel_version/kernel目录中

2. 安装 kernel 和 initramfs

   ```shell
   make install
   ```

   > 在/boot目录下生成了内核(vmlinux)和initramfs等内核启动所需的文件。
   >
   > 在运行`make install`之后，在grub配置文件(如：/boot/grub2/grub.cfg)中也自动添加一个gurb选项
   >
   > - 重启系统
   >
   > - 手动modprobe命令加载kvm和kvm_intel
   >
   >   ```shell
   >   modprobe kvm
   >   modprobe kvm_intel
   >   lsmod | grep kvm
   >   ```
   >
   > - 检查/dev/kvm文件
   >
   >   ```shell
   >   ls -l /dev/kvm
   >   ```
   >
   >   > 它是kvm内核模块提供给用户空间的QEMU程序使用的一个控制接口，它提供了客户机（Guest）操作系统运行所需的模拟和实际的硬件设备环境。

## 编译和安装 QEMU

### 下载 QEMU 源代码

- 代码仓库

  ```shell
  git://git.qemu.org/qemu.git
  https://gitlab.com/qemu-project/qemu
  ```

  

- 最近几个发布版压缩包

  ```shell
  https://www.qemu.org/download/
  ```

### 配置、编译QEMU和安装QEMU

- 配置QEMU

  ```shell
  ./configure --target-list=x86_64-softmmu
  ```

  > - 通常情况下，直接运行代码仓库中configure文件进行配置即可
  > - 我们只使用x86架构的客户机，因此指定“--target-list=x86_64-softmmu”，可以节省大量的编译时间。
  > - 配置完成后。qemu/build目录下会生成config-host.mak和config.status
  >
  > 1. **config-host.mak**:可以查看通过上述configure之后的结果，它会在后续make中被引用
  > 2. **config.status**:后续要重新configure时，只要执行“./config.status”就可以恢复上一次configure的配置

- 编译QEMU

  ```shell
  make
  ```

- 安装QEMU

  ```shell
  make install
  ```

  > - 创建QEMU的一些目录。复制一些配置文件到相应的目录下，复制一些firmware文件(如：sgabios.bin、kvmvapic.bin)到目录下，以便qemu命令行启动时可以找到对应的固件供客户机使用。
  > - 复制keymaps到相应的目录下，以便在客户机中支持各种所需键盘类型。
  > - 复制qemu-system-x86_64、qemu-img等可执行程序到对应的目录下。

## 安装客户机





