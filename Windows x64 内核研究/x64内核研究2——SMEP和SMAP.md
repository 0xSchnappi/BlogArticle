[toc]

# x64内核研究2——SMEP和SMAP

## 简介

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221114202426.png)

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221115205633.png)

For supervisor-mode accesses:

- Data reads from user-mode pages. Access rights depend on the value of CR4.SMAP:  
  - If CR4.SMAP = 0, data may be read from any user-mode address with a protection key for which read access is permitted.
  - If CR4.SMAP = 1, access rights depend on the value of EFLAGS.AC and whether the access is implicit or explicit:
    - If EFLAGS.AC = 1 and the access is explicit, data may be read from any user-mode address with a protection key for which read access is permitted.
- Data writes to user-mode addresses.Access rights depend on the value of CR0.WP:
  -  If CR0.WP = 0, access rights depend on the value of CR4.SMAP:
    - If CR4.SMAP = 0, data may be written to any user-mode address with a protection key for which write access is permitted.
- Instruction fetches from user-mode addresses. Access rights depend on the values of CR4.SMEP:
  - If CR4.SMEP = 1, instructions may not be fetched from any user-mode address.

> SMEP 内核权限执行用户代码空间的代码
>
> SMAP 内核权限读写用户代码空间的代码

## idt 中断

```shell
// ForWindows10.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include <Windows.h>

extern "C" void IntEntry();
extern "C" void go();

extern "C" ULONG64 x;
ULONG64 x;
// int3 0967ee00`0010cdc0 00000000`fffff807
// int3 func addr :  fffff807 0967cdc0
// idtr fffff8021188e000
// IntEntry  4000ee00 0010D7F0 00000000 00000001
// eq fffff8021188e210 4000ee000010D7F0
// eq fffff8021188e218 1
int main()
{
	printf("IntEntry Address : %p\n", IntEntry);
	if ((ULONG64)IntEntry != 0x000000014000D7F0)
	{
		printf("wrong IntEntry at %p\n", IntEntry);
		system("pause");
		exit(-1);
	}

	go();
	std::cout << std::hex << x << "\n";
	system("pause");
}
```

```c++
; x64asm.asm
option casemap:none

EXTERN x:qword
.data
;ttt qword ?
.code

IntEntry	Proc
	mov rax,[0fffff8020f26edc0h]
	db 0fh, 01h, 0cbh	;stac
	mov x, rax
	iretq
IntEntry Endp

go Proc
	int 21h
	ret
go Endp

END
```

```shell
kd> r cr4
cr4=00000000003506f8
kd> .formats 00000000003506f8
Evaluate expression:
  Hex:     00000000`003506f8
  Decimal: 3475192
  Decimal (unsigned) : 3475192
  Octal:   0000000000000015203370
  Binary:  00000000 00000000 00000000 00000000 00000000 00110101 00000110 11111000
  Chars:   .....5..
  Time:    Tue Feb 10 13:19:52 1970
  Float:   low 4.86978e-039 high 0
  Double:  1.71697e-317
```

> 想要运行上述代码cr4的SMEP和SMAP位都置零。否则会产生三重错误，无法蓝屏。

## 读取IDT表

```shell
kd> !idt 3
Dumping IDT: fffff8021188e000
03:	fffff8020f26edc0 nt!KiBreakpointTrap

kd> u fffff8020f26edc0
nt!KiBreakpointTrap:
fffff802`0f26edc0 4883ec08        sub     rsp,8
fffff802`0f26edc4 55              push    rbp
fffff802`0f26edc5 4881ec58010000  sub     rsp,158h
```

![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221115203716.png)