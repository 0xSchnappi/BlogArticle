[toc]

# Windows内核实验01——中断提权



## 实验环境

双机调试

物理机：window10 + windbg

试验机：VMware + winxp（一个CPU处理器一个核心数）

[学习视频](https://www.bilibili.com/video/BV1Eb411P7K5?spm_id_from=333.999.0.0&vd_source=032603e56385a7af6789a8f132f83ad2)

## IDT

- Windbg查看

  ```shell
  r idtr
  dq 8003f400
  !idt -a
  ```

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220616170444.png)

- pchunter查看

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220616170038.png)

- IDT简单介绍

  > - IDT是CPU（硬件）与操作系统（软件）交接中断和异常的关口（gate）。操作系统在启动早期的一个重要任务就是设置IDT，准备好处理异常和中断的各个函数。
  >
  > - IDT的每个表项是一个所谓的门描述符（gate description）结构。IDT的基本用途就是引领CPU从一个空间到另一个空间去执行，每个表项好像是一个从一个空间进入另一个空间的大门（gate）。
  >
  > - IDT可以包含3种门描述符：
  >
  >   1. 任务门（task-gate）描述符：任务切换
  >   2. 中断门（interrupt-gate）描述符：中断处理
  >   3. 陷进门（trap-gate）描述符：异常处理
  >
  > - IDT每个表项结构
  >
  >   ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220617111759.png)

## 程序

- vs2019编写测试程序编译器配置

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220616165140.png)

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220616165739.png)

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220616164905.png)

  > 1. vs2019编译在xp上运行的程序时，需要设置xp工具集，以及运行库、符号模式设置为否。（本人是Winxp上实验的，所以需要修改指令集等配置）
  > 2. 随机基址 否；固定基址 是。为了程序安全，编译器默认会使用基址随机化，不利于实验。

- C编写程序

  ```shell
  #include <iostream>
  #include <Windows.h>
  
  DWORD dwAddress = 0;
  
  //0x00401040
  void __declspec(naked) IdtEntry()
  {
      __asm {
          push eax
          mov eax, dword ptr ds:[0x8003f500]
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
      if ((DWORD)IdtEntry != 0x401040)
      {
          printf("wrong addr: %p", IdtEntry);
          exit(-1);
      }
      go();
      printf("%p\n", dwAddress);
      system("pause");
  }
  ```

  > 该程序的IdtEntry函数的执行权限是R0级的。
  >
  > 实现原理：
  >
  > 1. 编写中断处理函数，并且获取到地址
  > 2. 利用Windbg或者CE程序向计算机IDT中添加一条中断处理，这里添加的位置为IDT的第二十个表项。
  > 3. 然后运行该程序，该程序会自动触发0x20号中断，中断处理函数得到运行。

- 使用Windbg修改idt表

  ```shell
  eq 8003f500 0040ee0000081040
  ```

  > 以上是windbg命令是在中断描述符表第二十（地址为：8003f500）个中断处，添加一个可接收用户触发（由表项结构DPL位控制）的中断。
  >
  > 中断处理函数（IdtEntry）地址为00401040，中间的部分是关于权限相关的内容。

- 执行结果

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220617092255.png)

  > 读取IDT第二十个表项的低32位