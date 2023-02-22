[toc]

# 第二章 KVM原理介绍

## 硬件虚拟化技术

### CPU虚拟化

- Intel在处理器级别提供了对虚拟化技术的支持，被称为VMX(virtual-macine extensions)。有两种VMX操作模式：VMX根模式（root operation）与VMX非根模式（non-root operation）。作为虚拟机监控器中的KVM就是运行在跟操作模式下，而虚拟机客户机的整个软件栈（包括操作系统和应用程序）则运行在非根操作模式下。进入VMX非根操作模式“VM Entry”；从非根操作模式退出，被称为“VM Exit”。

- 在客户机中执行的一些特殊的敏感指令或者一些异常会触发“VM Exit”退到虚拟机的监控器中，从而运行在VMX根模式。正是这样的限制，让虚拟机监控器保持了对处理器资源的控制。

- 逻辑处理器在根模式和非根模式之间的切换通过一个叫VMCS（Virtual Machine Control Data Structure）的数据结构控制。使用VMPTRST和VMPTRLD指令对VMCS指针进行读写，使用VMREAD、VMWRITE和VMCLEAR等指令对VMCS实现配置。

- 部分在非根模式下会导致“VM Exit”的敏感指令

  > 1. 一定会导致VM Exit的指令：CPUID、GETSEC、INVD、XSETBV等，以及VMX模式引入的INVEPT、INVVPID、VMCALL、VMCLEAR、VMLANUCH、VMPTRLD、VMPTRST、VMRESUME、VMXOFF、VMXON等。
  > 2. 在一定的设置条件下会导致VM Exit的指令：CLTS、HLT、IN、OUT、INVLPG、INVPCID、LGDT、LMSW、MONITOR、MOV from CR3、MOV to CR3、MWAIT、RDMSR、RWMSR、VMREAD、VMWRITE、RDRAND、RDTSC、XSAVES、XRSTORS等。如在处理器的虚拟机执行控制寄存器中的“HLT exiting”比特位被置为1时，HLT的执行就会导致VM Exit。
  > 3. 可能会导致VM Exit的事件：一些异常、三次故障（Triple fault）、外部中断、不可屏蔽中断（NMI）、INIT信号、系统管理中断（SMI）等。如在虚拟机执行控制寄存器中的“NMI exiting”比特位被置为1时，不可屏蔽中断就会导致VM Exit。
  >
  > - **提示：**由于发生一次VM Exit的代价比较高（可能会消耗成百上千个CPU执行周期，而平时很多指令是几个CPU执行周期就能完成），所以对于VM Exit的分析是虚拟化中性能分析和调优的一个关键点。

### 内存虚拟化

#### 地址

1. 客户机虚拟地址，GVA（Guest Virtual Address）
2. 客户机物理地址，GPA（Guest Physical Address）
3. 宿主机虚拟地址，HVA（Host Virtual Address）
4. 宿主机物理地址，HGA（Host Physical Address）

#### 前期

虚拟机监控器需要维护从客户机虚拟地址到宿主机物理地址之间的一个映射关系，在没有硬件提供内存虚拟化之前，这个维护映射关系的页表叫作影子页表（Shadow Page Table）

#### 现在

Intel CPU 在硬件设计上就引入了EPT（Extended Page Tables，扩展页表），从而将客户机虚拟地址到宿主机物理地址的转换通过硬件来实现。

- 通过客户机CR3寄存器将客户机虚拟地址转化为客户物理地址

- 通过查询EPT来实现客户机物理地址到宿主物理地址的转化

  > EPT的控制权在虚拟机监控器中，只有当CPU工作在非根模式时才参与内存地址的转换。
  >
  > 使用EPT后，客户机在读写CR3和执行INVLPG指令时不会导致VM Exit，而且客户页表结构自身导致的页故障也不会导致VM Exit。

#### 特性

Intel 在内存虚拟化效率方面还引入了VPID（Virtual-processor identifier）特性，在硬件级别对TLB资源管理进行了优化。

- **问题**

  > 在没有VPID之前，不同客户机的逻辑CPU在切换执行时需要刷新TLB，而TLB的刷新会让内存访问的效率下降。

- **解决方案**

  > VPID技术通过在硬件上为TLB增加一个标志，可以识别不同的虚拟化处理器的地址空间，所以系统可以区分虚拟机监控器和不同虚拟机上不同处理器的TLB，在逻辑CPU切换执行时就不会刷新TLB，而只需要使用对应的TLB即可
  >
  > VPID的值在3种情况下为0，第1种是在非虚拟化环境中执行时，第2种是在根模式下执行时，第3种是在非根模式下执行但“enable VPID”控制位被置0时。

### I/O虚拟化

通常4种`I/O`虚拟化方式：

1. 设备模拟：在虚拟机监控器中模拟一个传统的I/O设备的特性，比如QEMU中模拟一个Intel的千兆网卡或者一个IDE硬盘驱动器，在客户机中就暴露为对应的硬件设备。客户机的I/O请求都由虚拟机监控器捕获并模拟执行返回给客户机。
2. 前后端驱动接口：在虚拟机监控器与客户机之间定义一种全新的适合于虚拟化环境的交互接口，比如常见的virtio协议就是在客户机中暴露为virtio-net、virtio-blk等网络和磁盘设备，在QEMU中实现相应的virtio后端驱动。
3. 设备直接分配：将一个物理设备，如一个网卡或硬盘驱动器直接分配给客户机使用，这种情况下I/O请求的链路中很少需要或基本不需要虚拟机监控器的参与，所以性能很好。
4. 设备共享分配：是设备直接分配方式的一种扩展。一个（具有特定特性的）物理设备可以支持多个虚拟机的功能接口，可以将虚拟功能接口独立的分配给不同的客户机使用。如SR-IOV就是这种方式的一个标准协议。

> - 尽管VT-d特性支持的设备直接分配方式性能可以接近物理设备在非虚拟化环境中的性能极限，但是它有一个缺点：单个设备只能分配给一个客户机，而在虚拟化环境下一个宿主机上往往运行着多个客户机，很难保证每个客户机都能得到一个直接分配的设备。
> - 实现了SR-IOV规范的设备，有一个功能完整的PCI-e设备成为物理功能（Physical Function，PF）。在使能了SR-IOV之后，PF就会派生出若干个虚拟功能（Virtual Function，VF）。VF看起来依然是一个PCI-e设备，它拥有最小化的资源配置，有用独立的资源，可以作为独立的设备直接分配给客户机。
> - SR-IOV特性可以看作VT-d的一个特殊例子，所以SR-IOV除了设备本身要支持该特性，同时也需要硬件平台打开VT-d特性支持。

## KVM 架构概述

KVM就是在硬件辅助虚拟化技术之上构建起来的虚拟机监控器。（KVM对硬件的最低依赖是CPU的硬件虚拟化支持）

KVM虚拟化的核心主要由以下两个模块组成：

1. KVM内核模块，它属于标准Linux内核的一部分，是一个专门提供虚拟化功能的模块，主要负责CPU和内存虚拟化，包括：客户机的创建、虚拟内存的分配、CPU执行模式的切换、vCPU寄存器的访问、vCPU的执行。
2. QEMU用户态工具，它是一个普通的Linux进程，为客户机提供设备模拟的功能，包括模拟BIOS、PCI/PCIE总线、磁盘、网卡、声卡、显卡、键盘、鼠标等。同时它通过ioctl系统调用与内核态的KVM模块进行交互。

## KVM 内核模块

- KVM模块是KVM虚拟化的核心模块，它在内核中由两部分组成：一个是处理器架构无关的部分，用lsmod命令中可以看到，叫作kvm模块；另一个是处理器架构相关的部分，在Intel平台上就是kvm_intel这个内核模块。KVM的主要功能是初始化CPU硬件，打开虚拟化模式，然后将虚拟客户机运行在虚拟机模式下，并对虚拟客户机的运行提供一定的支持。
- `/dev/kvm`这个设备可以被当作一个标准的字符设备，KVM模块与用户空间QEMU的通信接口主要是一系列针对这个特殊设备文件的loctl调用。
- 处理器对设备的访问主要是通过I/O指令和MMIO，其中I/O指令会被处理器直接截获，MMIO会通过配置内存虚拟化来捕捉。但是，外设的模拟一般不由KVM模块负责。一般来说，只有对性能要求比较高的虚拟设备才会由KVM内核模块来直接负责，比如虚拟中断控制器和虚拟时钟。

## QEMU/KVM组件

- **vhost-net**（网络）

  > vhost-net是Linux内核中的一个模块，它用于替代QEMU中的virtio-net用户态的网络的后端实现。使用vhost-net时，还支持网卡的多队列，整体来说会让网络性能得到较大的提高。

- **Open vSwitch**（虚拟交换机）

  > Open vSwitch是一个高质量的、多层虚拟交换机，使用开源Apache2.0许可协议，主要用可移植性强的C语言编写。它的目的是让大规模网络自动化可以通过编程扩展，同时仍然支持标准的管理接口和协议（例如NetFlow、sFlow、SPAN、RSPAN、CLI、LACP、802.lag）。同时也提供了对OpenFlow协议的支持，用户可以使用任何支持OpenFlow协议的控制器对OVS进行远程管理控制。Open vSwitch被设计为支持跨越多个物理服务器的分布式环境，类似于VMware的vNetwork分布式vswitch或Cisco Nexus 1000 V。Open vSwitch支持多种虚拟化技术，包括Xen/XenServer、KVM和VirtualBox。在KVM虚拟机中，要实现软件定义网络（SDN），那么Open vSwitch是一个非常好的开源选择。

- **DPDK**（网络）

  > DPDK全称是Data Plane Development Kit，Intel公司为Intel x86处理器架构下用户空间高效的数据包处理提供库函数和驱动支持开源项目，它还支持POWER和ARM架构。他专注于网络应用中数据包的高性能处理。具体体现在DPDK应用程序是运行在用户空间上，利用自身提供的数据平面库来收发数据包，绕过了Linux内核协议栈对数据包处理过程。其优点是：性能高、用户态开发、出故障易恢复。在KVM架构中，为了达到非常高的网络处理能力（特别是小包处理能力），可以选择DPDK与QEMU中的vhost-user结合起来使用。

- **SPDK**（存储）

  > SPDK全称是Storage Performance Development Kit，它可为编写高性能、可扩展的、用户模式的存储程序提供一系列工具及开发库。其主要特点是：将驱动放到用户态从而实现零拷贝、用轮询模式替代传统的中断模式、在所有的I/O链路上实现无锁设计，这些设计会使其性能比较高。在KVM中需要非常高的存储I/O性能时，可以将QEMU与SPDK结合使用。

- **Ceph**（分布式存储系统）

  > Ceph是Linux上一个著名的分布式存储系统，能够在维护POSIX兼容性的同时加入复制和容错功能。Ceph由储存管理器（Object storage cluster，对象存储集群，即OSD守护进程）、集群监视器（Ceph Monitor）和元数据服务器（Metadata server cluster，MDS）构成。其中，元数据服务器MDS仅仅在客户端通过文件系统方式使用Ceph时才需要。当客户端通过块设备或对象存储使用Ceph时，可以没有MDS。Ceph支持3种调用接口：对象存储，块存储，文件系统挂载。在libvirt和QEMU中都有Ceph的接口，所以Ceph与KVM虚拟化集成是非常容易的。在OpenStack的云平台解决方案中，Ceph是一个非常常用的存储后端。

- **libguestfs**（镜像磁盘管理）

  > libguestfs是用于访问和修改虚拟机的磁盘镜像的一组集合。libguestfs提供了访问和编辑客户机中的文件、脚本化修改客户机中的信息、监控磁盘使用和空闲的统计信息、P2V、V2V、创建客户机、克隆客户机、备份磁盘内容、格式化磁盘、调整磁盘大小等非常丰富的功能。libguestfs不需要启动KVM客户机就可以对磁盘镜像进行管理，功能强大的且非常灵活，是管理KVM磁盘镜像的首选工具。

## KVM上层管理工具

- **libvirt**

  > libvirt是使用最广泛的对KVM虚拟化进行管理的工具和应用程序接口，已经是事实上的虚拟化接口标准。作为通用的虚拟化API，libvirt不但能管理KVM，还能管理VMware、Hyper-V、Xen、VirtualBox等其他虚拟化方案。

- **virsh**

  > virsh是一个常用的管理KVM虚拟化的命令行工具，对于系统管理员在单个宿主机上进行运维操作，virsh命令行可能是最佳选择。virsh是用C语言编写的一个使用libvirt API的虚拟化管理工具，其源代码也是在libvirt这个开源项目中的。

- **virt-manager**

  > virt-manager是专门针对虚拟机的图形化管理软件，底层与虚拟化交互的部分仍然是调用libvirt API来操作的。virt-manager除了提供虚拟机生命周期（包括：创建、启动、停止、打快照、动态迁移等）管理的基本功能，还提供性能和资源使用率的监控，同时内置了VNC和SPICE客户端，方便图形化连接到虚拟客户机中。virt-manager在RHEL、CentOS、Fedora等操作系统上非常流行的虚拟化管理软件，在管理的机器数量规模较小时，virt-manager是很好的选择。因其图形化操作的易用性，成为新手入门学习虚拟化操作的首选管理软件。

- **OpenStack**

  > OpenStack是一个开源的基础架构服务（IaaS）云计算管理平台，可用于构建公有云和私有云服务的基础设施。OpenStack是目前业界使用最广泛的功能强大最强大的云管理平台，它不仅提供了管理虚拟机的丰富功能，还有非常多其他重要管理功能，如：对象存储、块存储、网络、镜像、身份验证、编排服务、控制面板等。OpenStack仍然使用libvirt API来完成对底层虚拟化的管理。

