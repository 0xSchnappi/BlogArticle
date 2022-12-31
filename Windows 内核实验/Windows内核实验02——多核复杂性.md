[toc]

# Windows内核实验02——多核复杂性

## 实验环境

双机调试

物理机：window10 + windbg

试验机：VMware + winxp（一个CPU处理器两个核心数）

[学习视频](https://www.bilibili.com/video/BV1Lb411P76o?spm_id_from=333.999.0.0)

## 测试程序01

- demo

  ```c++
  #include <iostream>
  #include <Windows.h>
  
  DWORD dwAddress = 0;
  
  //0x00401040
  void __declspec(naked) IdtEntry1()
  {
      __asm {
          push eax
          mov eax, 1
          mov dwAddress, eax
          pop eax
          iretd
      }
  }
  
  //0x00401050
  void __declspec(naked) IdtEntry2()
  {
      __asm {
          push eax
          mov eax, 2
          mov dwAddress, eax
          pop eax
          iretd
      }
  }
  
  void go()
  {
      __asm int 0x20
  }
  
  int main()
  {
      if ((DWORD)IdtEntry1 != 0x401040 || (DWORD)IdtEntry2 != 0x401050)
      {
          printf("IdtEntry1 addr: %p\nIdtEntry2 addr: %p", IdtEntry1, IdtEntry2);
          exit(-1);
      }
      go();
      printf("%p\n", dwAddress);
      system("pause");
  }
  ```

  > 由于多核CPU拥有多个核心数，这时每个核心都有一个IDT，核心1的IDT的第二十个表项的处理函数IdtEntry1，核心2的IDT的第二十个表项的处理函数IdtEntry2，我们的程序在哪个核心上执行是随机的，在那个核心上执行就会执行对应的中断处理函数，打印对应的

- windbg设置IDT

  ```shell
  ~0
  eq 8003f500 0040ee0000081040
  ~1
  eq f892e690 0040ee0000081050
  ```

  >1. 切换0号CPU
  >
  >2. 设置0号CPU IDT
  >
  >   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220617165714.png)
  >
  >3. 切换1号CPU
  >
  >4. 设置1号CPU IDT
  >
  >   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220617165428.png)
  >

- 执行

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/image-20220617165906818.png)

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220617170125.png)

## 测试程序02



1. 打开PChunter工具选择 驱动模块，第一个ntkrnlpa.exe右键定位到文件（内核文件版本比较多，单核版本、多核版本、支持物理内存扩展等版本）。

   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220621105944.png)

2. 由上图我们可以看见内核文件的基地址为0x804D8000，我们可以使用IDA 32位打开设置基地址。

   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220621110722.png)

3. 关闭写保护

   ```assembly
   # 关闭写保护x86
   __asm
   {
   cli;//将处理器标志寄存器的中断标志位清0，不允许中断
   mov eax, cr0
   and eax, not 0x10000
   mov cr0, eax
   }
   
   # 开启写保护x86
   __asm
   {
   mov eax, cr0
   or eax, 0x10000
   mov cr0, eax
   sti;//将处理器标志寄存器的中断标志置1，允许中断
   }
   ```

   ```assembly
   # 关闭写保护x64
   __asm
   {
   cli; //将处理器标志寄存器的中断标志位清0，不允许中断
   mov rax,cr0
   and rax, not 0x10000
   mov cr0, rax
   }
   
   
   # 开启写保护x64
   __asm
   {
   mov rax, cr0
   or rax, 0x10000
   mov cr0, rax
   sti; //将处理器标志寄存器的中断标志置1，允许中断
   }
   
   ```

3. 可以在对应的函数中进行内核挂钩，多核内核挂钩需要解决的问题是，你挂钩函数完成前，别的核不能执行该函数。否则可能会触发异常代码，导致蓝屏。

