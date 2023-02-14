[toc]

# 第二章 KVM原理介绍

## 硬件虚拟化技术

- VT-x技术
- VT-d技术
- VT-c技术

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

### I/O虚拟化

## KVM 架构概述

## KVM 内核模块

## QEMU/KVM组件

- **vhost-net**
- **Open vSwitch**
- **DPDK**
- **SPDK**
- **Ceph**
- **libguestfs**

## KVM上层管理工具

- **libvirt**
- **virsh**
- **virt-manager**
- **OpenStack**

