[toc]

# x64内核研究4——KVAS

内核虚拟地址影子（Kernel Virtual Address Shadow，由微软提出的一个术语，简称KVAS），类似于Linux上的KPTI（Kernel page-table isolation）内核页表隔离机制，即把进程页表按照成用户态、内核态独立的分割成两份，为了杜绝用户态通过一些旁路漏洞来窃取内核态的数据。KVAS在Windows10/11上是默认开启的。

如果开启KVAS的话，应用程序会有两个CR3，即有PCB.DirectoryTableBase和PCB.UserDirectoryTableBase两个域。其中DirectoryTableBase域可以理解为内核CR3，能够访问内核物理页，而三环的Cr3（UserDirectoryTableBase）只映射了内核的KVASCODE区段的物理页（少数r3进入r0的入口），而没有映射其他区段的，因此通过3环的Cr3寻找内核TEXT段的物理页，最多只能找到PPE，而从PDE开始就没有映射了。

KVAS实现的本质就是内核使用Shadow函数类似于动态库中的stub函数一样，只是一个简单的跳转函数而已，没有实质功能。Windows实现KVAS的效果就是，用户进程访问不到内核的重要函数、数据等，实现这一功能主要是由CR3，之前用户进程能访问到内核的原因是，内核和用户进程共用一个CR3，通过这个CR3的和页映射关系即可访问到内核。现在Windows使用两个CR3，用户CR3和内核CR3，用户CR3只能访问用户进程和内核Shadow函数，无法访问真正的内核函数，只有通过内核CR3才能访问到真正的内核函数。

## 工具介绍

- 使用

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221127114914.png)

  > 这个工具的主要功能就是对PDBWindows符号文件进行解析,而且还会解析出Windows的结构体
  >
  > - 首先你需要设置`_NT_SYMBOL_PATH`环境变量,方便使用
  >
  > - 选择使用环境变量
  >
  >   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221127115854.png)
  >
  > - 设置PDB文件,以及生成C格式头文件的路径,点击Translate即可生成头文件
  >
  >   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221127120015.png)

- IDA添加Windows符号结构体

  > - 添加头文件(Ctrl+F9)
  >
  >   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221127120215.png)
  >
  > - 查看结构体(Shift+F11)
  >
  >   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221127120315.png)
  >
  >   

## KVAS存在形式

- 简介

  > KPTI(Kernel Page-Table Isolation).

  ```shell
  KVASCODE:FFFFF8020F3F4280 KiBreakpointTrapShadow proc near        ; DATA XREF: .pdata:FFFFF8020F5DE9F8↓o
  KVASCODE:FFFFF8020F3F4280                                         ; INITDATA:FFFFF8020FAF4208↓o
  KVASCODE:FFFFF8020F3F4280 F6 44 24 08 01                          test    [rsp+arg_0], 1
  KVASCODE:FFFFF8020F3F4285 74 5F                                   jz      short loc_FFFFF8020F3F42E6
  KVASCODE:FFFFF8020F3F4287 0F 01 F8                                swapgs
  KVASCODE:FFFFF8020F3F428A 65 0F BA 24 25 18 70 00+                bt      dword ptr gs:7018h, 1
  KVASCODE:FFFFF8020F3F428A 00 01
  KVASCODE:FFFFF8020F3F4294 72 0C                                   jb      short loc_FFFFF8020F3F42A2
  KVASCODE:FFFFF8020F3F4296 65 48 8B 24 25 00 70 00+                mov     rsp, gs:7000h
  KVASCODE:FFFFF8020F3F4296 00
  KVASCODE:FFFFF8020F3F429F 0F 22 DC                                mov     cr3, rsp
  
  .text:FFFFF8020F26EDC0 KiBreakpointTrap proc near              ; CODE XREF: KiBreakpointTrapShadow:loc_FFFFF8020F3F42E6↓j
  .text:FFFFF8020F26EDC0                                         ; DATA XREF: .pdata:FFFFF8020F5CA874↓o ...
  .text:FFFFF8020F26EDC0 48 83 EC 08                             sub     rsp, 8
  .text:FFFFF8020F26EDC4 55                                      push    rbp
  .text:FFFFF8020F26EDC5 48 81 EC 58 01 00 00                    sub     rsp, 158h
  .text:FFFFF8020F26EDCC 48 8D AC 24 80 00 00 00                 lea     rbp, [rsp+80h]
  .text:FFFFF8020F26EDD4 C6 45 AB 01                             mov     [rbp+0E8h+var_13D], 1
  ```

  > 分别用用户cr3和内核cr3对以上两个函数地址进行翻译，对比翻译结果

- 用户cr3

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221127141254.png)

  ```shell
  
  KVASCODE:FFFFF8020F3F4280 KiBreakpointTrapShadow proc near        ; DATA XREF: .pdata:FFFFF8020F5DE9F8↓o
  KVASCODE:FFFFF8020F3F4280                                         ; INITDATA:FFFFF8020FAF4208↓o
  
  CR3 = 25c92000
  
  kd>  .formats FFFFF8020F3F4280
  Evaluate expression:
    Hex:     fffff802`0f3f4280
    Decimal: -8787247283584
    Decimal (unsigned) : 18446735286462268032
    Octal:   1777777600101717641200
    Binary:  11111111 11111111 11111000 00000010 00001111 00111111 01000010 10000000
    Chars:   .....?B.
    Time:    ***** Invalid FILETIME
    Float:   low 9.42983e-030 high -1.#QNAN
    Double:  -1.#QNAN
    
  1111100 00				PML4E		1F0
  0000010 00				PDPTE		8
  001111 001				PDE			79
  11111 0100				PTE			1F4
  0010 10000000			offset		280
  
  kd> !dq 25c92000 + 1f0 * 8
  #25c92f80 00000000`01208063 00000000`00000000
  #25c92f90 00000000`00000000 00000000`00000000
  kd> !dq 01208000 + 8 * 8
  # 1208040 00000000`01209063 00000000`00000000
  # 1208050 00000000`00000000 00000000`00000000
  kd> !dq 01209000 + 79 * 8
  # 12093c8 00000000`01293063 00000000`01294063
  # 12093d8 00000000`01295063 00000000`01296063
  kd> !dq 01293000 + 1F4 * 8
  # 1293fa0 09000000`022f0121 09000000`022f1121
  # 1293fb0 09000000`022f2121 09000000`022f3121
  kd> !db 22f0000 + 280
  # 22f0280 f6 44 24 08 01 74 5f 0f-01 f8 65 0f ba 24 25 18 .D$..t_...e..$%.
  # 22f0290 70 00 00 01 72 0c 65 48-8b 24 25 00 70 00 00 0f p...r.eH.$%.p...
  
  
  .text:FFFFF8020F26EDC0 KiBreakpointTrap proc near              ; CODE XREF: KiBreakpointTrapShadow:loc_FFFFF8020F3F42E6↓j
  .text:FFFFF8020F26EDC0                                         ; DATA XREF: .pdata:FFFFF8020F5CA874↓o ...
  
  kd> .formats FFFFF8020F26EDC0
  Evaluate expression:
    Hex:     fffff802`0f26edc0
    Decimal: -8787248878144
    Decimal (unsigned) : 18446735286460673472
    Octal:   1777777600101711566700
    Binary:  11111111 11111111 11111000 00000010 00001111 00100110 11101101 11000000
    Chars:   .....&..
    Time:    ***** Invalid FILETIME
    Float:   low 8.23022e-030 high -1.#QNAN
    Double:  -1.#QNAN
    
  11111000 0			PML4E	1F0
  0000010 00			PDPTE	8
  001111 001			PDE		79
  00110 1110			PTE		6E
  1101 11000000		offset	DC0
  
  kd> !dq 25c92000 + 1f0 * 8
  #25c92f80 00000000`01208063 00000000`00000000
  #25c92f90 00000000`00000000 00000000`00000000
  kd> !dq 01208000 + 8 * 8
  # 1208040 00000000`01209063 00000000`00000000
  # 1208050 00000000`00000000 00000000`00000000
  kd> !dq 01209000 + 79 * 8
  # 12093c8 00000000`01293063 00000000`01294063
  # 12093d8 00000000`01295063 00000000`01296063
  kd> !dq 1293000 + 6E * 8
  # 1293370 09000000`0216a121 09000000`0216b121
  # 1293380 09000000`0216c121 09000000`0216d121
  kd> !db 216a000 + dc0
  # 216adc0 48 83 ec 08 55 48 81 ec-58 01 00 00 48 8d ac 24 H...UH..X...H..$
  # 216add0 80 00 00 00 c6 45 ab 01-48 89 45 b0 48 89 4d b8 .....E..H.E.H.M.
  ```

  > 使用

- 内核cr3

  ```shell
  kd> !process 0 0 ForWindows10.exe
  PROCESS ffff870c917a7080
      SessionId: 1  Cid: 1118    Peb: 0033f000  ParentCid: 0e24
      DirBase: 1abcb000  ObjectTable: ffffa9833d33c540  HandleCount:  47.
      Image: ForWindows10.exe
  ```

  

- 问题探究

  ```shell
  kd> !process 0 0 ForWindows10.exe
  PROCESS ffff870c917a7080
      SessionId: 1  Cid: 1118    Peb: 0033f000  ParentCid: 0e24
      DirBase: 6db4b000  ObjectTable: ffffa9833d33c540  HandleCount:  47.
      Image: ForWindows10.exe
      
  kd> !process 0 0 ForWindows10.exe
  PROCESS ffff870c917a7080
      SessionId: 1  Cid: 1118    Peb: 0033f000  ParentCid: 0e24
      DirBase: 1abcb000  ObjectTable: ffffa9833d33c540  HandleCount:  47.
      Image: ForWindows10.exe
  ```

  

- int3 中断分析

  ```assembly
  KVASCODE:000000014034D280 KiBreakpointTrapShadow proc near
  KVASCODE:000000014034D280                 test    byte ptr [rsp+8], 1
  KVASCODE:000000014034D285                 jz      short loc_14034D2E6
  KVASCODE:000000014034D287                 swapgs
  KVASCODE:000000014034D28A                 bt      dword ptr gs:7018h, 1
  KVASCODE:000000014034D294                 jb      short loc_14034D2A2
  KVASCODE:000000014034D296                 mov     rsp, gs:7000h
  KVASCODE:000000014034D29F                 mov     cr3, rsp
  KVASCODE:000000014034D2A2
  KVASCODE:000000014034D2A2 loc_14034D2A2:                          ; CODE XREF: KiBreakpointTrapShadow+14↑j
  KVASCODE:000000014034D2A2                 mov     rsp, gs:7008h
  KVASCODE:000000014034D2AB                 mov     gs:10h, rsi
  KVASCODE:000000014034D2B4                 mov     rsi, gs:38h
  KVASCODE:000000014034D2BD                 add     rsi, 4200h
  KVASCODE:000000014034D2C4                 push    qword ptr [rsi-8]
  KVASCODE:000000014034D2C7                 push    qword ptr [rsi-10h]
  KVASCODE:000000014034D2CA                 push    qword ptr [rsi-18h]
  KVASCODE:000000014034D2CD                 push    qword ptr [rsi-20h]
  KVASCODE:000000014034D2D0                 push    qword ptr [rsi-28h]
  KVASCODE:000000014034D2D3                 mov     rsi, gs:10h
  KVASCODE:000000014034D2DC                 and     qword ptr gs:10h, 0
  KVASCODE:000000014034D2E6
  KVASCODE:000000014034D2E6 loc_14034D2E6:                          ; CODE XREF: KiBreakpointTrapShadow+5↑j
  KVASCODE:000000014034D2E6                 jmp     KiBreakpointTrap
  ```

  



- 硬件补丁

  ```assembly
  .text:00000001401C7DC0 KiBreakpointTrap proc near              ; CODE XREF: KiBreakpointTrapShadow:loc_14034D2E6↓j
  .text:00000001401C7DC0                                         ; DATA XREF: .pdata:0000000140523874↓o ...
  .text:00000001401C7DC0
  .text:00000001401C7DC0                 sub     rsp, 8
  .text:00000001401C7DC4                 push    rbp
  .text:00000001401C7DC5                 sub     rsp, 158h
  .text:00000001401C7DCC                 lea     rbp, [rsp+80h]
  .text:00000001401C7DD4                 mov     [rbp+0E8h+var_13D], 1
  .text:00000001401C7DD8                 mov     [rbp+0E8h+var_138], rax
  .text:00000001401C7DDC                 mov     [rbp+0E8h+var_130], rcx
  .text:00000001401C7DE0                 mov     [rbp+0E8h+var_128], rdx
  .text:00000001401C7DE4                 mov     [rbp+0E8h+var_120], r8
  .text:00000001401C7DE8                 mov     [rbp+0E8h+var_118], r9
  .text:00000001401C7DEC                 mov     [rbp+0E8h+var_110], r10
  .text:00000001401C7DF0                 mov     [rbp+0E8h+var_108], r11
  .text:00000001401C7DF4                 test    [rbp+0E8h+arg_0], 1
  .text:00000001401C7DFB                 jnz     short loc_1401C7E27
  .text:00000001401C7DFD                 test    byte ptr gs:278h, 1
  .text:00000001401C7E06                 jnz     short loc_1401C7E10
  .text:00000001401C7E08                 lfence
  .text:00000001401C7E0B                 jmp     loc_1401C8069
  ```

  

## 参考文献

[漏洞](https://xz.aliyun.com/t/3072)

[KVAS1](https://www.fortinet.com/blog/threat-research/a-deep-dive-analysis-of-microsoft-s-kernel-virtual-address-shadow-feature)

[KVAS2](http://www.qfrost.com/WindowsKernel/KVAS/)