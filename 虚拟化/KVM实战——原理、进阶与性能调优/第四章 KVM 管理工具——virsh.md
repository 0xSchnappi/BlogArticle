[toc]

# KVM管理工具——Virsh

## virsh 简介

> virsh 是用于管理虚拟化环境中的客户和Hypervisor的命令行工具，通过调用libvirt API来实现虚拟化的管理。virsh是完全在命令行文本模式下运行的用户态工具，它是系统管理员通过脚本程序实现虚拟化自动部署和管理的理想工具之一。virsh程序的源代码在libvirt项目源代码的tools目录下，实现virsh工具最核心的一个源代码文件是virsh.c。

## virsh 常用命令

### 域管理命令

| 命令                            | 功能描述                                                     |
| ------------------------------- | ------------------------------------------------------------ |
| list                            | 获取当前节点上所有域的列表                                   |
| domstate <ID or Name or UUID>   | 获取一个域的运行状态                                         |
| dominfo <ID>                    | 获取一个域的基本信息                                         |
| domid <Name or UUID>            | 根据域的名称或UUID返回域的ID值                               |
| domname <ID or UUID>            | 根据域的ID或UUID返回域的名称                                 |
| dommemstat <ID>                 | 获取一个域的内存使用情况的统计信息                           |
| setmem <ID> <mem-size>          | 设置一个域的内存大小（默认单位为KB）                         |
| vcpuinfo <ID>                   | 获取一个域的vCPU的基本信息                                   |
| vcpuin <ID> <vCPU> <pCPU>       | 将一个域的vCPU绑定到某个物理CPU上运行                        |
| setvcpus <ID> <vCPU-num>        | 设置一个域的vCPU的个数                                       |
| vncdisplay <ID>                 | 获取一个域的VNC连接IP地址和端口                              |
| create <dom.xml>                | 根据域的XML配置文件创建一个域（客户机）                      |
| define <dom.xml>                | 定义一个域(但不启动)                                         |
| start <ID>                      | 启动一个（预定义的）域                                       |
| suspend <ID>                    | 暂停一个域名                                                 |
| resume <ID>                     | 唤醒一个域名                                                 |
| shutdown <ID>                   | 让一个域执行关机操作                                         |
| reboot <ID>                     | 让一个域重启                                                 |
| reset <ID>                      | 强制重启一个域，相当于在物理机器上按"reset"按钮（可能会损坏该域的文件系统） |
| destroy <ID>                    | 立即销毁一个域，相当于直接拔掉物理机器的电源线（可能会损坏该域的文件系统） |
| save <ID> <file.img>            | 保存一个运行中的域的状态到一个文件中                         |
| restore <file.img>              | 从一个被保存的文件中恢复一个域的运行                         |
| migrate <ID> <dest_url>         | 将一个域迁移到另外一个目的地址                               |
| dump <ID> <core.file>           | coredump一个域保存到一个文件                                 |
| attach-device <ID> <device.xml> | 向一个域添加XML文件中的设备（热拔插）                        |
| detach-device <ID> <device.xml> | 将XML文件中的设备从一个域中移除                              |
| console <ID>                    | 连接到一个域的控制台                                         |

### 宿主机和Hypervisor的管理命令

| 命令                                        | 功能描述                                                     |
| ------------------------------------------- | ------------------------------------------------------------ |
| version                                     | 显示libvirt和Hypervisor的版本信息                            |
| sysinfo                                     | 以XML格式打印宿主机系统的信息                                |
| nodeinfo                                    | 显示该节点的基本信息                                         |
| uri                                         | 显示当前连接的URI                                            |
| hostname                                    | 显示当前节点（宿主机）的主机名                               |
| capabilities                                | 显示该节点宿主机和客户机的架构和特性                         |
| freecell                                    | 显示当前MUMA单元的可用空闲存储                               |
| nodememstats <cell>                         | 显示该节点的（某个）内存单元使用情况的统计                   |
| connect <URI>                               | 连接到URI指示的Hypervisor                                    |
| nodecpustats <cpu-num>                      | 显示该节点的（某个）CPU使用情况统计                          |
| qemu-attach <pid>                           | 根据PID添加一个QEMU进程到libvirt中                           |
| qemu-monitor-command domian [--hmp] command | 向域的QEMU monitor 中发送一个命令，一般需要“--hmp”参数，以便直接传入monitor中的命令不需要转换 |

### 网络的管理命令

| 命令                            | 功能描述                                |
| ------------------------------- | --------------------------------------- |
| iface-list                      | 显示出物理主机的网络接口列表            |
| iface-mac <if-name>             | 根据网络接口名称查询其对应的MAC地址     |
| iface-name <MAC>                | 根据MAC地址查询其对应的网络接口名称     |
| iface-edit <if-name-or-uuid>    | 编辑一个物理主机的网络接口的XML配置文件 |
| iface-dumpxml <if-name-or-uuid> | 以XML格式转存出一个网络接口的状态信息   |
| iface-destroy <if-name-or-uuid> | 关闭宿主机上的一个物理网络接口          |
| net-list                        | 列出libvirt管理的虚拟网络               |
| net-info <net-name-or-uuid>     | 根据名称查询一个虚拟网络的基本信息      |
| net-uuid <net-name>             | 根据UUID查询一个虚拟网络名称            |
| net-create <net.xml>            | 根据一个网络XML配置文件创建一个虚拟网络 |
| net-edit <net-name-or-uuid>     | 编译一个虚拟网络的XML配置文件           |
| net-dumpxml <net-name-or-uuid>  | 转存出一个虚拟网络的XML格式化的配置信息 |
| net-destroy <net-name-or-uuid>  | 销毁一个虚拟网络                        |

### 存储池和存储卷的管理命令

| 命令                                     | 功能描述                              |
| ---------------------------------------- | ------------------------------------- |
| pool-list                                | 显示libvirt管理的存储池               |
| pool-info <pool-name>                    | 根据一个存储池名称查询其基本信息      |
| pool-uuid <pool-name>                    | 根据存储池名称查询其基本信息          |
| pool-create <pool.xml>                   | 根据XML配置文件的信息创建一个存储池   |
| pool-edit <pool-name-or-uuid>            | 编辑一个存储池的XML配置文件           |
| pool-destroy <pool-name-or-uuid>         | 关闭一个存储池（在libvirt可见范围内） |
| pool-delete <pool-name-or-uuid>          | 删除一个存储池（不可恢复）            |
| vol-list <pool-name-or-uuid>             | 查询一个存储池中的存储卷的列表        |
| vol-name <vol-key-or-path>               | 查询一个存储卷的名称                  |
| vol-path --pool <pool> <vol-name-or-key> | 查询一个存储卷的路径                  |
| vol-create <vol.xml>                     | 根据XML配置文件创建一个存储池         |
| vol-clone <vol-name-path> <name>         | 克隆一个存储卷                        |
| vol-delete <vol-name-or-key-or-path>     | 删除一个存储卷                        |





