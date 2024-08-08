# docker 容器连接

## 网络端口映射

  ```shell
  docker run -d -p 127.0.0.1:80:5000 0xschnappi/simple-webapp python app.py 
  ```

  > 这样就可以通过访问127.0.0.1:80来访问容器的5000端口

## docker 容器互联

docker 连接会创建一个父子关系， 其中父容器可以看到子容器的信息。

### docker 容器命名

  ```shell
  docker run -d -P --name runoob 0xschnappi/simple-webapp python app.py 
  ```

  > 可以使用`--name`标识来命名容器

### docker 新建网络

  ```shell
  docker network create -d bridge test-net
  ```

  > 创建一个新的Docker网络
  > -d: 参数指定Docker网络类型，有bridge、overlay

### 连接容器

  ```shell
  docker run -itd --name test1 --network test-net ubuntu /bin/bash
  docker run -itd --name test2 --network test-net ubuntu /bin/bash

  docker exec -it test1 /bin/bash       # 进入test1容器
  ping test2        # 通过ping test2 网络证明容器建立了互联关系
  ```

## 配置 DNS

在宿主机的`/etc/docker/daemon.json`文件中增加以下内容

```json
{
  "dns" : [
    "114.114.114.114",
    "8.8.8.8"
  ]
}
```

查看效果

```shell
docker run -it --rm ubuntu
cat etc/resolv.conf
```

### 手动指定容器的配置

只想在指定的容器设置DNS，使用以下命令：

  ```shell
  docker run -it --rm -h host_ubuntu  --dns=114.114.114.114 --dns-search=test.com ubuntu
  ```

  > --rm：容器退出时自动清理容器内部的文件系统。
  > -h HOSTNAME 或者 --hostname=HOSTNAME： 设定容器的主机名，它会被写到容器内的 /etc/hostname 和 /etc/hosts。
  > --dns=IP_ADDRESS： 添加 DNS 服务器到容器的 /etc/resolv.conf 中，让容器用这个服务器来解析所有不在 /etc/hosts 中的主机名。
  > --dns-search=DOMAIN： 设定容器的搜索域，当设定搜索域为 .example.com 时，在搜索一个名为 host 的主机时，DNS 不仅搜索 host，还会搜索 host.example.com。
