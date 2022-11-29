# linux 内核编译

## make 命令

- make clean
  删除大多数的编译生成文件， 但是会保留内核的配置文件.config， 还有足够的编译支持来建立扩展模块
- make mrproper
  删除所有的编译生成文件， 还有内核配置文件， 再加上各种备份文件
- make distclean
  mrproper删除的文件， 加上编辑备份文件和一些补丁文件。

## make 警告

```shell
make[5]: 警告：文件“drivers/net/ethernet/sfc/falcon/Makefile”的修改时间在未来 41964 秒后
make[5]: 警告：检测到时钟错误。您的构建版本可能是不完整的。
make[4]: 警告：检测到时钟错误。您的构建版本可能是不完整的。
```

> 主要是你编译文件时，make发现文件的修改时间，比此时系统时间还要晚，因此会发出这个警告，个人认为经验，本质上还是得修改系统时钟，但是操作是无效的，那么只能修改文件时间

```shell
find ./ -type f |xargs touch
```

> 命令的本质就是遍历当前所有目录中的文件，touch一下（修改文件的时间为当前时间）
