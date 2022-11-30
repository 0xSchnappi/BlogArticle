# Windows内核实验12——内存延迟分配

## 原理

CPU给进程分配时采用的惰性分配物理内存，只有当你读取或写入该页的数据时，会触发物理内存页异常，此时CPU才会将该页的数据映射到物理内存上。

## 代码

```c++
#include <iostream>
#include <Windows.h>


DWORD g_out = 0;
#pragma section("data_seg",read,write)
__declspec(allocate("data_seg"))    DWORD g_var = 1;

//0x00401040
void __declspec(naked) IdtEntry1()
{
    __asm
    {
        mov eax, g_var
        mov g_out, eax

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
    //printf("g_var: %p\n", g_var);
    go();
    printf("g_out: %p\n", g_out);
    system("pause");
}

```



## 结果

- 加上注释执行

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221021082911.png)

- 去掉注释执行

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221021083316.png)

**结论：**CPU给进程分配时采用的惰性分配物理内存，只有当你读取或写入该页的数据时，会触发物理内存页异常，此时CPU才会将该页的数据映射到物理内存上。

汇编语言读取的时候也会触发也异常，但是由于环境确实，无法处理该异常，导致内存未映射到物理内存上，第一个结果，CPU不认为你要读取或写入该数据，所以CPU未将该页映射到物理内存上；第二个结果先读取以后，CPU就会将该页映射到物理内存中，后面就可以读取到数据。

**小用途：**应用于反调试，当调试器、CE工具查看了该地址以后，结果就为1，否则为0.

## 参考文献

[内存延迟分配](https://www.bilibili.com/video/BV1Rt41127dq/?spm_id_from=333.999.0.0&vd_source=032603e56385a7af6789a8f132f83ad2)