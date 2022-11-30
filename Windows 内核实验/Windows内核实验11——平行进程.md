[toc]

# Windows内核实验11——平行进程

## 原理

- 修改`CR3`寄存器以后，`EIP`是不变的，通过这个原理，实现了去对方进程获取数据、执行代码

## 代码

- `IdtEntry.cpp`

  ```c++
  #include <iostream>
  #include <Windows.h>
  
  
  DWORD g_num;
  
  //0x00401040
  void __declspec(naked) IdtEntry1()
  {
      __asm
      {
          mov eax, cr3
          mov ds:[0x8003f120], eax
  
          mov eax, ds:[0x8003f128]
          mov cr3, eax    // 0x40104F
  
          mov eax, 0x12345678
          mov eax, 0x12345678
          mov eax, 0x12345678
          mov eax, 0x12345678
          mov eax, 0x12345678     // 0x401066
          nop
          nop
          nop
          nop
          nop
          nop
          mov g_num, eax      //0x401071
  
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
      printf("g_num: %p\n", g_num);
      system("pause");
  }
  ```

  

- `Parallel.cpp`

  ```c++
  #include <iostream>
  #include <Windows.h>
  
  DWORD g_cr3;
  DWORD g_num = 0;
  
  //0x00401040
  void __declspec(naked) IdtEntry1()
  {
  
      __asm
      {
          mov eax ,cr3
          mov ds:[0x8003f128], eax
          mov g_cr3, eax
  
          iretd
  
          mov eax, 0x12345678     // 0x40104F
          nop
          nop
          mov ecx,1
          mov g_num, ecx
          mov eax, 0x11111111
          mov ecx, ds:[0x8003f120]
          mov cr3, ecx    // 0x40106D
          nop     
          nop     // 0x401070
  
  
          
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
  
      while (true)
      {
          printf("g_cr3 %p \tg_num: %p\n", g_cr3, g_num);
          Sleep(2000);
      }
  
      system("pause");
  }
  ```

  

## 结论

- 执行结果

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221020202323.png)

- 执行过程图

  ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20221020204359.png)

- **重点：**修改`CR3`寄存器以后，`EIP是不变的，通过这个原理，实现了去对方进程获取数据、执行代码

## 参考资料

[平行进程](https://www.bilibili.com/video/BV17t41127rT/?spm_id_from=333.999.0.0&vd_source=032603e56385a7af6789a8f132f83ad2)





