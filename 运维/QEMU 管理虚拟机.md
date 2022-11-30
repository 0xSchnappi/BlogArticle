# QEMU 管理虚拟机

## qemu-img create

- create
  
  > 在文件系统上创建新磁盘映像。
  
  ```shell
  qemu-img create -f qcow2 mac_hdd_ng.img 128G
  ```
  
  > [-f qcow2]:目标映像的支持格式为raw和qcow2
  > 
  > [mac_hdd_ng.img]:目标映像文件的路径
  > 
  > [128G]:目标映像文件的最大大小(也就是虚拟磁盘大小)

- info
  
  > 显示相关磁盘映像的信息。
  
  ```shell
  OSX-KVM$ qemu-img info mac_hdd_ng.img
  image: mac_hdd_ng.img
  file format: qcow2
  virtual size: 128 GiB (137438953472 bytes)
  disk size: 196 KiB
  cluster_size: 65536
  Format specific information:
      compat: 1.1
      lazy refcounts: false
      refcount bits: 16
      corrupt: false
  ```
  
  > 

- check
  
  > 检查现有磁盘映像是否有错误。

- compare
  
  > 检查两个映像的内容是否相同。

- map
  
  > 转储映像文件名的元数据及其后备文件链。

- amend
  
  > 修正映像文件名的映像格式特定选项。

- convert
  
  > 将现有磁盘映像转换为其他格式的新映像。

- snapshot
  
  > 管理现有磁盘映像的快照。

- commit
  
  > 应用对现有磁盘映像进行的更改。

- rebase
  
  > 基于现有映像创建新的基本映像。

- resize
  
  > 增大或减小现有映像的大小。

## qemu-system-x86_64

# 
