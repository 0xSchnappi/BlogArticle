[toc]

# x64内核研究5——硬件漏洞补丁和CFG

## 关键字

- Meltdown（熔断）

- Spectre（幽灵）

- side-channel attack（侧信道攻击）

- Rogue Data Cache Load（恶意数据缓存加载）

- Speculative Execution（预测执行）

- Control Flow Guard（控制流）
  
  > [Control Flow Guard - Win32 apps | Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/secbp/control-flow-guard)

## Meltdown and Spectre

> 漏洞形成的主要原因是CPU的推测执行。
> 
> ```cpp
> ......                                // 0
> int x = 0;
> int y = 1;
> int z = 2;
> char arr[5] = {0};
> int exp;
> ......                                // 1
> if (x + y + z > 0)                    // 2
> {
>     printf("total is position");      // 3
>     exp = arr[pointer];               // exp下标越界读取敏感信息
> 
> }
> else
> {
>     printf("total is negative");      // 4
> }
> ```
> 
> CPU的推测执行技术的发展原因在于CPU处理数据的时间远远快于从内存读取数据的时间，最后就有了高速缓冲存储器Cache（L1、L2、L3）。
> 
> 下面就通过这段C代码介绍CPU推测执行优势以及漏洞产生的原因
> 
> - CPU推测执行
>   
>   > 由于CPU读取速度远远快于内存，导致CPU总是处于等待内存数据的状态，CPU厂商为了解决这一问题，就推出了CPU推测执行的功能。
>   > 
>   > 具体实现：
>   > 
>   > 如上代码定义了三个变量x、y、z，在位置1处对这三变量进行大量的运算，然后在位置2处要对这三个变量的值进行判断 。此时需要从内存中取出这三个变量进行判断来确定CPU该执行if里面还是else里面的语句。
>   > 
>   > 1. CPU没有推测执行功能。CPU就在位置2处等待从内存取出三个变量，CPU处于等待状态，内存读取数据特别慢，等待CPU拿到这三个变量的值后进行运算以后确定执行哪里就去执行哪里。
>   > 
>   > 2. CPU有推测执行功能。CPU在位置2处不会等待从内存读取数据，它会推测执行if语句内的内容，但是此时寄存器的状态保存了在位置2处的状态，但是CPU已经开始执行3处的代码，当CPU拿到从内存返回的数据时。CPU会计算if条件是否为真，如果为真CPU会接着推测执行继续执行；如果为假，CPU会回滚（CPU推测执行不能直接覆盖寄存器的值，改变程序在位置2处的状态，方便推测执行错误回滚）到位置2处的状态，接着执行else（位置4）里的语句。
> 
> - 漏洞利用
>   
>   > Cache Memory：当CPU尝试查询内存中的数据，我们在缓存中会备份一份，下次CPU需要时，直接在缓存中读取。
>   > 
>   > 漏洞产生的原因是，在推测执行位置3处的代码时，通常情况下执行exp代码，CPU会抛出异常，但是CPU为了提高执行效率，在位置2处不等待读取内存x、y、z返回直接预先执行位置3处的代码和exp，CPU会读取非法越界数组的数据，CPU认为kernel会验证数组越界，如果越界则会强制结束程序，当程序预先执行exp后，arr[pointer]位置的敏感数据已经在Cache（arr[pointer] = 4）中备份了一份，当CPU发现预测执行错误时，就算CPU发生回滚，但是Cache不会发生回滚。 
>   > 
>   > 侧信道攻击的方式就是基于时间的攻击，ABCDEFG分别代表敏感信息的key，它们会利用这个key取访问Value值，访问的过程中发现，访问C的时间短，那么Key=C时Value的值为4，因为arr[pointer] = 4在先前访问的时候在Cache中备份了一份，读取时需要的时间短。
>   > 
>   > 

## KiBreakpointTrapShadow

```c++
__int64 KiBreakpointTrapShadow()
{
  unsigned __int64 v0; // rsi
  char v4; // [rsp-20h] [rbp-20h]

  if ( (v4 & 1) != 0 )
  {
    __asm { swapgs }
    v0 = KeGetPcr()->Prcb.KernelDirectoryTableBase;
    if ( !_bittest(MK_FP(__GS__, 0x7018i64), 1u) )// gs[7018] _KPCR.Prcb.ShadowFlags 第1位为0 为普通权限进程 切换CR3
      __writecr3(v0);                           // 将内核CR3写入KernelDirectoryTableBase
  }
  return KiBreakpointTrap();
}


```

> 先执行swapgs，进行cr3切换（IA32_GS_BASE和IA32_KERNEL_GS_BASE交换）
>
> 会将PCB.DirectoryTableBase写入PRCB.KernelDirectoryTableBase，也就是前面看到的GS[0x7000]位置；并会依据KPROCESS->AddressPolicy来设置ShadowFlags（GS[0x7018]）, KPROCESS->AddressPolicy在进程创建时依据进程是否由管理员身份启动而设置（NtCreateProcess->PspAllocateThread->PspUserThreadStartup->PspDisablePrimaryTokenExchange->SeTokenIsAdmin/SecureHandle->Process->Pcb.AddressPolicy = 1），如果是管理员进程，则KPROCESS->AddressPolicy为1，ShadowFlags会被设置为2，若是普通进程，则ShadowFlags为1。 在中断发生时，会依据ShadowFlags判断是否要切换CR3到PCB.DirectoryTableBase。PCB.DirectoryTableBase中映射了内核内存，而PCB.UserDirectoryTableBase没有映射内核内存，而非特权级应用程序在三环中使用的时UserDirectoryTableBase，只有在中断时才会被切换到DirectoryTableBase从而达到内核页表隔离的目的。

## lfence

> Specifically, LFENCE does not execute until all prior（先前的，较早的） instructions have completed locally, and no later instruction begins execution until LFENCE inparticular completes. 
>
> Instructions following an LFENCE may be fetched（取） from memory before the LFENCE, but they will not execute (even speculatively) （推测执行）until the LFENCE completes.

```assembly
.text:000000014004A86E                 jz      loc_14017CF15
.text:000000014004A874                 movzx   ecx, word ptr [rbx+4]
.text:000000014004A878                 mov     eax, cs:KeNumberProcessors_0
.text:000000014004A87E                 cmp     ecx, eax
.text:000000014004A880                 jnb     loc_14017CF23
.text:000000014004A886                 lfence
.text:000000014004A889                 lea     r9, KiProcessorBlock
.text:000000014004A890                 mov     eax, ecx
.text:000000014004A892                 mov     r9, [r9+rcx*8]
```

> lfence会存在Jcc后面，目的就是为了阻止推测执行，只有执行完lfence指令前的所有指令，才能执行lfence后面的指令

## Control Flow Guard （控制流防护）

### 开启方式

- 编译选项

  1. vs编译器[编译选项设置](https://learn.microsoft.com/en-us/windows/win32/secbp/control-flow-guard)

  2. 编译选项不兼容

     ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20230103200204.png)

     ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20230103200320.png)

     > 将调试信息格式设置为无

- dumpbin检查

  ```shell
  dumpbin /headers /loadconfig CFGtest.exe
  ```

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/image-20230103194207530.png)

  > #####  DLL Characteristics
  >
  > The following values are defined for the DllCharacteristics field of the optional header.
  >
  > | Constant                          | Value  | Description                        |
  > | --------------------------------- | ------ | ---------------------------------- |
  > | IMAGE_DLLCHARACTERISTICS_GUARD_CF | 0x4000 | Image supports Control Flow Guard. |

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/image-20230103195415934.png)

  > - Guard CF address of check-function pointer：_guard_check_icall_fptr的地址，在调试的时候可以发现它其实是指向ntdll!LdrpValidateUserCallTarget。
  > - Guard CF address of dispatch-function pointer：在VS2015编译出来上是个保留字段，直译是保护调度函数指针，在IDA中可看到代码就一句 jmp rax 。
  > -  Guard CF function table： RVA列表的指针，其包含了程序的代码。每个函数的RVA将转化为 CFGBitmap中的“1”位。CFGBitmap 的位信息来自Guard CF function table。
  > -  Guard CF function count： RVA的个数。

- IDA查看

  - 未开启CFG

    ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/image-20230103201755517.png)

    > 未开启CFG时，直接调用函数指针，调用函数。

  - 开启CFG

    ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/image-20230103202021533.png)

    > 开启CFG后，在调用函数指针时，
    >
    > 1. 将函数指针作为`__guard_dispatch_icall_fptr`函数的参数，
    > 2. 调用`__guard_dispatch_icall_fptr`函数进行地址合法行检查
    > 3. 调用`j___RTC_CheckEsp`函数，对函数栈进行检查
    > 4. 最后才是通过函数指针调用函数

### 代码

```c++
#include <iostream>

typedef int(*fun_t)(int);

int foo(int a)
{
    printf("hellow world %d\n", a);
    return a;
}
class CTargetObject
{
public:
    fun_t fun;
};
int main()
{
    int i = 0;
    CTargetObject* o_array = new CTargetObject[5];
    for (i = 0; i < 5; i++)
        o_array[i].fun = foo;
    o_array[0].fun(1);
    return 0;
}
```

> 通过函数指针调用函数，然后通过反汇编可执行文件查看开启CFG前后的区别。

### 原理

> 简单的总结一下，相当于对用户层的函数做了一个函数地址表，当你使用函数指针时就会通过地址翻译去在这个表里去校验这个指针，如果没有找到该指针对应的地址，则判定为无效，如果能找到，则为有效。

### 动态调试

![image-20230106094700775](C:\Users\hantong\AppData\Roaming\Typora\typora-user-images\image-20230106094700775.png)

![image-20230106094755183](C:\Users\hantong\AppData\Roaming\Typora\typora-user-images\image-20230106094755183.png)

```assembly
0:000> r ecx
ecx=00f41360
0:000> u 00f41360
CFGtest!ILT+848(?fooYAHHZ):
00f41360 e90b0f0000      jmp     CFGtest!foo (00f42270)
00f41365 cc              int     3

Evaluate expression:
  Hex:     00f41360
  Decimal: 15995744
  Octal:   00075011540
  Binary:  00000000 11110100 00010011 01100000
  Chars:   ...`
  Time:    Sun Jul  5 11:15:44 1970
  Float:   low 2.24148e-038 high 0
  Double:  7.90295e-317
  
ntdll!LdrpValidateUserCallTarget:
77c189f0 8b150093cb77    mov     edx,dword ptr [ntdll!LdrSystemDllInitBlock+0xb8 (77cb9300)]
77c189f6 8bc1            mov     eax,ecx
77c189f8 c1e808          shr     eax,8
0:000> r edx
edx=00f60000
0:000> r eax
eax=0000f413
;CFG bitmap 基址 ntdll!LdrSystemDllInitBlock+0xb8 (77cb9300)
;取地址的高3字节通过CFG bitmap 基址进行获取校验值
ntdll!LdrpValidateUserCallTargetBitMapCheck:
77c189fb 8b1482          mov     edx,dword ptr [edx+eax*4]
0:000> r edx
edx=00041040

77c189fe 8bc1            mov     eax,ecx
77c18a00 c1e803          shr     eax,3
0:000> r eax
eax=001e826c
0:000> .formats 001e826c
Evaluate expression:
  Hex:     001e826c
  Decimal: 1999468
  Octal:   00007501154
  Binary:  00000000 00011110 10000010 01101100
  Chars:   ...l
  Time:    Sat Jan 24 11:24:28 1970
  Float:   low 2.80185e-039 high 0
  Double:  9.87868e-318
0:000> .formats 00041040

77c18a03 f6c10f          test    cl,0Fh
0:000> r cl
cl=60

77c18a06 7506            jne     ntdll!LdrpValidateUserCallTargetBitMapRet+0x1 (77c18a0e)
77c18a08 0fa3c2          bt      edx,eax
77c18a0b 730a            jae     ntdll!LdrpValidateUserCallTargetBitMapRet+0xa (77c18a17)
ntdll!LdrpValidateUserCallTargetBitMapRet:
77c18a0d c3              ret


Evaluate expression:
  Hex:     00041040
  Decimal: 266304
  Octal:   00001010100
  Binary:  00000000 00000100 00010000 01000000
  Chars:   ...@
  Time:    Sun Jan  4 09:58:24 1970
  Float:   low 3.73171e-040 high 0
  Double:  1.31572e-318

```

> 

### retpoline

> 幽灵漏洞补丁
