[toc]

# Windows内核实验08——PAE分页

## 概念

PAE(Physical Address Extension)：物理内存扩展，物理地址由32位索引扩充到36位，PDE、PTE由4字节扩充到8字节,引入了PDPTE。

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



## 结果分析

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221006103021.png)

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221006113904.png)

```shell
kd> !process 0 0
**** NT ACTIVE PROCESS DUMP ****
PROCESS 8208ec10  SessionId: 0  Cid: 0218    Peb: 7ffdd000  ParentCid: 0620
    DirBase: 0a980220  ObjectTable: e282c318  HandleCount:  15.
    Image: IdtEntry.exe
    
kd> .formats 004197B0
Evaluate expression:
  Hex:     004197b0
  Decimal: 4298672
  Octal:   00020313660
  Binary:  00000000 01000001 10010111 10110000
  Chars:   .A..
  Time:    Fri Feb 20 02:04:32 1970
  Float:   low 6.02372e-039 high 0
  Double:  2.12383e-317
  
// 2 9 9 12 分页模式
00				0			pdpti
000000010		2			pdi
000011001		19h			pti
011110110000	7B0h		offset
kd> !dq 0a980220
# a980220 00000000`0fc93001 00000000`0f054001
kd> !dq 0fc93000 + 2*8
# fc93010 00000000`0fa5c067 00000000`00000000
kd> !dq 0fa5c000 + 19*8
# fa5c0c8 80000000`10fb3067 80000000`0f0f5067
kd> !db 10fb3000 + 7B0
#10fb37b0 78 56 34 12 00 00 00 00-00 00 00 00 00 00 00 00 xV4.............

// windbg暂停到当前进程
kd> .process /i 8208ec10
You need to continue execution (press 'g' <enter>) for the context
to be switched. When the debugger breaks in again, you will be in
the new process context.
kd> g
Break instruction exception - code 80000003 (first chance)
nt!RtlpBreakWithStatusInstruction:
80528bdc cc              int     3
kd> r cr3
cr3=0a980220
kd> db 004197B0
004197b0  78 56 34 12 00 00 00 00-00 00 00 00 00 00 00 00  xV4.............
kd> !db 10fb3000 + 7B0
#10fb37b0 78 56 34 12 00 00 00 00-00 00 00 00 00 00 00 00 xV4.............

kd> !vtop 0a980220  004197b0
X86VtoP: Virt 00000000004197b0, pagedir 000000000a980220
X86VtoP: PAE PDPE 000000000a980220 - 000000000fc93001
X86VtoP: PAE PDE 000000000fc93010 - 000000000fa5c067
X86VtoP: PAE PTE 000000000fa5c0c8 - 8000000010fb3067
X86VtoP: PAE Mapped phys 0000000010fb37b0
Virtual address 4197b0 translates to physical address 10fb37b0.

kd> ?? 0xc0000000 + ((0x004197B0 >> 12)  <<3)
unsigned int 0xc00020c8
kd> dq 0xc00020c8
c00020c8  80000000`10fb3067 80000000`0f0f5067
c00020d8  80000000`0ec7f025 00000000`00000000
kd> !dq 000000000fa5c0c8 
# fa5c0c8 80000000`10fb3067 80000000`0f0f5067
# fa5c0d8 80000000`0ec7f025 00000000`00000000
```

> 内存的属性由PDE、PTE修改。
>
> va of pte =  0xc0000000 + ((addr >> 12)  <<3)
>
> va of pde = 0xc0600000 + ((addr >> 21)  <<3)
>
> 

## 参考资料

[windows内核实验15_PAE分页--周壑](https://www.bilibili.com/video/BV1Yt41127jr/?spm_id_from=333.999.0.0&vd_source=032603e56385a7af6789a8f132f83ad2)
