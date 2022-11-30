[toc]

# Windows内核实验10——跨进程内存访问

## 原理

- CPU进程切换通过cr3实现
- 获取要访问的进程cr3，然后进行切换，再去读写对应进程
- **注意：**跨进程访问的代码实现必须在公共内存空间，因为cpu切换进对方进程，此时自己的进程已经无法访问·
- **大白话：**就是利用内核公共区域的代码修改指定进程的内存空间

## 代码实现

```c++
#include <iostream>
#include <Windows.h>

DWORD Target[3] = { 0x8003F120,0x8003F1C0,0x8003F200 };
DWORD* ServiceTable = (DWORD*)0x8003F3C0;
void  SystemCallEntry();

char* p;
//0x00401040
void __declspec(naked) IdtEntry1()
{

    p = (char*)Target[0];
    for (size_t i = 0; i < 128; i++)
    {

        *p = ((char*)SystemCallEntry)[i];
        p++;
    }

    __asm
    {

        iretd
    }
}

DWORD g_cr3;
void __declspec(naked) SystemCallEntry()
{
    __asm
    {
        mov eax, cr3
        mov g_cr3, eax

        mov eax ,0x0a4403a0
        mov cr3, eax

        mov eax, 0x00410041
        mov ds:[0xAAE58], eax

        mov eax, g_cr3
        mov cr3, eax

        iretd



    }
}


void go()
{
    __asm int 0x20
}

// eq 8003f500 0040ee0000081040
// eq 8003f500 8003ee000008F120
int main()
{
    if ((DWORD)IdtEntry1 != 0x401040)
    {
        printf("IdtEntry1 addr: %p\n", IdtEntry1);
        system("pause");
        exit(-1);
    }
    go();
    system("pause");
}

```

## 结果

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221020083921.png)

- 找到记事本这个字符串的地址为：0xAAE58

  ```shell
  PROCESS 8183e4a8  SessionId: 0  Cid: 00ec    Peb: 7ffde000  ParentCid: 05e8
      DirBase: 0a4403a0  ObjectTable: e1135d00  HandleCount:  46.
      Image: notepad.exe
  ```

  > 获取到notepad.exe进程的cr3：0a540360

- 将读取进程的代码复制到0x8003F120

  ```shell
  eq 8003f500 0040ee0000081040
  ```

  - 执行程序

- 触发0x20中断，将0x8003F120处的代码得到执行，进而访问notepad.exe进程空间

  ```shell
  eq 8003f500 8003ee000008F120
  ```

  - 再次执行程序

- 修改notepad.exe进程空间成功

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221020092128.png)

- **问题：**点击两次后会出现错误，等待排查中

  ```shell
  watchdog!WdUpdateRecoveryState: Recovery enabled.
  
  *** Fatal System Error: 0x0000007f
                         (0x0000000D,0x00000000,0x00000000,0x00000000)
  
  Break instruction exception - code 80000003 (first chance)
  
  A fatal system error has occurred.
  Debugger entered on first try; Bugcheck callbacks have not been invoked.
  
  A fatal system error has occurred.
  
  nt!RtlpBreakWithStatusInstruction:
  80528bdc cc              int     3
  kd> r idtr
  idtr=8003f400
  kd> !idt 8003f400
  
  Dumping IDT: 8003f400
  
  WARNING: Process directory table base 0A440340 doesn't match CR3 0A4403A0
  WARNING: Process directory table base 0A440340 doesn't match CR3 0A4403A0
  fc879fa98003f400:	00000000 
  
  ```

  [MSDN](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/bug-check-0x7f--unexpected-kernel-mode-trap)
  
  - 0x0000000D - 其他异常未涵盖的异常；与应用程序的访问冲突有关的保护错误
  
  在代码实现中使用g_cr3变量保存cr3寄存器的值，可是g_cr3是当前程序的虚拟地址，当切换到notepad.exe程序时，`mov eax, g_cr3`操作取回的是notepad.exe对应的虚拟地址的值，所以会导致多次执行时出现错误，只需将该变量改为零环可读写的地址即可
  
  ```assembly
  mov eax, cr3
  mov g_cr3, eax
  
  mov eax ,0x0a4403a0
  mov cr3, eax
  
  mov eax, 0x00410041
  mov ds:[0xAAE58], eax
  
  mov eax, g_cr3
  mov cr3, eax
  
  ```
  
  

## 参考文献

[跨进程访问](https://www.bilibili.com/video/BV1dt41127Hu/?spm_id_from=333.999.0.0&vd_source=032603e56385a7af6789a8f132f83ad2)

