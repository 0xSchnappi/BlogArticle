[toc]

# Windows内核实验04——再次开中断(调用内核函数)

## 要素

1. 内核权限
2. 内核环境

## 开启中断

- 开启中断

  ```assembly
  sti
  ```

  

- 内核环境

  ```assembly
  push 30h
  pop fs
  
  # 下面代码可以加，但不必要，只是为了安全考虑
  mov ecx, 23h
  mov ds, ecx
  mov es, ecx
  ```

  1. 当线程进入0环时，FS:[0]指向KPCR(3环时 FS:[0] --> TEB)
  2. 每个CPU都有一个KPCR结构体(一个内核一个)
  3. KPCR中存储了CPU本身要用的一些重要数据：GDT、IDT以及线程相关的一些信息。

- demo1

  ```c++
  #include <iostream>
  #include <Windows.h>
  
  typedef DWORD(__stdcall* Ex_ALLOCATE)(DWORD PoolType, DWORD NumberOfBytes);
  Ex_ALLOCATE ExAllocatePool = (Ex_ALLOCATE)0x8053454C;
  DWORD g_pool;
  typedef DWORD(*DBG_PRINT)(PCSTR Format, ...);
  DBG_PRINT DbgPrint = (DBG_PRINT)0x80528e62;
  char str[] = "HelloDriver0xSchnappi";
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
          cli
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

  ```shell
  eq 8003f500 0040ee0000081040
  ```

  > 一般内核函数调用的环境就是fs寄存器设置，不用的函数还有区别，需要测试。
  >
  > 函数调用后fs恢复为三环状态时，要关中断，不然在恢复fs过程中遇到中断会造成系统蓝屏

- 结果

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20220922105811.png)

