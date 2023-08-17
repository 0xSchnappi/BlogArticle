[toc]

# 第四章 KVM 管理工具——libvirt

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

```xml
<device>
    <disk type='file' device='disk'>
        <driver name='qemu' type='qcow2' cache='none'/>
        <source file='/var/lib/libvirt/images/centos7u2.qcow2'/>
        <target dev='vda' bus='virtio'/>
        <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
    </disk>
</device>
```

> 表示使用`qcow2`格式的`centos7u2.qcow`镜像文件作为客户机的磁盘，其在客户机中使用`virtio`总线（使用`virtio-blk`驱动），设备名称为`/dev/vda`，其PCI地址为`0000:00:07.0`
>
> - `<disk>`属性
>
>   > 1. `type`：属性表示磁盘使用哪种类型作为磁盘的来源，其取值为file、block、dir、或network中的一个，分别表示使用文件、块设备、目录或网络作为客户机磁盘来源。
>   > 2. `device`：属性表示让客户机如何使用该块设备，其取值为floppy、disk、cdrom或lun中的一个，分别为软盘、硬盘、光盘和LUN（逻辑单元号），默认值为disk（硬盘）
>
> - `<disk>`子标签
>
>   > driver用于定义Hypervisor如何为该磁盘提供驱动，它的name属性用于指定宿主机中使用的后端驱动名称，QEMU/KVM仅支持name='qemu'，但是支持的类型type可以是很多，包括raw、qcow2、qed、bochs等。cache属性表示在宿主机中打开该磁盘是使用的缓存方式，可以配置为default、none、writethrough、writeback、directsync和unsafe等多种模式。
>
> - `<source>`子标签
>
>   > 表示磁盘的来源
>   >
>   > 1. 当<disk>标签的type属性为file时，应该配置为<source file='/var/lib/libvirt/images/centos7u2.qcow2'/>这样
>   > 2. 当<disk>标签的type属性为block时，应该配置为<source dev='/dev/sda'/>这样
>
> - `<target>`
>
>   > 表示磁盘暴露给客户机时的总线类型和设备名称
>   >
>   > 1. dev属性表示客户机中该磁盘设备的逻辑设备名称
>   > 2. bus属性表示该磁盘设备被模拟挂载的总线类型，bus属性的值可以为ide、scsi、virtio、usb、sata等
>   >
>   > 如果省略了bus属性，libvirt会根据dev属性中的名称来“推测”bus属性的值，例如，sda会被推测是scsi,而vda被推测是virtio.
>
> - `<address>`
>
>   > 表示磁盘设备在客户机中的PCI总线地址。如果该标签不存在，libvirt会自动分配一个地址。

### 其他配置

1. QEMU 模拟器配置

   ```xml
   <device>
       <emulator>/usr/local/bin/qemu-system-x86_64</emulator>
   </device>
   ```

   > 需要指定使用的设备模型的模拟器，需要绝对路径。

   ```xml
   <type arch='x86_64' machine='pc'>hvm</type>
   ```

   > 自己编译的`qemu-system-x86_64`，这个配置必须为`machine='pc'`

2. 图形显示方式

   ```xml
   <device>
       <graphics type='vnc' port='-1' autoport='yes'/>
   </device>
   ```

   > 表示通过VNC的方式连接到客户机，其VNC端口为libvirt自动分配

   ```xml
   <device>
       <graphics type='sdl' display=':0.0'/>
       <graphics type='vnc' port='5904'>
           <listen type='address' address='1.2.3.4'/>
       </graphics>
       <graphics type='rdp' autoport='yes' multiUser='yes' />
       <graphics type='desktop' fullscreen='yes' />
       <graphics type='spice'>
           <listen type='network' network='rednet'
       </graphics>
   </device>
   ```

   > 支持其他多种类型的图形显示方式，配置了SDL、VNC、RDP、SPICE等

3. 客户机声卡和显卡的配置

   ```xml
   <device>
       <sound model='ich6'>
           <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
       </sound>
       <video>
           <model type='qxl' ram='65536'  vram='65536' vgamem='16384' heads='1'/>
           <address type='pci' domain='0x0000' bus='0x00' slot-'0x02' function='0x0'/>
       </video>
   </device>
   ```

   > - <sound>表示的是声卡配置，model表示为客户机模拟的声卡类型，取值为es1370、sb16、ac97和ich6中的一个。
   > - `<video>`表示显卡配置
   > - <model>为客户机模拟的显卡类型
   >   1. type属性的取值可以为vga、cirrus、vmvga、xen、vbox、qxl中的一个
   >   2. vram属性表示虚拟显卡的显存容量（单位为KB）
   >   3. heads属性表示显示屏幕的序号

4. 串口和控制台

   > 串口和控制台的主要用途，在调试客户机的内核或遇到客户机宕机的情况下，一般都可以在串口或控制台中查看一些利于系统管理员分析问题的日志信息。

   ```xml
   <device>
       <serial type='pty'>
           <target port='0'/>
       </serial>
       <console type='pty'>
           <target type='serial' port='0'
       </console>
   </device>
   ```

   > 设置了客户机的编号为0的串口（即`/dev/ttyS0`），使宿主机的伪终端（pty），由于这里没有指定使用宿主机中的哪个虚拟终端，因此libvirt会自己选择一个空闲的虚拟机终端（可能为/dev/pts下的任意一个）。当然也可以加上`<source path='/dev/pts/1'/>`配置来明确指定使用宿主机中的哪一个虚拟终端。
   >
   > 通常情况下，控制台（console）配置在客户机中的类型为`serial`，此时，如果没有配置串口（serial），则会将控制台的配置复制到串口配置中，如果已经配置了串口，则libvirt会忽略控制台的配置项。

5. 输入设备

   ```xml
   <device>
       <input type='tablet' bus='usb'/>
       <input type='mouse' bus='ps2'/>
       <input type='keyboard' bus='ps2'/>
   </device>
   ```

   > 配置会让QEMU模拟PS2接口的鼠标和键盘，还提供了tablet这种类型的设备，让光标可以在客户机获取绝对位置定位。

6. PCI控制器

   ```xml
   <controller type='usb' index='0' model='ich9-ehcil'>
       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x07'/>
   </controller>
   <controller type='usb' index='0' model='ich9-ehcil'>
       <master startport='0'/>
       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0' multifunction='on'/>
   </controller>
   <controller type='usb' index='0' model='ich9-ehcil'>
       <master startport='2'/>
       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x1'/>
   </controller>
   <controller type='usb' index='0' model='ich9-ehcil'>
       <master startport='4'/>
       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x2'/>
   </controller>
   <controller type='pci' index='0' model='pci-root'/>
   <controller type='virtio-serial' index='0' model='ich9-ehcil'>
       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
   </controller>
   ```

   > 显式指定了4个USB控制器、1个pci-root和1个virtio-serial控制器。libvirt默认还会为客户机分配一些必要的PCI设备，如PCI主桥（Host bridge）、ISA桥等。

## libvirt API简介

- 连接Hypervisor相关的API

  > 以virConnect开头的一系列函数，与Hypervisor建立连接

  1. virConnectOpen

     > 函数可以建立一个连接，返回值是一个virConnectPtr对象，该对象就代表到Hypervisor的一个连接；如果连接出错，则返回空值（NULL）。

  2. virConnectOpenReadOnly

     > 建立一个只读的连接，在该连接上可以使用一些查询的功能，而不使用创建、修改等功能。

  3. virConnectOpenAuth

     > 函数提供了根据认证建立的连接

  4. virConnectGetCapabilities

     > 函数返回对Hypervisor和驱动的功能描述的XML格式的字符串。

  5. virConnectListDomains

     > 函数返回一列与标识符，他们代表该Hypervisor上的活动域。

- 域管理的API

  > 以virDomainPtr开头的一系列函数，获取域对象

  1. 获取域的对象

     > `virDomainLookupByID`、`virDomainLookupByUUID`、`virDomainLookupByName`：
     >
     > 函数根据ID、UUID、Name值到conn这个连接上去查找相应的域

  2. 查询域的信息

     > `virDomainGetHostname`,`virDomainGetInfo`,`virDomainGetVcpus`,`virDomainGetVcpusFlags`,`virDomainGetCPUStats`等

  3. 控制域的生命周期

     > `virDomainCreate`,`virDomainSuspend`,`virDomainResume`,`virDomainDestroy`,`virDomainMigrate`等

- 节点管理的API

  > 以virNode开头的一系列函数，对节点进行信息查询和控制功能

  1. virNodeGetInfo

     > 获取节点的物理硬件信息

  2. virNodeGetCPUStats

     > 可以获取节点上各个CPU的使用统计信息

  3. virNodeGetMemoryStats

     > 函数可以获取节点上的内存的使用统计信息

  4. virNodeGetFreeMemory

     > 函数可以获取节点上可用的空闲内存大小

  5. virNodeSetMemoryParameters

     > 函数可以设置节点上内存的调度参数

  6. virNodeSuspendForDuration

     > 函数可以让节点（宿主机）暂停运行一段时间

- 网络管理的API

  > 以virNetwork开头的一系列函数和部分以virInterface开头的函数，查询和控制虚拟网络。

  1. virNetworkGetName

     > 获取网络名称

  2. virNetworkGetBridgeName

     > 获取网络中网桥的名称

  3. virNetworkGetUUID

     > 获取网络的UUID标识

  4. virNetworkGetXMLDesc

     > 获取网络的以XML格式的描述

  5. virNetworkIsActive

     > 网络是否正在使用

  6. virNetworkCreareXML

     > 根据提供的XML格式的字符串创建一个网络

  7. virNetworkDestroy

     > 函数可以销毁一个网络（同时也会关闭使用该网络的域）

  8. virNetworkFree

     > 函数可以回收一个网络（但不会关闭正在运行的域）

  9. virNetworkUpdate

     > 根据提供XML格式的网络配置来更新一个已存在的网络。

  10. virInterface

      > virInterfaceCreate、virInterfaceFree、virInterfaceDestroy、virInterfaceGetName、virInterfaceIsActive等函数可以用于创建、释放和销毁网络接口，以及查询网络接口的名称和激活状态。

- 存储卷管理的API

  > 以virStorageVol开头的一系列函数，主要是对域的镜像文件管理，
  >
  > 获取存储卷对象：

  1. virStorageVolLookupByKey

     > 根据全局唯一的键值来获取一个存储卷对象

  2. virStorageVolLookupByName

     > 根据名称在一个存储资源池（storage pool）中获取一个存储卷对象

  3. virStorageVolLookupByPath

     > 根据它在节点上路径来获取一个存储卷对象

  > 查询存储卷信息：

  1. virStorageVolGetName

     > 查询某个存储卷的使用情况

  2. virStorageVolGetName

     > 获取存储卷的名称

  3. virStorageVolGetPath

     > 获取存储卷路径

  4. virStorageVolGetConnect

     > 查询存储卷的连接

  > 创建和修改存储卷：

  1. virStorageVolCreateXML

     > 根据提供的XML描述来创建一个存储卷

  2. virStorageVolFree

     > 释放存储卷的句柄（但是存储卷依然存在）

  3. virStorageVolDelete

     > 删除一个存储卷

  4. virStorageVolResize

     > 可以调整存储卷的大小

- 存储池管理的API

  > 以virStoragePool开头的一系列函数。
  >
  > libvirt对存储池（pool）的管理包括对本地的基本文件系统、普通网络共享文件系统、iSCSI共享文件系统、LVM分区等的管理
  >
  > | 函数名                       | 描述                                                         |
  > | ---------------------------- | ------------------------------------------------------------ |
  > | virStoragePoolLookupByName   | 根据存储池的名称来获取一个存储池对象                         |
  > | virStoragePoolLookupByVolume | 根据一个存储卷返回其对应的存储池对象                         |
  > | virStoragePoolCreateXML      | 根据XML描述创建一个存储池（默认已激活）                      |
  > | virStoragePoolDefineXML      | 根据XML描述静态定义一个存储池（尚未激活）                    |
  > | virStoragePoolCreate         | 可以激活一个存储池                                           |
  > | virStoragePoolGetInfo        | 获取存储池信息                                               |
  > | virStoragePoolGetName        | 获取存储池名称                                               |
  > | virStoragePoolGetUUID        | 获取存储池UUID                                               |
  > | virStoragePoolIsActive       | 查询存储池状态是否处于使用中                                 |
  > | virStoragePoolFree           | 函数可以释放存储池相关的内存（但是不改变其在宿主机中的状态） |
  > | virStoragePoolDestroy        | 用于销毁一个存储池（但并没有释放virStoragePoolPtr对象，之后还可以用virStoragePoolCreate函数重新激活） |
  > | virStoragePoolDelete         | 物理删除一个存储池资源（该操作不可恢复）                     |
  >
  > 

- 事件管理的API

  > 以virEvent开头的函数。
  >
  > libvirt支持事件机制，在使用该机制注册之后，可以在发生特定的事件（如域的启动、暂停、恢复、停止等）时得到自己定义的 一些通知

- 数据流管理的API

  > 以virStream开头的函数
  >
  > libvirt提供了一系列函数用于数据流传输

## 建立到 Hypervisor的连接

URI（Uniform Resource Identifier）统一资源标识符

### 本地 URI

```shell
driver[+transport]:///[path][?extral-param]
```

> driver是连接Hypervisor驱动名称（如qemu、xen、xbox、lxe等）
>
> transport选择该连接使用的传输方式
>
> path连接到服务器端上的某个路径
>
> ?extral=param是可以额外添加一些参数（如Unix domain sockect的路径）

- qemu:///session：连接到本地的session实例，该连接仅能管理当前用户的虚拟化资源
- qemu+unix:///session：以Unix domain sockert的方式连接到本地的session实例，该连接仅能管理当前用户的虚拟化资源
- qemu:///system：连接到本地的system实例，该连接能管理当前节点的所有特权用户可以管理虚拟化资源
- qemu+unix:///system：以Unix domain sockert的方式连接到本地的system实例，该连接能管理当前节点的所有特权用户可以管理虚拟化资源

### 远程 URI

```shell
driver[+transport]://[user@][host][:port]/[path][?extral-param]
```

> transport 表示传输方式，取值可以是ssh、tcp、libssh2等。

- qemu+ssh://root@www.example.com/system：通过ssh通道连接到远程节点的system实例，具有最大的权限来管理远程节点上的虚拟化资源。建立该远程连接时，需要经过ssh的用户名和密码验证或者基于密钥的验证。
- qemu+ssh://root@www.example.com/session：通过ssh通道连接到远程节点的使用user用户的session实例，该连接仅能对user用户的虚拟化资源进行管理。建立该远程连接时，同样需要经过ssh的验证。
- qemu://example.com/system：通过建立加密的TLS连接与远程节点的system实例相连接，具有对节点的特权管理权限。在建立该远程连接时，一般需要经过TLSx509安全协议的证书验证。
- qemu+tcp://example.com/system：通过建立非加密的普通TCP连接与远程节点的system实例相连接，具有对该节点的特权管理权限。在建立该远程连接时，一般需要经过SASL/Kerberos认证授权。

### 使用 URI 建立到 Hypervisor 的连接

在使用virsh这个libvirt客户端工具时，可以用“-c”或“--connect”选项来指定建立到某个URI的连接。只有连接建立之后，才能操作。

```shell
# schnappi @ ASUS in ~ [16:21:21] 
$ virsh -c qemu:///system
Welcome to virsh, the virtualization interactive terminal.

Type:  'help' for help with commands
       'quit' to quit

virsh # list
 Id   Name           State
------------------------------
 9    ubuntu_20_04   running

virsh # quit

```

## libvirt API 使用示例

- `Ubuntu`安装 libvirt 动态库

  ```shell
  sudo apt-get install  libvirt-dev
  ```

- Ubuntu 安装 libvirt python 包

  ```shell
  sudo apt-get install python3-libvirt
  ```

### libvirt 的 C API 使用

```shell
# schnappi @ ASUS in ~/Desktop/gist [18:34:53] 
$ gcc -o dominfo dominfo.c -lvirt

# schnappi @ ASUS in ~/Desktop/gist [18:34:57] 
$ sudo virsh list                
 Id   Name           State
------------------------------
 1    ubuntu_20_04   running


# schnappi @ ASUS in ~/Desktop/gist [18:35:01] 
$ sudo ./dominfo 
----Get domian info by ID via libvirt C API -----
Domain ID: 1
    vcpus: 5
   maxMem: 8388608 KB
   memory: 8388608 KB
```

> gcc 必须使用 `-lvirt`参数，否则会出现以下情况
>
> ```shell
> # schnappi @ ASUS in ~/Desktop/gist [17:28:55] C:1
> $ gcc dominfo.c
> /usr/bin/ld: /tmp/cc29IerI.o: in function `getDomainInfo':
> dominfo.c:(.text+0x34): undefined reference to `virConnectOpenReadOnly'
> /usr/bin/ld: dominfo.c:(.text+0x7d): undefined reference to `virDomainLookupByID'
> /usr/bin/ld: dominfo.c:(.text+0xb5): undefined reference to `virConnectClose'
> /usr/bin/ld: dominfo.c:(.text+0xd2): undefined reference to `virDomainGetInfo'
> /usr/bin/ld: dominfo.c:(.text+0x103): undefined reference to `virDomainFree'
> /usr/bin/ld: dominfo.c:(.text+0x10f): undefined reference to `virConnectClose'
> /usr/bin/ld: dominfo.c:(.text+0x198): undefined reference to `virDomainFree'
> /usr/bin/ld: dominfo.c:(.text+0x1ab): undefined reference to `virConnectClose'
> collect2: error: ld returned 1 exit status
> ```
>
> 顺便问了以下chat-gpt：`-lvirt` 是一个编译选项，用于告诉编译器在链接时使用 `libvirt` 库。具体来说，`-l` 选项是告诉编译器链接一个库文件，`virt` 是库文件的名称。在编译时使用 `-lvirt` 选项后，编译器会在系统中查找 `libvirt` 库文件并将其链接到您的程序中。这样，您的程序就可以使用 `libvirt` 库中定义的函数和符号了。

```c
/**
 * Get domain information via libvirt C API
 * 
*/

#include <stdio.h>
#include <libvirt/libvirt.h>
#include <libvirt/libvirt-host.h>

int getDomainInfo(int id)
{
    virConnectPtr conn = NULL;      /* the hypervisor connection */
    virDomainPtr dom = NULL;        /* the domain being checked */
    virDomainInfo info;             /* the information being fetched */

    /* NULL means connect to local QEMU/KVM hypervisor */
    conn = virConnectOpenReadOnly(NULL);
    if (conn == NULL)
    {
        fprintf(stderr, "Failed to connect to hypervisor\n");
        return 1;
    }

    /* Find the domain by its ID */
    dom  = virDomainLookupByID(conn, id);
    if (dom == NULL)
    {
        fprintf(stderr, "Failed to find Domain %d\n", id);
        virConnectClose(conn);
        return 1;
    }

    /*Get virDomainInfo structure of the domain */
    if (virDomainGetInfo(dom, &info) < 0)
    {
        fprintf(stderr, "Failed to get information for Domain %d\n", id);
        virDomainFree(dom);
        virConnectClose(conn);
        return 1;
    }

    /* Print some info of the domian */
    printf("Domain ID: %d\n", id);
    printf("    vcpus: %d\n", info.nrVirtCpu);
    printf("   maxMem: %ld KB\n", info.maxMem);
    printf("   memory: %ld KB\n", info.memory);

    if (dom != NULL)
    {
        virDomainFree(dom);
    }
    if (conn != NULL)
    {
        virConnectClose(conn);
    }

    return 0;
}

int main(int argc, char **argv)
{
    int dom_id = 1;
    printf("----Get domian info by ID via libvirt C API -----\n");
    getDomainInfo(dom_id);
    return 0;
}
```

### libvirt 的 Python API 的使用 

- 运行结果

  ```shell
  # schnappi @ ASUS in ~/Desktop/gist [19:14:36] 
  $ sudo /bin/python3 /home/schnappi/Desktop/gist/libvirt-test.py
  [sudo] schnappi 的密码： 
  --- Get domian info via libvirt python API ---
  ----- Connection is created successfully -----
  
  ----------- get doman info by name -----------
  Dom id: 1      name: ubuntu_20_04
  Dom state: [1, 1]
  Dom info: [1, 8388608, 8388608, 5, 75680000000]
  memory: 8192.0 MB
  memory status: {'actual': 8388608, 'swap_in': 0, 'swap_out': 0, 'major_fault': 0, 'minor_fault': 0, 'unused': 7946384, 'available': 8072388, 'usable': 7816240, 'last_update': 1679394754, 'disk_caches': 90816, 'hugetlb_pgalloc': 0, 'hugetlb_pgfail': 0, 'rss': 1921536}
  vCPUs: 5
  
  ------ get domain info by ID -----
  Domain id is 1 ; Name is ubuntu_20_04
  
  Connection is closed
  
  ```

- code

  ```c++
  #!/usr/bin/python3
  # Get domian info via libvirt python API
  # Tested with python3.10.6 and pythin3-libvirt 8.0.0 on aKVM host
  
  import libvirt
  import sys
  
  def createConnection():
      conn = libvirt.openReadOnly(None)
      if not conn:
          print('Failed to open connection to QEMU/KVM')
          sys.exit(1)
      else:
          print('----- Connection is created successfully -----')
          return conn
      
  def closeConnection(conn):
      print("")
      try:
          conn.close()
      except:
          print("Failed to close the connection")
          return 1
      
      print("Connection is closed")
      
  def getDomInfoByName(conn, name):
      print("")
      print("----------- get doman info by name -----------")
      try:
          dom = conn.lookupByName(name)
      except:
          print("Failed to find the domian with name '%s'" % name)
          return 1
      
      print("Dom id: {0}      name: {1}".format(dom.ID(), dom.name()))
      print("Dom state: {0}".format(dom.state(0)))
      print("Dom info: {0}".format(dom.info()))
      print("memory: {0} MB".format(dom.maxMemory()/1024))
      print("memory status: {0}".format(dom.memoryStats()))
      print("vCPUs: {0}".format(dom.maxVcpus()))
      
  def getDomInfoByID(conn, id):
      print("")
      print("------ get domain info by ID -----")
      try:
          dom = conn.lookupByID(id)
      except:
          print("Failed to find the domian with ID {0}".format(id))
          return 1
      
      print("Domain id is {0} ; Name is {1}".format(dom.ID(), dom.name()))
      
      
  if __name__ == "__main__":
      name = "ubuntu_20_04"
      id = 1
      print("--- Get domian info via libvirt python API ---")
      conn = createConnection()
      
      getDomInfoByName(conn, name)
      getDomInfoByID(conn, id)
      
      closeConnection(conn)
     
  ```
