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

> lfence会存在与Jcc后面，阻止推测执行

## PspSystemThreadStartup

### _guard_dispatch_icall

```shell
0x9090d0ff
```

### retpoline

> 幽灵漏洞补丁
