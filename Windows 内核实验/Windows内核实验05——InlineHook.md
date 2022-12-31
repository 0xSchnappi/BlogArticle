[toc]

# Windows内核实验05——InlineHook

## InlineHook 基本原理

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/image-20221002173341019.png)

> InlineHook:就是对函数前五个字节码或七个字节码改成一个jmp语句，jmp跳转到Hook处理函数处，执行完Hook处理函数然后Jmp到原函数处执行，或者直接退出。
>
> 本实验的思想就是把ExAllocatePool函数Hook了，然后打印Hook ExAllocatePool Sucess！字符串，然后接着执行函数体。

## 代码实现

```c++

#include <iostream>
#include <Windows.h>

typedef DWORD(*DBG_PRINT)(char* Format, ...);
DBG_PRINT DbgPrint = (DBG_PRINT)0x80528e62;
char* pExAllocatePoolHook;
char* pExAllocatePool;
char ExAllocatePoolHookBinary[] = { 0x50, // push    eax
                            0x68, 0x23, 0xf5, 0x03, 0x80 , // push    8003f523
                            0xb8, 0x62, 0x8e, 0x52, 0x80 , // mov     eax,offset nt!DbgPrint (80528e62)
                            0xff, 0xd0 , // call    eax 
                            0x83, 0xc4, 0x04, // add     esp,4
                            0x58, // pop eax
                            0x8B, 0xFF, 0x55, 0x8B, 0xEC, // mov     ecx,23h
                            0xe9, 0x2E, 0x50, 0x4f, 0x00, // jmp     nt!ExAllocatePool+0x5 (80534551)
                            0x48, 0x6f, 0x6f, 0x6b, 0x20, 
                            0x45, 0x78, 0x41, 0x6c, 0x6c, 
                            0x6f, 0x63, 0x61, 0x74, 0x65, 
                            0x50, 0x6f, 0x6f,0x6c, 0x20, 
                            0x53, 0x75, 0x63, 0x65, 0x73, 
                            0x73, 0x21, 0x0a
                            };
char JmpExAllocatePoolHook[] = { 0xe9, 0xB7, 0xAF, 0xB0, 0xFF };

//0x00401040
void __declspec(naked) IdtEntry1()
{
    // 关闭写保护x86

    __asm
    {
        cli;//将处理器标志寄存器的中断标志位清0，不允许中断
        mov eax, cr0
        and eax, not 0x10000
        mov cr0, eax
    }

    // 将ExAllocatePoolHook函数写到0x8003f508
    pExAllocatePoolHook = (char*)0x8003f508;
    for (size_t i = 0; i < 55; i++)
    {

        *pExAllocatePoolHook = ((char*)ExAllocatePoolHookBinary)[i];
        pExAllocatePoolHook++;
    }

    // 修改ExAllocatePool开头5字节
    pExAllocatePool = (char*)0x8053454C;
    for (size_t i = 0; i < 5; i++)
    {
        *pExAllocatePool = JmpExAllocatePoolHook[i];
        pExAllocatePool++;
    }

    // 开启写保护x86
    __asm
    {
        mov eax, cr0
        or eax, 0x10000
        mov cr0, eax
        sti;//将处理器标志寄存器的中断标志置1，允许中断
    }
}

//void __declspec(naked) ExAllocatePoolHook()
//{
//    DbgPrint(HookInfo);
//}

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
> 程序主要功能是通过int 20 中断获取内核权限,对ExAllocatePool函数进行Hook,Hook处理函数为ExAllocatePoolHookBinary,它的C语言版为ExAllocatePoolHook这个函数;JmpExAllocatePoolHook为ExAllocatePool函数前五字节跳转到Hook处理函数的机器码.
>
> Hook处理函数的地址为IDT表的空闲空间,由于该空间的权限不可写入,汇编代码为关闭CPU写保护.


```c++
#include <iostream>
#include <Windows.h>

typedef DWORD(__stdcall* Ex_ALLOCATE)(DWORD PoolType, DWORD NumberOfBytes);
Ex_ALLOCATE ExAllocatePool = (Ex_ALLOCATE)0x8053454C;
DWORD g_pool;
typedef DWORD(*DBG_PRINT)(PCSTR Format, ...);
DBG_PRINT DbgPrint = (DBG_PRINT)0x80528e62;
char str[] = "Call ExAllocatePool";
//0x00401040
void __declspec(naked) IdtEntry1()
{
    __asm
    {
        push 0x30
        pop fs
        sti
    }
    
    g_pool = ExAllocatePool(0, 4096);
    DbgPrint(str);
    __asm
    {
        push 0x3B
        pop fs
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
    printf("%p\n", g_pool);
    system("pause");
}
```

> 该函数调用了ExAllocatePool函数,用于触发Hook,属于验证程序.

## 总结

1. Inline Hook 地址问题

   > Inline Hook 的地址跳转问题，比如要Hook的函数Func地址在0x00400000处，处理Hook函数FuncHook的地址在0x00400010处，那么我们有两种方式跳转(修改函数Func入口处的机器码)，前者直接、字节数少，但是地址计算容易出错，后者需要利用寄存器，但是不容易出错,。
   >
   > ```assembly
   > # 方式一：
   > jmp (0x00400010-(0x00400000 + 5))
   > # 方式二：
   > mov eax, 0x00400010
   > jmp eax
   > # 方式三；
   > push 0x00400010
   > ret
   > ```
   >
   > - 对于第三种方式利用的是，esp指针指向返回地址。

   
