[toc]

# 第三章 构建KVM环境

## 硬件系统的配置

- BIOS打开VT功能

  1. BIOS中的Advanced选项
  2. BIOS中Enabled的VT和VT-d选项

- 检查CPU特性

  > 在linux系统中，可以通过检查/proc/cpuinfo文件中的cpu特性标志(flags)来查看CPU目前是否支持硬件虚拟化。

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

5. make olddefconfig：和上面make silentoldconfig一样，但不需要手动交互，而是对新选项以其默认值配置。

6. make xconfig：基于X Window的一种配置方式，提供了漂亮的配置窗口，不过只能在X Server上运行X桌面应用程序时使用。它依赖于QT，如果系统中没有安装QT库，则会出现“Unable to find any QT installation”的错误提示。

7. make gconfig：与make xconfig类似，不同的是make gconfig依赖于GTK库。

8. make defconfig：按照内核代码中提供的默认配置文件对内核进行配置（在Intel x86-64平台上，默认配置为arch/x86/configs/x86_64_defconfig），生成.config文件可以用作初始化配置，然后再使用make menuconfig进行定制化配置。

9. make allyesconfig：尽可能多地使用“y”输入设置内核选项值，生成的配置中包含了全部的内核特性。

10. make allnoconfig：除必需的选项外，其他选项一律不选（常用于嵌入式Linux系统的编译）。

11. make allmodconfig：尽可能多地使用“m”输入设置内核选项值来生成配置文件。

12. make localmodconfig：会执行 lsmod 命令查看当前系统中加载了哪些模块（Modules），并最终将原来的.config 中不需要的模块去掉，仅保留前面 lsmod 命令查出来的那些模块，从而简化了内核的配置过程。这样做确实方便了很多，但是也有个缺点：该方法仅能使编译出的内核支持当前内核已经加载的模块。因为该方法使用的是 lsmod 查询得到的结果，如果有的模块当前没有被加载，那么就不会编到新的内核中。

    

13. make clean：删除大多数的编译生成文件， 但是会保留内核的配置文件.config， 还有足够的编译支持来建立扩展模块

14. make mrproper：删除所有的编译生成文件， 还有内核配置文件， 再加上各种备份文件

15. make distclean：mrproper删除的文件， 加上编辑备份文件和一些补丁文件。

### 编译 KVM

1. 编译 kernel

   ```shell
   make vmlinux -j $(nproc)
   ```

   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/vmlinux compile.png)

   > **错误：**
   >
   > 1. 证书问题
   >
   >    - 错误表现
   >
   >      ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/2023-2-13-19-18.png)
   >
   >    - 查看MakeFile文件
   >
   >      ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/2023-2-13-19-22.png)
   >
   >      ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/2023-2-13-19-25.png)
   >
   >      > 由于KVM编译的时间比较长，没有查看过编译过程，只是在结尾部分查看编译结果，一直在Error 2上查找问题，困扰了好几天，由于证书找不到，但是错误结果在build in这里的原因是，在证书这里无法完成构建，在1992行整体构建的时候就会出错。
   >
   >    - 解决办法
   >
   >      ```makefile
   >      CONFIG_SYSTEM_TRUSTED_KEYS=""
   >      CONFIG_SYSTEM_REVOCATION_KEYS=""
   >      ```
   >
   >      > 以上两个字段把`"debian/canonical-crets.pem"`这个去掉，留空即可编译

2. 编译bzImage

   ```shell
   make bzImage
   ```

   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/2023-02-13 19-55-33.png)

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

1. 创建镜像文件

   ```shell
   qemu-img create -f raw linux_lite6.img 40G
   ```

   > 使用create命令创建一个空白的客户机镜像，raw格式，文件名为`linux_lite6.img`，大小是40G，但是并不占用磁盘空间，按照后期实际需求分配文件的实际大小。

   ```shell
   qemu-img create -f raw -o preallocation=full linux_lite6.img 40G
   ```

   > 通过设置-o参数可以让文件一开始就实际占有40G（建立的过程比较耗时，还会占用更大的空间。所以qemu-img默认的方式是按需分配的）

   > 除raw格式以外，qemu-img还支持创建其他格式的image文件，比如qcow2，甚至是其他虚拟机用到的文件格式，比如VMware的vmdk、vdi、vhd等。不同的文件格式会有不同的“-o”选项。

2. 启动客户机

   ```shell
   qemu-system-x86_64 -enabke-kvm -m 8G -smp 4 -boot once=d -cdrom linux-lite-6.2-64bit.iso linux_lite6.img
   ```

   > - -m 8G：客户机分配8G内存
   > - -smp 4：指定客户机为对称多处理器结构并分配4个CPU
   > - -boot once=d：是指定系统的启动顺序为首次光驱，以后再使用默认启动项（硬盘），
   > - -cdrom ** ：是分配客户机的光驱

## 启动第一个KVM客户机

```shell
qemu-system-x86_64 -m 8G -smp 4 /root/linux_lite6.img
```







