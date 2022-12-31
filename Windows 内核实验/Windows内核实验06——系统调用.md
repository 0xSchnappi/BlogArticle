[toc]

# Windows内核实验06——系统调用

## 使用INT 2E切换到内核模式

[软件调试----张银奎](http://advdbg.org/)

- NtDll.dll中的NtReadFile()函数非常简短，首先将ReadFile()对应的系统服务号（0xa1，与版本有关）放入EAX寄存器中，讲参数指针放入EDX寄存器中，然后便通过INT n指令发出调用。（每个服务号是唯一的，但是微软未公开，每个服务号不能保证在不同版本的Windows版本中保持一致。）

  ```assembly
  ntdll!NtReadFile:	// Windows 2000
  mov eax,0xa1
  lea edx, [esp+4]
  int 2e
  ret 0x24
  ```

- IDT 2e向量号对应的服务例程是KiSystemService()，KiSystemService()是内核态中专门用来分发系统调用的例程。

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221005164736.png)

- Windows 将2e号向量专门用于系统调用，在启动早期初始化中断中断描述符表（ Interrupt Descriptor Table , IDT ）时，便注册好了合适的服务例程。因此当 NTDLL. DLL 中的NIReadFilc()发出 INT 2E指令后， CPU 便会通过 IDT 找到 KiSystemService() 函数。因为 KiSystemService() 函数是位于内核空间的，所以 CPU 在执行权交给 KiSystcmService() 函数前，会做好从用户模式切换到内核模式的各种工作，包括：

  1. 权限检查，即检查源位置和目标位置所在的代码段权限，核实是否可以转移；

  2. 准备内核模式使用的栈，为了保证内核安全，所以线程在内核执行时都必须使用位于内核空间的内核栈（ kernel stack） ，内核栈的大小一般为8KB或12KB
     KiSystemService()会根据服务 ID 从系统服务分发( System Service Dispatch Table ）中查找到要调用的服务函数地址和参数描述，然后将参数从用户态栈复制到该线程的内核栈中，最后KiSystemService()调用内核中真正的NtReadFile()函数，执行读文件操作，操作结束后会返回到KiSystemService()，KiSystemService()会将操作结果复制回该线程用户态栈，最后通过IRET指令将执行权交回给NtDll.dll中的NtReadFile()函数（继续执行INT 2E后面的那条指令）。

     通过 INT 2E进行系统调用时，CPU 必须从内存中分别加载门描述符和段描述符才能得到KiSystemService()的地址，即使门描述符和段描述符已经在高速缓存中， CPU 也需要通过“内存读（memory read）”操作从高速缓存中读出这些数据，然后进行权限检查。

- 系统中断后的栈帧

  | 栈帧                                                       |
  | ---------------------------------------------------------- |
  | EIP（三环的当前执行地址）[esp]                             |
  | CS（代码执行权限）[esp+4]                                  |
  | eflags（保存中断时CPU状态）[esp+8]                         |
  | ESP（三环的栈指针）[esp+0xC]                               |
  | SS（三环和零环切换时，保证正确的切换对应的栈帧）[esp+0x10] |


## 代码实现

```c++
#include <iostream>
#include <Windows.h>

DWORD Target[3] = { 0x8003F120,0x8003F1C0,0x8003F200 };
DWORD* ServiceTable = (DWORD*)0x8003F3C0;
void  SystemCallEntry();
void AllocMem();
void ReadMem();

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

    p = (char*)Target[1];
    for (size_t i = 0; i < 128; i++)
    {

        *p = ((char*)ReadMem)[i];
        p++;
    }

    p = (char*)Target[2];
    for (size_t i = 0; i < 128; i++)
    {

        *p = ((char*)AllocMem)[i];
        p++;
    }

    ServiceTable[0] = 0x8003F1C0;
    ServiceTable[1] = 0x8003F200;
    __asm
    {
        // eq 8003f500 8003ee000008f120
        mov eax, 0x0008f120
        mov ds:[0x8003f508], eax
        mov eax, 0x8003ee00
        mov ds:[0x8003f50c], eax

        iretd
    }
}

void __declspec(naked) SystemCallEntry()
{
    __asm
    {
        push 0x30
        pop fs
        sti

        mov ebx, ss:[esp + 0xC]		// 获取三环栈帧顶地址
        mov ecx, ds:[ebx + 4]		// 获取三环参数
        mov ebx, 0x8003F3C0			// 根据服务ID从系统服务分发( System Service Dispatch Table ）
        mov edx, ds:[ebx + eax*4]	// 在这里就是eax的值
        call edx					// 根据服务ID调用对应的函数

        cli
        push 0x3b
        pop fs

        iretd

    }
}

void __declspec(naked) ReadMem()
{
    __asm
    {
        mov eax, ecx	// 将参数复制到eax中进行返回
        ret
    }
}

void __declspec(naked) AllocMem()
{
    __asm 
    {
        push ecx	// ecx参数压栈，调用ExAllocatePool函数
        push 0
        mov eax, 0x8053454C
        call eax
        ret
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
        system("pause");
        exit(-1);
    }
    go();
    system("pause");
}
```

>SystemCallEntry()函数实现的功能就是从三环栈帧中复制函数参数到内核栈帧中，然后分发到对应的处理函数中对参数进行处理，然后将参数返回到函数中。
>
>ReadMem()对传递进来的ecx参数进行处理。

```c++
#include<iostream>
#include<Windows.h>

DWORD ReadMem(DWORD addr);
DWORD AllocMem(DWORD size);

DWORD __declspec(naked) ReadMem(DWORD addr)
{
    __asm
    {
        mov eax, 0
        int 0x21
        ret
    }
    
}

DWORD __declspec(naked) AllocMem(DWORD size)
{
    __asm
    {
        mov eax, 1
        int 0x21
        ret
    }

}

void main()
{
    printf("%p\n", ReadMem(0x8003F3C0));
    printf("%p\n", AllocMem(16));
    system("pause");
}
```

> ReadMem相当于NTDLL.dll中NtReadFile函数，
>
> mov eax，0  就是通过eax传递调用例程
>
> int 0x21 就是触发，查找21号向量的服务例程

## 补充知识点

[RET RETF IRET IRETD 指令的不同](https://blog.csdn.net/qq_50332504/article/details/124145581)

### RET
机器指令：C3

近返回，一般函数调用的返回，call 对应 ret，也是唯一的用途。

- RET 的本质是：从栈顶弹出 EIP (pop EIP)，EIP是返回地

  ```shell
  注意：pop EIP没有这条指令，只是方便理解
  ```

  如果是 RET n 这样的，那么之后还会 ESP + n (后面这种形式就不写了)

### RETF (return far)
机器指令：CB

远返回，call far 对应的 retf，当然分为两种情况

- 相同权限返回：从栈顶弹出 EIP >> CS (先 >> 后)
- 不同权限返回：从栈顶弹出 EIP >> CS >> ESP >> SS

权限是否相同指的是：当前段的特权级别和将要返回的段的特权权限是否相同(CPL和DPL是否相同)

tip:不同权限之间的跳转都是要进行权限检查和各种保护检查

### IRET (interrupt return)
机器指令：CF66

中断返回，int n 对应 iret；任务切换(nested task swith)的 call far 也用 iret 返回

- 这里会用到一个NT位 (在EFLAGS寄存器中)，这个表示是否是嵌套的任务切换 (是否是call命令的任务切换)。这将会影响到返回的方式。
  - NT = 0，从栈顶弹出 EIP >> CS >> EFLAGS >> ESP >> SS （类似于RETF）
  - NT = 1，任务切换返回，使用到TSS表。详情请查看任务段调用及返回

### IRETD
机器指令：CF

中断返回，同iret

- 32位下，IRETD和IRET至少执行结果是一样的，但是硬编码却略有不同
- 本来是专门为32位定制的，但是编译器却允许IRET有32位和16位两种返回方式。
  (32位下，IRET 等价于 IRETD，且 IRET 比 IRETD 更常用)

> 书中原文：
> IRET and IRETD are mnemonics for the same opcode. The IRETD mnemonic (interrupt return double) is intendedfor use when returning from an interrupt when using the 32-bit operand size; however, most assemblers use theIRET mnemonic interchangeably for both operand sizes.

### 参考书籍

```shell
参考 : (可以参考书中的代码)
英特尔2卷 Vol. 2A 3-525				//IRET IRETD
英特尔2卷 Vol. 2B 4-563				//RET RETF
```

