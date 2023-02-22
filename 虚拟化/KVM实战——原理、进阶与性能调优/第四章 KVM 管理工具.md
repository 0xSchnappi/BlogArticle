[toc]

# 第四章 KVM 管理工具

## libvirt 简介

## libvirt 的安装与配置

### ubuntu 20.04 apt 安装

```shell
sudo apt install -y virt-manager libvirt-daemon-system virtinst libvirt-clients bridge-utils
```

> - `virt-manager` – 一款通过 libvirt 守护进程，基于 QT 的图形界面的虚拟机管理工具
> - `libvirt-daemon-system` – 为运行 libvirt 进程提供必要配置文件的工具
> - `virtinst` – 一套为置备和修改虚拟机提供的命令行工具
> - `libvirt-clients` – 一组客户端的库和API，用于从命令行管理和控制虚拟机和管理程序
> - `bridge-utils` – 一套用于创建和管理桥接设备的工具

### libvirt 的配置文件

libvirt相关的配置文件都在/etc/libvirt/目录之下

```shell
# schnappi @ ASUS in /etc/libvirt [8:39:05] 
$ ls
hooks               libxl.conf          nwfilter         qemu-sanlock.conf
libvirt-admin.conf  libxl-lockd.conf    qemu             secrets
libvirt.conf        libxl-sanlock.conf  qemu.conf        virtlockd.conf
libvirtd.conf       lxc.conf            qemu-lockd.conf  virtlogd.conf
# schnappi @ ASUS in /etc/libvirt/qemu [8:39:34] 
$ ls
networks
```



1. /etc/libvirt/libvirt.conf

   ```shell
   # schnappi @ ASUS in /etc/libvirt [8:41:22] 
   $ cat libvirt.conf 
   #
   # This can be used to setup URI aliases for frequently
   # used connection URIs. Aliases may contain only the
   # characters  a-Z, 0-9, _, -.
   #
   # Following the '=' may be any valid libvirt connection
   # URI, including arbitrary parameters
   
   #uri_aliases = [
   #  "hail=qemu+ssh://root@hail.cloud.example.com/system",
   #  "sleet=qemu+ssh://root@sleet.cloud.example.com/system",
   #]
   
   #
   # These can be used in cases when no URI is supplied by the application
   # (@uri_default also prevents probing of the hypervisor driver).
   #
   #uri_default = "qemu:///system"
   
   ```

   > libvirt.conf文件用于配置一些常用libvirt连接（通常是远程连接）的别名。
   >
   > 其中，配置了sleet这个别名，用于指代qemu+ssh://rootsleet.cloud.example

2. /etc/libvirt/libvirtd.conf

