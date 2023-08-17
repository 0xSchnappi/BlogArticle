[toc]

# 第五章 KVM 核心基础功能——CPU配置

## vCPU 概念

> 在`KVM`环境中，每个客户机都是一个标准的`Linux`进程(`QEMU`进程)，而每一个`vCPU`在宿主机中是`QEMU`进程派生的一个普通线程。
>
> 在普通的`Linux`系统中，进程一般有两种执行模式：内核模式和用户模式。而在`KVM`环境中，增加了第三章模式：客户模式
>
> 1. 用户模式（User Mode）
>
>    > 主要处理`I/O`的模拟和管理，由`QEMU`的代码实现。
>
> 2. 内核模式（Kernel Mode）
>
>    > 主要处理特别需要高性能和安全相关的指令，如处理客户机模式到内核模式的转换，处理客户模式下的`I/O`指令或其他特权指令引起的退出（`VM-Exit`），处理影子内存管理（`Shadow MMU`）。
>
> 3. 客户模式（Guest Mode）
>
>    > 主要执行Guest中的大部分指令，`I/O`和一些特权指令除外（它们会引起`VM-Exit`，被`Hypervisor`截获并模拟）
>
> `kvm`的内核部分是作为可动态加载内核模拟运行在宿主机中的，其中一个模块是与硬件平台无关的实现虚拟化核心基础架构的`KVM`模块，另一个是硬件平台相关的`kvm_intel`(或`kvm_amd`)模块 

## `SMP` 支持

> `SMP(Symmetric Multi-Processor, 对称多处理器)`系统使用多处理器、多核、超线程等技术中一个或多个。

```shell
#!/bin/bash
#this script only works in a Linux system which has one or more identical physical CPU(s).

echo -n "logical CPU number in total: "
# 逻辑CPU个数
# wc命令可以统计字节、行数等. -l 统计行数 
cat /proc/cpuinfo | grep "processor" | wc -l

# 有些系统没有多核也没有打开超线程，就直接退出脚本
# grep 匹配查找内容 -i：忽略大小写进行匹配。-q 或 --quiet或--silent : 不显示任何信息。
cat /proc/cpuinfo | grep -qi "core id"
# $? 最后运行的命令的结束代码（返回值）
# -ne 不等于
if [ $? -ne 0 ]; then
        echo "Warning.No Multi-core or hyper-threading is enabled."
        exit 0;
fi

echo -n "physical CPU number in total: "
# 物理CPU个数
# sort 可针对文本文件的内容，以行为单位来排序
# uniq 可检查文本文件中重复出现的行列
cat /proc/cpuinfo | grep "physical id" | sort | uniq | wc -l


echo -n "core number in a physical CPU: "
# 每个物理CPU上core的个数（未计入超线程）
core_per_phy_cpu=$(cat /proc/cpuinfo | grep "core id" | sort | uniq | wc -l)
echo $core_per_phy_cpu

echo -n "logical CPU number in a physical CPU: "
# 每个物理CPU中逻辑CPU（可能是core、threads或both）的个数
# awk -F: '{print $2}' 打印输出第二个参数
# 比如："siblings        : 12" 就会打印 "12"
logical_cpu_per_phy_cpu=$(cat /proc/cpuinfo | grep "siblings" | sort | uniq | awk -F: '{print $2}')
echo $logical_cpu_per_phy_cpu

# 是否打开超线程，以及每个core上的超线程数目
# 如果在同一个物理CPU上的两个逻辑CPU具有相同的"core id"，那么超线程是打开的
# 此处根据前面计算的core_per_phy_cpu和logical_core_per_phy_cpu的比较来查看超线程
# -gt 大于
# -eq 等于

if [ $logical_cpu_per_phy_cpu -gt $core_per_phy_cpu ]; then
        echo "Hyper threading is enabled. Each core has $(expr $logical_cpu_per_phy_cpu / $core_per_phy_cpu) threads."
elif [ $logical_cpu_per_phy_cpu -eq $core_per_phy_cpu ]; then
        echo "Hyper threading is NOT enabled."
else
        echo "Error. There's something wrong."
fi

```

> 客户机实现`SMP`的两种方式：
>
> 1. 将不同的`vCPU`的进程交换执行（分时调度，即使物理硬件非`SMP`，也可以为客户机模拟出`SMP`系统环境）
> 2. 将在物理`SMP`硬件系统上同时执行多个`vCPU`的进程

- `qemu`命令行，`-smp`参数

  > `-smp`参数即是配置客户机的`SMP`系统
  >
  > ```shell
  > -smp [cpus=]n[,maxcpus=cpus][,cores=cores][,threads=threads][,sockets=sockets]
  > ```
  >
  > - `n` 用于设置客户机中使用的逻辑CPU数量（默认值是1）
  > - `maxcpus` 用于设置客户机中最大可能被使用的CPU数量，包括启动时处于下线（`offline`）状态的CPU数量（可用于热拔插`hot-plug`加入CPU,但不能超过`maxcpus`这个上限）
  > - `cores`用于设置每个CPU的`core`数量（默认值是1）
  > - `threads`用于设置每个`core`上的线程数（默认值是1）
  > - `sockets`用于设置客户机中看到的总的CPU `socket`数量

## CPU 过载使用

`KVM`允许客户机过载使用（`over-commit`）物理资源，即允许为客户机分配的CPU和内存数量多于物理上实际存在的资源。

`CPU`的过载使用是让一个或多个客户机使用`vCPU`的总数量超过实际拥有的物理`CPU`数量。

**关于`CPU`的过载使用，推荐的做法是对多个单`CPU`的客户机使用`over-commit`，**比如，在拥有4个逻辑`CPU`的宿主机中，同时运行多于4个（如8个、16个）客户机，其中每个客户机都分配一个`vCPU`。这时，如果每个宿主机的负载不是很大，宿主机`Linux`对每个客户机的调度是非常有效的，这样的过载使用并不会带来客户机的性能损失。

**关于`CPU`的过载使用，最不推荐的做法是让某一个客户机的`vCPU`数量超过物理系统上存在的`CPU`数量。**比如，在拥有4个逻辑`CPU`的宿主机中，同时运行一个或多个客户机，其中每个客户机的`vCPU`的数量多于4个（如16个）。这样的使用方法会带来比较明显的性能下降，其性能反而不如为客户机分配2个（或4个）`vCPU`的情况。而且客户机的负载过重，可能会让整个系统运行不稳定。不过，在并非100%满负载的情况下，一个（或多个）有4个`vCPU`的客户机运行在拥有4个逻辑`CPU`的宿主机中并不会带来明显的性能损失。

## CPU 模型

虚拟机管理程序（`Virtual Machine Monitor`，简称`VMM`或`Hypervisor`）

`QEMU/KVM`在默认情况下会向客户机提供一个名为`qemu64`和`qemu32`的基本`CPU`模型。

`QEMU/KVM`的这种策略会带来一些好处，如可以对`CPU`特性提供一些高级的过滤功能，还可以将物理平台根据提供的基本`CPU`模型进行分组（如将几台`IvyBridge`和`Sandybridge`硬件平台分为一组，都提供相互兼容的`SandBridge`或`qemu64`的`CPU`模型），从而使客户机在同一组硬件平台上的动态迁移更加平滑和安全。

在`qemu`命令行中，可以用`“-cpu cpu_model”`来指定在客户机中的`CPU`模型。

## 进程的处理器亲和性和vCPU的绑定

**进程的处理器亲和性（`Processor Affinity`）**即`CPU`的绑定设置，是指将进程绑定到特定的一个或多个`CPU`上去执行，而不允许将进程调度到其他的`CPU`上。`Linux`内核对进程的调度算法也是遵守进程的处理器亲和性设置的。设置进程的处理器亲和性带来的好处是可以减少进程在多个`CPU`之间交换运行带来的缓存命中失效（`cache missing`），从该进程运行的角度来看，可能带来一定程度上的性能提升。换个角度来看，对进程亲和性的设置也可能带来一定的问题，如破坏了原有`SMP`系统中各个`CPU`的负载均衡（`load balance`），这可能会导致整个系统的进程调度变得低效。特别是在使用多处理器、多核、多线程技术的情况下，在`NUMA`结构的系统中，如果不能对系统的`CPU`、内存等有深入的了解，对进程的处理器亲和性进行设置可能导致系统的整体性能的下降而非提升。

每个`vCPU`都是宿主机中一个普通的`QEMU`线程，可以使用`taskset`工具对其设置处理器亲和性，使其绑定到某一个或几个固定的`CPU`上去调度。尽管`Linux`内核进程调度算法已经非常高效了，在多数情况下不需要对进程的调度进行干预，不过，在虚拟化环境中有时有必要将客户机的`QEMU`进程或线程绑定到固定的逻辑`CPU`上。

**案例：**作为`IaaS（Infrastructure as a Service）`类型的云计算提供商的`A`公司（如Amazon、Google、Azure、阿里云等），为客户提供一个有两个逻辑`CPU`计算能力的一个客户机。要求`CPU`资源独立被占用，不受宿主机中其他客户机的负载水平影响。为了满足这个需求可以分为如下两个步骤来实现。

1. 启动宿主机时隔离出两个逻辑`CPU`专门供一个客户机使用。在`	Linux`内核启动的命令行中加上`“isolcpus=”`参数

   - 查看`Linux`内核启动命令行

     ```shell
     $ cat /proc/cmdline                                   
     BOOT_IMAGE=/boot/vmlinuz-6.1.0-rc8 root=UUID=0cf1e58d-e735-4e34-941e-db07585956cd ro quiet splash vt.handoff=7 isolcpus=4,5
     ```

   - 查看5号逻辑`CPU`上运行的线程信息（也包括进程在内）

     ```shell
     ps -eLo ruser,pid,ppid,lwp,psr,args | awk '{if($5==5) print $0}'
     ```

     线程：

     > - `migration`线程：用于进程在不同的`CPU`间迁移
     > - `kworker`线程：用于处理`workqueues`
     > - `ksoftirqd`线程：用于调度`CPU`软中断的进程
     > - `watchdog`线程
     >
     > 这些线程都是内核对各个`CPU`的守护进程。

     命令解析：

     > - `ps`命令显示当前系统的进程信息的状态
     > - `-e`参数用于显示所有的进程
     > - `-L`参数用于将线程（`light-weight process, LWP`）也显示出来
     > - `-o`参数表示以用户自定义的格式输出
     >   - `psr`表示当前分配给进行运行的处理器编号
     >   - `lwp`表示线程的ID
     >   - `ruser`表示运行进程的用户
     >   - `pid`表示进程的ID
     >   - `ppid`表示父进程的ID
     >   - `args`表示运行的命令及其参数

2. 启动一个拥有两个`vCPU`的客户机，并将其`vCPU`绑定到宿主机中两个CPU上。

   > 1. 绑定代表整个客户机的`QEMU`进程，使其运行在`cpu4`上
   > 2. 绑定第一个`vCPU`的线程，使其运行在`cpu4`上
   > 3. 绑定第二个`vCPU`的线程，使其运行在`cpu5`上
   >
   > 对于`taskset`命令，此处使用的语法是：`taskset -pc cpulist pid`。

