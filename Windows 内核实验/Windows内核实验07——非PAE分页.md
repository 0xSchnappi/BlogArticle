[toc]

# Windows内核实验07——非PAE分页

## 简介

1. 虚拟内存与物理内存的转换
2. Windbg有关的命令的使用

## 系统设置非PAE分页模式

Windows设置非分页，在启动文件中boot.ini设置

```shell
[boot loader]
timeout=30
default=multi(0)disk(0)rdisk(0)partition(1)\WINDOWS
[operating systems]
multi(0)disk(0)rdisk(0)partition(1)\WINDOWS="Microsoft Windows XP Professional" /noexecute=optin /fastdetect/debug /debugport=com_1 baudrate=115200

```

> 将/noexecute=optin改为/execute=optin

## 代码实现

```c++
#include <iostream>
#include <Windows.h>

int g_num = 0x12345678;
DWORD g_cr3;
//0x00401040
void __declspec(naked) IdtEntry1()
{
    __asm
    {
        mov eax, cr3
        mov g_cr3, eax

        iretd
    }
}

void go()
{
    __asm int 0x20
}

// eq 8003f500 0040ee0000081040
int main()
{
    if ((DWORD)IdtEntry1 != 0x401040)
    {
        printf("IdtEntry1 addr: %p\n", IdtEntry1);
        exit(-1);
    }
    go();
    printf("addr: %p\n", &g_num);
    printf("CR3: %p\n", g_cr3);
    system("pause");
}
```

> 获取cr3寄存器的值，获取g_num全局变量的虚拟地址，然后计算并验证

## 实验结果与分析

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221005213817.png)

```shell
kd> !process 0 0
**** NT ACTIVE PROCESS DUMP ****
PROCESS 81b35a78  SessionId: 0  Cid: 0728    Peb: 7ffd9000  ParentCid: 062c
    DirBase: 1b19f000  ObjectTable: e1b451a8  HandleCount:  15.
    Image: IdtEntry.exe
```

> DirBase: 1b19f000值就是这个进程的cr3值

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221005220939.png)

```shell
kd> .formats 004197b0
Evaluate expression:
  Hex:     004197b0
  Decimal: 4298672
  Octal:   00020313660
  Binary:  00000000 01000001 10010111 10110000
  Chars:   .A..
  Time:    Fri Feb 20 02:04:32 1970
  Float:   low 6.02372e-039 high 0
  Double:  2.12383e-317
分解：
0000000001		1		pdi
0000011001		19h		pti
011110110000	7B0h	offset
```

```shell
kd> !dd 1b19f000 + 1*4
#1b19f004 1afdd067 00000000 00000000 00000000
kd> !dd 1afdd000 + 19*4
#1afdd064 1b084067 1b1ce067 1b162025 00000000
kd> !dd 1b084000 + 7B0
#1b0847b0 12345678 00000000 00000000 00000000
```

> 后三位都为属性值。
>
> PDE = CR3 + pdi * 4
>
> PTE = PDE(高20位) + pti * 4
>
> Pyscial Address = PTE(高20位) + offset

## Windbg有关命令使用

- !dd

  - !dd是读取物理内存
  - dd是读取虚拟内存

  其他db、dq、eb等这些命令类似

- !pte


  显示指定地址的页表项 (PTE) 和页目录项 (PDE)。

  ```shell
  !pte VirtualAddress 
  !pte PTE 
  !pte LiteralAddress 1 
  
  kd> !pte 801544f4
  801544F4  - PDE at C0300800        PTE at C0200550		// PDE和PTE虚拟地址
            contains 0003B163      contains 00154121		// PDE和PTE内容
          pfn 3b G-DA--KWV    pfn 154 G--A--KRV			// 将上一行的内容按照高20位和低12位分解为PFN（Page Frame Number）和页属性
  ```

> PFN用于转换物理地址，规则是先将其（PFN）乘以0x1000（页大小，也就是左移十二位），然后加上虚拟地址的页内偏移，即后12位。因此以上的物理地址为：
>
> 154 * 0x1000 + 4F4 = 1544F4
>
> 分别使用!dd和dd查看1544F4和801544f4，可以看到它们的内容是一致的。
>
> 页属性：
>
> - G代表全局(global)
>
> - D代表数据
> - A代表访问过(Accessed)
> - K代表这是内核态拥有的内存页
> - W代表可以写
> - E代表可以执行
> - V代表有效(Vaild)

- .formats

  以不同的格式显示数字

  ```shell
  0:000> .formats 1c407e62
  Evaluate expression:
    Hex:     1c407e62
    Decimal: 473988706
    Octal:   03420077142
    Binary:  00011100 01000000 01111110 01100010
    Chars:   .@~b
    Time:    Mon Jan 07 15:31:46 1985
    Float:   low 6.36908e-022 high 0
    Double:  2.34182e-315 
  ```

- .process

  - /i  让cpu进行线程调度，运行到指定线程时使用断点断下来，交给调试器调试。此时执行dd、!pte命令才是最准确的。侵入式调试，执行完这个命令必须执行g命令。
  
- !vtop

  - 虚拟地址转换为相应的物理地址，并显示其他页表和页目录信息
  
  - ```shell
    !vtop PFN VirtualAddress
    ```


## 参考资料

[软件调试----张银奎](http://advdbg.org/)

[windows内核实验14_非PAE分页--周壑](https://www.bilibili.com/video/BV18t41127Ab/?spm_id_from=333.999.0.0&vd_source=032603e56385a7af6789a8f132f83ad2)
