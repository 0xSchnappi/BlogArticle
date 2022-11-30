[toc]

# Windows内核实验14——指令TLB与流水线

## 原理

- `TLB`不确定性

## 代码

- TLB 不确定性

  ```c++
  #include <iostream>
  #include <Windows.h>
  
  
  #define PTE(x) ((DWORD*)(0xc0000000 + ((x >> 12) << 3)))
  #define PDE(x) ((DWORD*)(0xc0600000 + ((x >> 21) << 3)))
  
  DWORD old_pte[2];
  DWORD g_out = 0;
  #pragma section("data_seg",read,write)
  __declspec(allocate("data_seg"))    DWORD page1[1024];      // 0x0041b000
  __declspec(allocate("data_seg"))    DWORD page2[1024];      // 0x0041c000
  
  // 0x00401040
  void __declspec(naked) IdtEntry1()
  {
      
  
      old_pte[0] = PTE(0x0041c000)[0];    // 保存page2的PTE
      old_pte[1] = PTE(0x0041c000)[1];
  
      __asm
      {
          mov eax, cr3            // 刷新TLB
          mov cr3, eax
      }
  
      __asm mov eax, ds: [0x0041c000]
  
      PTE(0x0041c000)[0] = PTE(0x0041b000)[0];    // 将page2挂在到page1的物理内存上
      PTE(0x0041c000)[1] = PTE(0x0041b000)[1];
  
  
      __asm
      {
          mov eax, ds: [0x0041c000]  // 确保地址存在于TLB缓存中
          mov g_out, eax
      }
  
      PTE(0x0041c000)[0] = old_pte[0];    // 如果不恢复PTE，程序结束时释放内存会造成double free
      PTE(0x0041c000)[1] = old_pte[1];
  
      __asm
      {
          mov eax, cr3           
          mov cr3, eax
          iretd
      }
  }
  
  void go()
  {
      page1[0] = 0xc3;       // 确保物理地址存在
      page2[0] = 0xc390;
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
      system("pause");
      for (size_t i = 0; i < 500000; i++)
      {
          go();
          //printf("i: %d\n", i);
          if (g_out != 0xc390)
          {
              printf("i : %d\tg_out: %p\n", i, g_out);
          }
      }
      
      
      system("pause");
  }
  ```

  - 运行结果

    ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221024090704.png)

    > TLB不是固定的，是不确定的

  - page1和page2分别为十六进制数时就正常，是十进制数时就有问题？

- 指令TLB

  ```c++
  #include <iostream>
  #include <Windows.h>
  
  
  #define PTE(x) ((DWORD*)(0xc0000000 + ((x >> 12) << 3)))
  #define PDE(x) ((DWORD*)(0xc0600000 + ((x >> 21) << 3)))
  
  DWORD old_pte[2];
  DWORD g_out = 0;
  #pragma section("data_seg",read,write)
  __declspec(allocate("data_seg"))    DWORD page1[1024];      // 0x0041b000
  __declspec(allocate("data_seg"))    DWORD page2[1024];      // 0x0041c000
  
  // 0x00401040
  void __declspec(naked) IdtEntry1()
  {
      //__asm int 3
      
  
      old_pte[0] = PTE(0x0041c000)[0];    // 保存page2的PTE
      old_pte[1] = PTE(0x0041c000)[1];
  
      __asm
      {
          mov eax, cr3            // 刷新TLB
          mov cr3, eax
      }
  
      PTE(0x0041c000)[0] = PTE(0x0041b000)[0];    // 将page2挂在到page1的物理内存上
      PTE(0x0041c000)[1] = PTE(0x0041b000)[1];
  
  
      __asm
      {
          mov eax, ds: [0x0041c000]  // 确保地址存在于TLB缓存中
          mov g_out, eax
      }
  
      PTE(0x0041c000)[0] = old_pte[0];    // 如果不恢复PTE，程序结束时释放内存会造成double free
      PTE(0x0041c000)[1] = old_pte[1];
  
      __asm
      {
          mov eax, cr3           
          mov cr3, eax
          iretd
      }
  }
  
  void go()
  {
      page1[0] = 0xc3;       // 确保物理地址存在
      page2[0] = 0xc390;
      ((void(*)())(DWORD)page1)();
      ((void(*)())(DWORD)page2)();
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
      system("pause");
      for (size_t i = 0; i < 500000; i++)
      {
          go();
          if (g_out != 0xc3)
          {
              printf("i : %d\tg_out: %p\n", i, g_out);
          }
      }
      
      
      system("pause");
  }
  
  ```

  > 1. 保存page2的TLB
  > 2. 刷新TLB，使page1和page2的TLB缓存失效
  > 3. 访问page2地址，应该通过PTE访问物理地址
  >
  > - **结论：**每次g_out都是0xc3

## 结论

- 利用TLB确定性做合适的事情，比如刷新TLB，页如果没有设置G位，必然会在TLB缓存中失效，还有强制刷新，在你想刷新含有G位的页时使用