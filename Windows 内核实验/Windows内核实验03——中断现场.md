[toc]

# Windows内核实验03——中断现场

## 寄存器变化

### demo

```c++
#include <iostream>
#include <Windows.h>

DWORD g_eax[2], g_ebx[2], g_ecx[2], g_edx[2], g_esp[2], g_ebp[2], g_esi[2], g_edi[2];
WORD g_cs[2], g_ds[2], g_ss[2], g_es[2], g_fs[2], g_gs[2];

//0x00401040
void __declspec(naked) IdtEntry1()
{
    __asm 
    {
        mov [g_eax + 4], eax
        mov [g_ecx + 4], ecx
        mov [g_edx + 4], edx
        mov [g_ebx + 4], ebx
        mov [g_esp + 4], esp
        mov [g_ebp + 4], ebp
        mov [g_esi + 4], esi
        mov [g_edi + 4], edi

        push eax
        mov ax, cs
        mov[g_cs + 2], ax
        mov ax, ds
        mov[g_ds + 2], ax
        mov ax, ss
        mov[g_ss + 2], ax
        mov ax, es
        mov[g_es + 2], ax
        mov ax, fs
        mov[g_fs + 2], ax
        mov ax, gs
        mov[g_gs + 2], ax

        pop eax

        iretd
    }
}

void go()
{
    __asm
    {
        mov [g_eax], eax
        mov [g_ecx], ecx
        mov [g_edx], edx
        mov [g_ebx], ebx
        mov [g_esp], esp
        mov [g_ebp], ebp
        mov [g_esi], esi
        mov [g_edi], edi

        push eax

        mov ax, cs
        mov [g_cs], ax
        mov ax, ds
        mov [g_ds], ax
        mov ax, ss
        mov [g_ss], ax
        mov ax, es
        mov [g_es], ax
        mov ax, fs
        mov [g_fs], ax
        mov ax, gs
        mov [g_gs], ax

        pop eax
    }
    __asm int 0x20
}

int main()
{
    //if ((DWORD)IdtEntry1 != 0x401040 || (DWORD)IdtEntry2 != 0x401050)
    if ((DWORD)IdtEntry1 != 0x401040)
    {
        //printf("IdtEntry1 addr: %p\nIdtEntry2 addr: %p", IdtEntry1, IdtEntry2);
        printf("IdtEntry1 addr: %p\n", IdtEntry1);
        exit(-1);
    }
    go();
    printf("before: eax: %p,\tecx: %p\tedx: %p\tebx: %p\n", g_eax[0], g_ecx[0], g_edx[0], g_ebx[0]);
    printf("after: eax: %p,\tecx: %p\tedx: %p\tebx: %p\n", g_eax[1], g_ecx[1], g_edx[1], g_ebx[1]);
    printf("before: esp: %p,\tebp: %p\tesi: %p\tedi: %p\n", g_esp[0], g_ebp[0], g_esi[0], g_edi[0]);
    printf("after: esp: %p,\tebp: %p\tesi: %p\tedi: %p\n", g_esp[1], g_ebp[1], g_esi[1], g_edi[1]);
    printf("before: cs: %p\tss: %p\tes:%p\tfs: %p\tgs: %p\n", g_cs[0], g_ss[0], g_es[0], g_fs[0], g_gs[0]);
    printf("after: cs: %p\tss: %p\tes:%p\tfs: %p\tgs: %p\n", g_cs[1], g_ss[1], g_es[1], g_fs[1], g_gs[1]);
    system("pause");
}
```

```shell
eq 8003f500 0040ee0000081040
```

### 实验结果

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220918173603.png)

> 发生变化的分别是esp、cs、ss寄存器

### 总结

#### cs段寄存器

在x86保护模式下，段的信息（段基线性地址、长度、权限等）即**段描述符**占8个字节，段信息无法直接存放在段寄存器中（段寄存器只有2字节）。Intel的设计是段描述符集中存放在GDT(Global Descriptor Table)或LDT(Local Descriptor Table)中，分别保存在新增的寄存器GDTR和LDTR中。而**段寄存器**CS DS SS ES**存放的是段描述符在GDT或LDT内的索引值**(index)。

段选择子是从段描述符中获取如下图所示：

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220918220631.png)

> 开始设置eq 8003f500 0040ee0000081040，设置第0x20个中断描述符为0040ee00 0008 1040，
>
> 由上图对照可得，由于0x20所触发的中断段选择子为0008，零环时cs段寄存器的值为08

 段选择子结构简单，它是一个16位的描述符，指向了定义该段的段描述符。段选择子结构如下图所示：

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220918211102.png)

  它的成员解释如下：

- RPL：请求特权级别，通俗的讲我用什么权限来请求。
- TI：TI=0时，查GDT表；TI=1时，查LDT表。
- Index：处理器将索引值乘以8在加上GDT或者LDT的基地址，就是要加载的段描述符。

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220918212010.png)

> cs(代码段寄存器Code Segment):
>
> 三环时cs寄存器为1B(00011 0 11) RPL = 3 GDT Index = 3
>
> 零环时cs寄存器为08(00001 0 00) RPL = 0 GDT Index = 1

- 系统中断进入内核流程

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220919094101.png)

#### SS段寄存器和ESP栈针寄存器

  为了有效地实现保护，同一个任务在不同的特权级下使用不同的堆栈。例如，当从外层特权级3变换到内层特权级0时，任务使用的堆栈也同时从3级变换到0级堆栈；当从内层特权级0变换到外层特权级3时，任务使用的堆栈也同时从0级堆栈变换到3级堆栈。所以当我们进入到内核的时候TSS会自动在表里查找对应的段选择子和ESP值，形成了内核堆栈指针的切换

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220919213925.png)

  Windows只使用了TSS的SS0和ESP0，用于权限切换。
  TSS这个东西是Intel设计出来做任务切换的，windows和linux都没有使用任务，而是自己实现了线程。在windows中，TSS唯一的作用就是权限切换时要用到SS0和ESP0，又或者这样理解，TSS就是用来一次性替换一堆寄存器的。

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220920100551.png)

> 28 = 00101 0 00
>
> index = 5 查询GDT表 0环权限

## 参考文献

[段描述符与段选择子](https://www.cnblogs.com/wingsummer/p/15312627.html)

[中断处理之TSS](https://blog.csdn.net/m0_37329910/article/details/89944946)

[TSS，TR寄存器，TSS描述符，任务段跳转实验](https://blog.csdn.net/Kwansy/article/details/108890586)
