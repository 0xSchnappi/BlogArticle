[toc]

# 第五章 KVM 核心基础功能——内存配置

# 内存配置

> 内存作用是暂时存放`CPU`中将要执行的指令和数据，所有程序都必须先载入内存中才能够执行。内存的大小及其访问速度也直接影响整个系统的性能，所以在虚拟机系统中，对内存的虚拟化处理和配置也是比较关键的。

## 内存设置基本参数

通过`qemu`命令行启动客户机是设置内存大小的参数如下：

```shell
-m megs 	# 设置客户机的内存为megs MB大小
```

默认的单位为`MB`，也支持加上`"M"`或`"G"`作为后缀来显式指定使用`MB`或`GB`作为内存分配的单位。如果不设置`-m`参数，`QEMU`对客户机分配的内存大小默认为`128MB`

内存查看命令

```shell
dmesg
cat /proc/meminfo
```

## `EPT`和`VPID`简介

`EPT（Extended Page Tables,扩展页表）`，属于`Intel`的第二代硬件虚拟化技术，它是针对内存管理单元（`MMU`）的虚拟化扩展。`EPT`降低了内存虚拟化的难度（与影子页表相比），也提升了内存虚拟化的性能。

在虚拟化环境下，内存使用就需要两层的地址转换，即客户机应用程序可见的客户机虚拟地址（`Guest Virtual Address, GVA`）到客户机物理地址（`Guest Physical Address, GPA`）的转换，再从客户机物理内存地址（`GPA`）到宿主机物理地址（`Host Physical Address, HPA`）的转换。其中 ，前一个转换由客户机 操作系统来完成，而后一个转换由`Hypervisor`来负责。

**影子页表（`Shadow Page Tables`）**：从软件上维护了从客户机虚拟地址（`GVA`）到宿主机物理地址（`HPA`）之间的映射，每一份客户机操作系统的页表也对应一份影子页表。有了影子页表，在普通的内存访问时都可实现从`GVA`到`HPA`的直接转换，从而避免了上面提到的两次地址转换。`Hypervisor`将影子页表载入物理上的内存管理单元（`Memory Management Unit, MMU`）中进行地址翻译

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/%E5%BD%B1%E5%AD%90%E9%A1%B5%E8%A1%A8.png)

经管影子页表提供了在物理`MMU`硬件中能使用的页表，但是其缺点也是比较明显的。首先影子页表的实现非常复杂，导致其开发、调试和维护都比较困难。其次，影子页表的内存开销也比较大，因为需要为每个客户机进程对应的页表都维护一个影子页表。

**为了解决影子页表存在的问题，**`Intel`的`CPU`提供了`EPT`技术（`AMD`提供的类似技术叫作`NPT`，即`Nested Page Tables`），直接在硬件上支持`GVA-->GPA-->HPA`的两次地址转换，从而降低内存虚拟化实现的复杂度，也进一步提升了内存虚拟化的性能。

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/EPT%E5%9F%BA%E6%9C%AC%E5%8E%9F%E7%90%86.png)

`CR3`（控制寄存器3）将客户机程序所见的客户机虚拟地址（`GVA`）转换为客户机物理地址（`GPA`），然后再通过`EPT`将客户机物理地址（`GPA`）转换为宿主机物理地址（`HPA`）。这两次地址转换都是由`CPU`硬件来完成的，其转换效率非常高。在使用有`EPT`的情况下，客户机内部`Page Fault`、`INVLPG`（使用`TLB`项目失效）指令、`CR3`寄存器的访问等都不会引起`VM-Exit`，因此大大减少了`VM-Exit`的数量，从而提高了性能。

`EPT`只需要维护一张`EPT`页表，而不需要像“影子页表”那样为每个客户机进程的页表维护一张影子页表，从而也减少了内存的开销。

`VPID（Virtual Processor Identifiers, 虚拟处理器标识）`是在硬件上对`TLB`资源管理的优化，通过在硬件上为每个`TLB`项增加一个标识，用于不同的虚拟处理器的地址空间，从而能够区分`Hypervisor`和不同处理器的`TLB`。硬件区分了不同的`TLB`项分别属于不同虚拟处理器，因此可以避免每次进行`VM-Entry`和`VM-Exit`时都让`TLB`全部失效，提高了`VM`切换的效率。由于有了这些在`VM`切换后仍然继续存在的`TLB`项，硬件减少了一些不必要的页表访问，减少了内存访问次数，从而提高了`Hypervisor`和客户机的运行速度。`VPID`也会对客户机的实时迁移（`Live Migration`）有很好的效率提升，会节省实时迁移的开销，提升实时迁移的速度，降低迁移的延迟（`Latency`）。

- 查看`CPU`是否支持`EPT`和`VPID`

  ```shell
  $ grep -E "ept|vpid" /proc/cpuinfo
  fpu_exception	: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid mpx rdseed adx smap clflushopt intel_pt xsaveopt xsavec xgetbv1 xsaves dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp md_clear flush_l1d arch_capabilities
  vmx flags	: vnmi preemption_timer invvpid ept_x_only ept_ad ept_1gb flexpriority tsc_offset vtpr mtf vapic ept vpid unrestricted_guest ple pml ept_mode_based_exec
  
  ```

  

- 查看`kvm_intel` 加载时是否默认开启`EPT`和`VPID`

  ```shell
  # schnappi @ ASUS in ~/Desktop [9:01:37] 
  $ cat /sys/module/kvm_intel/parameters/ept
  Y
  
  # schnappi @ ASUS in ~/Desktop [9:03:44] 
  $ cat /sys/module/kvm_intel/parameters/vpid 
  Y
  
  ```

  > 根据`sysfs`文件系统中`kvm_intel`模块的当前参数值来确定`kvm`是否打开`EPT`和`VPID`特性。
  >
  > `sysfs`是一个虚拟的文件系统，它存在于内存之中，它将`Linux`系统中设备和驱动的信息从内核导出到用户空间。`sysfs`也用于配置当前系统，此时其作用类似于`sysctl`命令，`sysfs`通常是挂载在`/sys`目录上的，通过`mount`命令可以查看`sysfs`的挂载情况。

- 加载`kvm_intel`模块时，可以通过设置`ept`和`vpid`参数值来打开或者关闭`EPT`和`VPID`

  ```shell
  modprobe kvm_intel ept=0,vpid=0
  rmmod kvm_intel
  modprobe kvm_intel ept=1,vpid=1
  ```

## 内存过载使用

在`KVM`中内存也是允许过载使用（`over-commit`）的，`KVM`能够让分配给客户机的内存总数大于实际可用的物理内存数。由于客户机操作系统及其上的应用程序并非一直100%地利用其分配到的内存，并且宿主机上的多个客户机一般也不会同时达到100%的内存使用率，所以内存过载分配是可行的。一般通过一下三种方式实现内存过载使用。

1. **内存交换（swapping）：**用交换空间（`swap space`）来弥补内存的不足。
2. **气球（ballooning）：**通过`virio balloon`驱动来实现宿主机`Hypervisor`和客户机之间的协作。
3. **页共享（`page sharing`）：**通过`KSM（Kernel Samepage Merging）`合并多个客户机进程使用的相同内存页。

> 第一种内存交换的方式是最成熟的（`Linux`中很早就开始应用），相比`KSM`和`ballooning`的方式效率较低一些。

用`swapping`方式来让内存过载使用，要求有足够的交换空间（`swap space`）来满足所有的客户机进程和宿主机中其他进程所需的内存。可用物理内存空间和交换空间的大小之和应该等于或大于配置给所有客户机的内存总和，否则，在各个客户机内存使用同时达到较高比率时，可能会有客户机（因内存不足）被强制关机。

**案例：**某个服务器有32GB的物理内存，想在其上运行64个内存配置为1GB的客户机。在宿主机中，大约需要4GB大小的内存来满足系统进程、驱动、磁盘缓存及其他应用程序所需内存（不包括客户机进程所需内存）。计算过程如下：

> 客户机所需交换分区为：64*1GB + 4GB - 32GB = 36GB
>
> 根据`Redhat`的建议，对于32GB物理内存的`RHEL`系统，推荐使用至少4GB的交换分区。
>
> 因此，在宿主机中总共需要建立至少40GB（36GB+4GB）的交换分区，来满足安全实现客户机内存的过载使用。
