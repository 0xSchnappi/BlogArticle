[toc]

# 第五章 KVM 核心基础功能——存储配置

## 存储配置和启动顺序

`QEMU`提供了对多种块存储设备的模拟，包括`IDE`设备、`SCSI设备`、软盘、`U`盘、`virtio`磁盘等，而且对设备的启动顺序提供了灵活的配置。

### 存储的基本配置选项

1. `-hda file`

   > 将*`file`*镜像文件作为客户机中的第一个`IDE`设备（序号0），在客户机中表现为`/dev/hda`设备（若客户机中使用`PIIX_IDE`驱动）或`/dev/sda`设备（若客户机中使用`ata_piix`驱动）。
   >
   > 如果不指定`-hda`或`-hdb`等参数，那么在前面一些例子中提到的`qemu-system-x86_64 /root/kvm_demo/rhe16u3.img`就与加上`-hda`参数来指定镜像文件的效果是一样的。
   >
   > 另外也可以将宿主机中的一个硬盘（如`/dev/sdb`）作为`-hda`的*`file`*参数来使用，从而让整个硬盘模拟为客户机的第1个`IDE`设备。
   >
   > 如果*`file`*文件的文件名中包含有英文逗号（`","`），则在书写`file`时应该使用两个逗号（因为逗号是`qemu`命令行中的特殊间隔符，例如用于`"-cpu qemu64,+vmx"`这样的选项），如使用`"-hda my,,file"`将`"my,file"`这个文件作为客户机的第1个`IDE`设备

2. `-hdb file`

   > 作为客户机中的第2个`IDE`设备（序号1），在客户机表现为`/dev/hdb`或`/dev/sdb`设备

3. `-hdc file`

   > 作为客户机中的第3个`IDE`设备（序号2），在客户机表现为`/dev/hdc`或`/dev/sdc`设备

4. `-hdd file`

   > 作为客户机中的第4个`IDE`设备（序号3），在客户机表现为`/dev/hdd`或`/dev/sdd`设备

5. `-fda file`

   > 作为客户机中第1个软盘设备（序号0），在客户机中表现为`/dev/fd0`设备。

6. `fdb file`

   > 作为客户机中第2个软盘设备（序号1），在客户机中表现为`/dev/fd1`设备。

7. `-cdrom file`

   > 作为客户机中的光盘`CD-ROM`，在客户机中通常表现为`/dev/cdrom`设备。
   >
   > 也可以将宿主机中的软驱（`/dev/cdrom`）作为`-cdrom`的*`file`*来使用。
   >
   > **注意：**`-cdrom`参数不能和`-hdc`参数同时使用，因为`-cdrom`就是客户机中的第3个 `IDE`设备。
   >
   > 在通过物理光驱中的光盘或磁盘中`ISO`镜像文件安装客户机操作系统时，一般会使用`-cdrom`参数。

8. `-mtdblock file`

   > 作为客户机自带的一个`Flash`存储器（通常说的闪存）。

9. `-sd file`

   > 作为客户机中的`SD`卡（`Secure Digital Card`）。

10. `-pflash file`

    > 作为客户机的并行`Flash`存储器（`Parallel Flash Memory`）。

### 详细配置存储驱动的`-drive `参数

1. `file=file`
2. `if=interface`
3. `bus=bus,unit=unit`
4. `index=index`
5. `media=media`
6. `snapshot=snapshot`
7. `cache=cache`
8. `aio=aio`
9. `format=format`
10. `serial=serial`
11. `addr=addr`
12. `id=name`
13. `readonly=on|off`
14. 
