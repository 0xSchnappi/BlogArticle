[toc]

# 第四章 KVM 管理工具

# libvirt

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
   > 其中，配置了sleet这个别名，用于指代qemu+ssh://rootsleet.cloud.example/system这个远程的libvirt连接。有了这个别名后，就可以在用virsh等工具或自己写代码调用libvirt API时使用这个别名，而不需要写完整的、冗长的URI连接标识了。用virsh使用这个别名，连接到远程的libvirt上查询当前已经启动的客户机状态，然后退出连接。

2. /etc/libvirt/libvirtd.conf

   > libvirtd.conf是libvirt的守护进程libvirtd的配置文件，被修改后需要让libvirtd重新加载配置文件（或重启libvirtd）才会生效。在libvirtd.conf中配置了libvirtd启动时的许多设置，包括是否建立TCP、UNIX domain socket等连接方式及其最大连接数，以及这些连接的认证机制，设置libvirtd的日志级别等。

   ```shell
   listen_tls = 0		# 关闭TLS安全认证的连接（默认是打开的）
   listen_tcp = 1		# 打开TCP连接（默认是关闭TCP连接的）
   tcp_port = "16509"	#设置TCP监听端口
   unix_sock_dir = "/var/run/libvirt"	# 设置UNIX domain socket 的保存目录
   auth_tcp = "none"	# TCP连接不使用认证授权方式
   ```

   > **注意**：要使TCP、TLS等连接生效，需要启动libvirtd时加上`--listen`参数（简写为-l）。而默认的`systemctl start libvirtd`命令在启动libvirtd服务时并没带`--listen`参数。所以如果要使用TCP等连接方式，可以使用`libvirtd --listen -d`命令来启动libvirtd。

3. /etc/libvirt/qemu.conf

   > qemu.conf是libvirt对QEMU的驱动的配置文件，包括VNC、SPICE等，以及连接它们时采用的权限认证方式的配置，也包括内存大页、SELinux、Cgroups等相关配置。

4. /etc/libvirt/qemu/ 目录

   > 在qemu目录下存放的是使用QEMU驱动的域的配置文件。
   >
   > 可以使用virt-manager工具创建域的XML配置文件，默认会将其配置文件保存到/etc/libvirt/qemu/目录下，而其中的networks目录保存了创建一个域时默认使用的网络配置。

### libvirtd 的使用

libvirtd 是一个作为libvirt虚拟化管理系统中的服务器端的守护进程，要让某个节点能够利用libvirt进行管理（无论是本地还是远程管理），都需要在这个节点上运行libvirtd这个守护进程，以便让其他上层管理工具可以连接到该节点，libvirtd负责执行其他管理工具发送给它的虚拟化管理操作指令。而libvirt的客户端工具（包括virsh、virt-manager等）可以连接到本地或远程的libvirtd进程，以便管理节点上的客户机（启动、关闭、重启、迁移等）、收集节点上的宿主机和客户机的配置和资源使用状态。

libvirtd作为一个服务（service）配置在系统中，所以可以通过systemctl命令来对其进行操作。

|            命令            |                             释义                             |
| :------------------------: | :----------------------------------------------------------: |
|  systemctl start libvirtd  |                        启动 libvirtd                         |
| systemctl restart libvirtd |                        重启 libvirtd                         |
| systemctl reload libvirtd  | 不重启服务但重新加载配置文件（`/etc/libvirt/libvirtd.conf`） |
| systemctl status libvirtd  |                     查询libvirtd服务状态                     |

在默认情况下，libvirtd在监听一个本地的Unix domain socket,而没有监听基于网络的TCP/IP socket,需要使用“-l 或--listen”的命令行参数来开启对libvirtd.conf配置文件中TCP/IP socket的配置。另外，libvirtd守护进程的启动和停止，并不会直接影响正在运行中的客户机。libvirtd在启动或重启完成时，只要客户机的XML配置文件是存在的，libvirtd会自动加载这些客户机的配置，获取它们的信息。当然，如果客户机没有基于libvirt格式的XML文件来运行（例如直接使用qemu命令行来启动的客户机），libvirtd则不能自动发现它。

libvirtd是一个可执行程序，不仅可以使用“systemctl”命令调用它作为服务来运行而且可以单独的运行libvirtd命令来使用它

> 1. -d 或 --daemon
>
>    > 表示让libvirtd作为守护进程（daemon）在后台运行
>
> 2. -f 或 --config *FILE*
>
>    > 指定libvirtd的配置文件为*FILE*,而不是使用默认值（通常是`/etc/libvirt/libvirtd.conf`）
>
> 3. -l 或 --listen
>
>    > 开启配置文件中配置的TCP/IP连接
>
> 4. -p 或 --pid-file *FILE*
>
>    > 将libvirtd进程的PID写入*FILE*文件中，而不是使用默认值（通常是/var/run/libvirtd.pid）。
>
> 5. -t 或 --timeout *SECONDS*
>
>    > 设置对libvirtd连接的超时时间为SECOND秒。
>
> 6. -v 或 --verbose
>
>    > 执行命令输出详细的输出信息。特别是在运行出错是，详细的输出信息便于用户查找原因。
>
> 7. --version
>
>    > 显示libvirtd程序的版本信息

## libvirt 域的XML配置文件

### 示例

```xml
<!--
     WARNING: THIS IS AN AUTO-GENERATED FILE. CHANGES TO IT ARE LIKELY TO BE 
     OVERWRITTEN AND LOST. Changes to this xml configuration should be made using:
       virsh edit ubuntu_20_04
       or other application using the libvirt API.
 -->

<domain type='kvm'>
  <name>ubuntu_20_04</name>
  <uuid>7e7bc9fe-b5a7-11ed-a581-af520e544069</uuid>
  <memory unit='KiB'>1048576</memory>
  <currentMemory unit='KiB'>1048576</currentMemory>
  <vcpu placement='static'>2</vcpu>
  <os>
    <type arch='x86_64' machine='rhel6.3.0'>hvm</type>
    <boot dev='hd'/>
    <boot dev='cdrom'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw' cache='none'/>
      <source file='/var/lib/libvirt/images/rhel6u3-1.img'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </disk>
    <controller type='usb' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='ide' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
    </controller>
    <interface type='bridge'>
      <mac address='52:54:00:e9:e0:3b'/>
      <source bridge='br0'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <input type='tablet' bus='usb'/>
    <input type='mouse' bus='ps2'/>
    <graphics type='vnc' port='-1' autoport='yes'/>
    <sound model='ich6'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </sound>
    <video>
      <model type='cirrus' vram='9216' heads='1'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </memballoon>
  </devices>
</domain>
```



### CPU、内存、启动顺序等基本配置

#### CPU 的配置

```xml
  <vcpu placement='static'>2</vcpu>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <cpu mode='custom' match='exact' check='partial'>                                       
    <model fallback='allow'>Westmere</model>
  </cpu>
```

> - vcpu标签，表示客户机中vcpu的个数
> - festures标签，表示Hypervisor为客户机打开或关闭CPU或其他硬件特性。这里打开了ACPI、APIC和PAE等特性
> - CPU模型的配置
>   1. custom模式：基于某个基础的CPU模型，再做个性化设置
>   2. host-model模式：根据物理CPU的特性，选择一个与之最接近的标准CPU型号，如果没有指定CPU模式，默认也是使用这种模式。xml文件为<cpu mode='host-model' />
>   3. host-passthrough模式：直接将物理CPU特性暴露给虚拟机使用，在虚拟机上看到的完全就是物理CPU的型号。XML配置文件为：<cpu mode='host-passthrough' />

- 对VCPU的分配，可以有更细粒度的配置

  ```xml
  <domain>
      <vcpu placement='static' cpuset="1-4,^3,6" current="1">2</vcpu>
  </domain>
  ```

  > cpuset表示允许到哪些物理CPU上执行，这里表示客户机的两个vCPU被允许调度到1、2、4、6号物理CPU上执行（^3表示排除3号），而current表示启动客户机时只给1个vCPU,最多可以增加到使用2个vCPU.

- libvirt还提供cputune标签来对CPU的分配进行更多调节

  ```xml
  <domain>
      <cputune>
          <vcpupin vcpu="0" cpuset="1"/>
          <vcpupin vcpu="1" cpuset="2,3"/>
          <vcpupin vcpu="2" cpuset="4"/>
          <vcpupin vcpu="3" cpuset="5"/>
          <emulatorpin cpuset="1-3"/>
          <shares>2048</shares>
          <period>1000000</period>
          <quota>1</quota>
          <emulator_period>1000000</emulator_period>
          <emulator_quota>-1</emulator_quota>
      </cputune>
  </domain>
  ```

  > vcpupin标签表示将虚拟CPU绑定到某一个或多个物理CPU上
  >
  > - <vcpupin vcpu="2" cpuset="4"/>：表示客户机2号虚拟机CPU被绑定到4号物理CPU上
  > - <emulatorpin cpuset="1-3"/>：表示将QEMU emulator绑定到1～3号物理CPU上
  > - <shares>2048</shares>：表示客户机占用CPU时间的加权配置

- 还可以配置客户机的NUMA拓扑

#### 内存的配置

```xml
  <memory unit='KiB'>2097152</memory>
  <currentMemory unit='KiB'>2097152</currentMemory>
```

> 内存大小2097152KB（即2GB），
>
> - memory：表示客户机最大可使用的内存
> - currentMemory：表示启动时即分配给客户机使用的内存
>
> 在使用QEMU/KVM时，一般将二者设置为相同的值

- 内存的ballooning相关的配置

  > **KVM的内存气球技术**使得可以在虚拟机中按照需要调整的内存大小，提升内存的利用率。使用的时候，默认情况是需要安装virt balloon的驱动，内核开启CONFIG_VIRTIO_BALLOON。CentOS7默认已经开启了此选项，并且也安装了virtballoon驱动。
  >
  > **balloon有两种类型**
  >
  >  膨胀：虚拟机的内存被拿掉给宿主机
  >
  >  压缩：宿主机的内存还给虚拟机
  >
  >  气球技术最大优点是内存可以超用，缺点是可能造成内存不够用的而影响性能

  ```xml
  <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>
  </memballoon>
  ```

  > 内存的ballooning相关的配置包含在devices这个标签的memballoon子标签中，该标签配置了该客户机的内存气球设备。
  >
  > 该配置将为客户机分配一个使用virtio-balloon驱动的设备，以便实现客户机内存的ballooning调节。该设备在客户机中的PCI设备编号为0000:00:08.0。

#### 客户机系统类型和启动顺序

```xml
<os>
    <type arch='x86_64' machine='pc'>hvm</type>
    <boot dev='hd'/>
    <boot dev='cdrom'/>
</os>
```

> - <type arch='x86_64' machine='pc'>hvm</type>：表示客户机类型是hvm类型，操作系统架构是x86_64,机器类型是pc
>   1. HVM（hardware virtual machine,硬件虚拟机）表示在硬件辅助虚拟化技术（Intel VT和AMD-V等）的支持下不需要修改客户机操作系统就可以启动客户机。
> - boot选项用于设置客户机启动时的设备，这里有hd（即硬盘）和cdrom（光驱）两种，而且按照硬盘、光驱的顺序启动的，它们在XML配置文件中的先后顺序即启动时的先后顺序.

### 网络配置

#### 桥接方式的网络配置

```xml
<devices>
    <interface type="bridge">
      <mac address='52:54:00:e9:e0:3b'/>
      <source bridge='br0'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
</devices>
```

> - type='bridge'：表示使用桥接方式使客户机获得网络，address用于配置客户机中网卡的MAC地址
> - <source bridge='br0'/>：表示使用宿主机中的br0网络接口来建立网桥
> - <model type='virtio'/>：表示在客户机中使用virtio-net驱动的网卡设备
> - 配置了该网卡在客户机中的PCI设备编号为`10000:00:03.0`

#### NAT 方式的虚拟网络配置

```xml
<devices>
    <interface type="network">
      <mac address='52:54:00:e9:e0:3b'/>
      <source network='default'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
</devices>
```

> type='network'和<source network='default'/>表示使用NAT的方式，并使用默认的网络配置

```xml
<network>
  <name>default</name>
  <uuid>6c0e0732-9704-49fa-a194-c7170f4af063</uuid>
  <forward mode='nat'/>
  <bridge name='virbr0' stp='on' delay='0'/>
  <mac address='52:54:00:f0:29:07'/>
  <ip address='192.168.122.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.122.2' end='192.168.122.254'/>
    </dhcp>
  </ip>
</network>

```

> 客户机将会分配到192.168.122.0/24网段中的一个IP地址

#### 用户模式网络的配置

```xml
<devices>
    <interface type="user">
      <mac address='52:54:00:e9:e0:3b'/>
    </interface>
</devices>
```

> type="user"表示该客户机的网络接口是用户模式网络，是完全由QEMU软件模拟的一个网络协议栈。在宿主中，没有一个虚拟的网络接口连接到virbr0这样的网桥

#### 网卡设备直接分配（VT-d）

> 设备直接分配在域的XML配置文件中有两种方式：一种是较新的方式使用`<interface type='hostdev'>`标签；另一种是较旧但支持设备广泛的方式，直接使用`<hostdev>`标签

- `<interface type='hostdev'>`

  ```xml
  <device>
      <interface type='hostdev'>
          <driver name='vfio'/>
          <source>
              <address type='pci' domain='0x0000' bus='0x08' slot='0x10' function='0x0'/>
          </source>
          <mac address='52:54:00:6d:90:02'/>
      </interface>
  </device>
  ```

  > 目前支持libvirt 0.9.11以上的版本，而且支持SR-IOV特性的VF的直接配置。在`<interface type='hostdev'>`标签中，用`<driver name='vfio'/>`指定使用哪一种分配方式（默认是VFIO,如果使用较旧的传统的device assignment方式，这个值可配为`'kvm'`），用`<source>`标签来指示将宿主机哪个VF分配给客户机使用，还可使用`<mac address='52:54:00:6d:90:02'/>`来指定网卡的MAC地址

- `<hostdev>`

  ```xml
  <device>
      <hostdev mode='subsystem' type='pci' managed='yes'>
          <source>
              <address domain='0x0000' bus='0x08' slot='0x00' function='0x0'/>
          </source>
      </hostdev>
  </device>
  ```

  > 是libvirt 0.9.11版本之前对设备直接分配的唯一使用方式，而且对设备的支持比较广泛，既支持有SR-IOV功能的高级网卡的VF的直接分配，也支持无SR-IOV功能的普通PCI或PCI-e网卡的直接分配。这种方式并不支持对直接分配的网卡MAC地址的设置。

### 存储配置

### 其他配置

## libvirt API简介

## 建立到 Hypervisor的连接

### 本地 URI

### 远程 URI

### 使用 URI 建立到 Hypervisor 的连接

## libvirt API 使用示例

### libvirt 的 C API 使用

### libvirt 的 Python API 的使用 





