[toc]

# Windows内核实验09——零地址读写

## 空指针赋值区

1. 空指针是程序无论在何时都没有物理存储器与之对应的地址。为了保障“无论何时”这个条件，需要人为划分一个空指针的区域，固有上面NULL指针分区。

2. 对于在32位`x86`计算机上运行的`windows xp `来说，就是从`0x00000000`到`0x0000ffff`。为什么分配如此大的空间？而在定义NULL的时候，只使用了 `0x00000000`这么一个值，这不是浪费吗？我想，这是操作系统地址空间的分配粒度相关的，`windows xp sp2`的分配粒度是`64KB`，为了达到对齐，空间地址需要从`0x00010000`开始分配，故空指针的区间范围有那么大。

   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221019210619.png)

## 过程

- 申请一个全局可读写变量（为了获取可读写空间的`PTE`值）
- 将零地址的`PTE`修改为可读写内存的`PTE`值
- 然后修改零地址内存空间

## 代码

```c++
#include <iostream>
#include <Windows.h>


#define PTE(x) ((DWORD*)(0xC0000000 + (( x >> 12) << 3)))
#define PDE(x) ((DWORD*)(0xC0600000 + (( x >> 21) << 3)))


//0x4197b0
DWORD g_var = 0x12345678;
DWORD g_out;

//0x00401040
void __declspec(naked) IdtEntry1()
{

    PTE(0)[0] = PTE(0x4197b0)[0];
    PTE(0)[1] = PTE(0x4197b0)[1];
    g_out = *(DWORD*)0x7b0;
    *(DWORD*)0x7b0 = 0xaaaaaaaa;

    __asm
    {
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
    printf("IdtEntry1 addr: %p\n", IdtEntry1);
    printf("var addr: %p\n", &g_var);
    system("pause");
    go();

    printf("var: %p\n", g_var);
    printf("out: %p\n", g_out);
    printf("var: %p\n", *(DWORD*)(0x4197b0));

    system("pause");
}
```

> 

## 结果

1. 任何内存都是通过的权限都是通过`PTE`、`PDE`，两者的区别是`PTE`的粒度比`PDE`小很多，所以经常使用`PTE`修改内存权限。

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221019210425.jpg)

```shell
# 获取进程信息
Failed to get VadRoot
PROCESS 81ec6020  SessionId: 0  Cid: 0120    Peb: 7ffd3000  ParentCid: 0620
    DirBase: 0a680320  ObjectTable: e2429d28  HandleCount:  17.
    Image: IdtEntry.exe

kd> .process /i 81ec6020  
You need to continue execution (press 'g' <enter>) for the context
to be switched. When the debugger breaks in again, you will be in
the new process context.
kd> g
Break instruction exception - code 80000003 (first chance)
nt!RtlpBreakWithStatusInstruction:
80528bdc cc              int     3


# 代码执行前查看 零地址和变量地址的PTE值和物理地址
kd> !pte 0
                    VA 00000000
PDE at C0600000            PTE at C0000000
contains 0000000018029067  contains 0000000000000000
pfn 18029     ---DA--UWEV  not valid


kd> !pte 4197b0
                    VA 004197b0
PDE at C0600010            PTE at C00020C8
contains 0000000017C63067  contains 8000000018034067
pfn 17c63     ---DA--UWEV  pfn 18034     ---DA--UW-V

kd> !vtop 0a680320   0
X86VtoP: Virt 0000000000000000, pagedir 000000000a680320
X86VtoP: PAE PDPE 000000000a680320 - 0000000017f20001
X86VtoP: PAE PDE 0000000017f20000 - 0000000018029067
X86VtoP: PAE PTE 0000000018029000 - 0000000000000000
X86VtoP: PAE zero PTE
Virtual address 0 translation fails, error 0xD0000147.
kd> !vtop 0a680320   4197b0
X86VtoP: Virt 00000000004197b0, pagedir 000000000a680320
X86VtoP: PAE PDPE 000000000a680320 - 0000000017f20001
X86VtoP: PAE PDE 0000000017f20010 - 0000000017c63067
X86VtoP: PAE PTE 0000000017c630c8 - 8000000018034067
X86VtoP: PAE Mapped phys 00000000180347b0
Virtual address 4197b0 translates to physical address 180347b0.


# 代码执行后查看 零地址和变量地址的PTE值和物理地址

kd> .process /i 81ec6020  
You need to continue execution (press 'g' <enter>) for the context
to be switched. When the debugger breaks in again, you will be in
the new process context.
kd> g
Break instruction exception - code 80000003 (first chance)
nt!RtlpBreakWithStatusInstruction:
80528bdc cc              int     3
kd> !pte 0
                    VA 00000000
PDE at C0600000            PTE at C0000000
contains 0000000018029067  contains 8000000018034067
pfn 18029     ---DA--UWEV  pfn 18034     ---DA--UW-V

kd> !pte 4197b0
                    VA 004197b0
PDE at C0600010            PTE at C00020C8
contains 0000000017C63067  contains 8000000018034067
pfn 17c63     ---DA--UWEV  pfn 18034     ---DA--UW-V

kd> !vtop 0a680320   0
X86VtoP: Virt 0000000000000000, pagedir 000000000a680320
X86VtoP: PAE PDPE 000000000a680320 - 0000000017f20001
X86VtoP: PAE PDE 0000000017f20000 - 0000000018029067
X86VtoP: PAE PTE 0000000018029000 - 8000000018034067
X86VtoP: PAE Mapped phys 0000000018034000
Virtual address 0 translates to physical address 18034000.
kd> !vtop 0a680320   4197b0
X86VtoP: Virt 00000000004197b0, pagedir 000000000a680320
X86VtoP: PAE PDPE 000000000a680320 - 0000000017f20001
X86VtoP: PAE PDE 0000000017f20010 - 0000000017c63067
X86VtoP: PAE PTE 0000000017c630c8 - 8000000018034067
X86VtoP: PAE Mapped phys 00000000180347b0
Virtual address 4197b0 translates to physical address 180347b0.

```

> 虚拟地址转换物理地址是通过PDE和PTE以及偏移，把零地址的PTE修改为变量的PTE，相当于零地址和变量共享同一块PTE大小的物理内存

## 参考资料

[零地址读写](https://www.bilibili.com/video/BV14t41127mZ/?spm_id_from=333.999.0.0&vd_source=032603e56385a7af6789a8f132f83ad2)

[空指针赋值分区](https://blog.csdn.net/liuxiaomao1988/article/details/23036253)
