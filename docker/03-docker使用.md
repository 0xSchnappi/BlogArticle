# 容器使用

## 获取镜像

  ```shell

  docker pull ubuntu

  ```

## 启动容器

启动一个容器，以命令行模式进入该容器

  ```shell

  docker run -it ubuntu /bin/bash

  ```

  - `-i`：交互式操作
  - `-t`：终端
  - `/bin/bash` 希望有个交互式shell，因此用的是`/bin/bash`

## 启动已停止的容器

  ```shell

  docker start competent_einstein

  ```

## 后台运行

  ```shell

  docker run -itd --name ubuntu-test ubuntu /bin/bash

  ```

  > `-d`参数默认不会进入容器，想要进入容器需要使用指令`docker exec`

## 进入容器

  ```shell

  dokcer attach competent_einstein
  # 或者
  docker exec -it competent_einstein  /bin/bash

  ```

  > 推荐使用docker exec命令，u因为此命令退出容器终端，但不会导致容器停止

## 导出和导入容器

### 导出容器

  ```shell

  docker export competent_einstein > ubuntu.tar

  ```

  > 这样将导出容器快照到本地文件

### 导入容器

  ```shell

  cat docker/ubuntu.tar | docker import - test/ubuntu:v1

  ```

  > 使用`docker import`从容器快照文件中再导入为镜像，以上代码是将快照文件ubuntu.tar 导入到镜像 test/ubuntu:v1

  ```shell

  docker import http://example.com/exampleimage.tgz example/imagerepo

  ```

  > 也可以通过指定URL或者某个目录来导入

## 删除容器

  ```shell

  docker rm -f competent_einstein

  ```

下面的命令可以清理掉所有处于终止状态的容器

  ```shell

  docker container prune

  ```

## 运行一个web应用

  ```shell

  docker pull 0xschnappi/simple-webapp
  docker run -d -P 0xschnappi/simple-webapp python app.py
  
  ```

  > `-d`: 让容器在后台运行
  > `-P`: 将容器内部使用的网络端口随机映射到我们使用的主机上

  ```shell

  docker run -d -p 80:5000 0xschnappi/simple-webapp python app.py 

  ```
  > 以上示例是将docker的5000端口映射到主机的80端口
  > `-p`: 参数设置不一样的端口

## 网络端口的快捷方式

查看容器端口的映射情况
  ```shell

  docker port distracted_rhodes
  # 5000/tcp -> 0.0.0.0:80
  # 5000/tcp -> [::]:80

  ```

## 查看WEB应用程序日志

  ```shell

  docker logs -f --tail 100 distracted_rhodes

  ```

## 查看WEB应用程序容器的进程

  ```shell

  docker top distracted_rhodes

  ```

## 检查WEB应用程序

  ```shell

  docker inspect distracted_rhodes

  ```

  > 它会返回一个JSON文件记录着Docker容器的配置和状态信息

## 停止WEB应用容器

  ```shell

  docker stop distracted_rhodes

  ```

## 重启WEB容器

  ```shell

  docker restart distracted_rhodes

  ```

## 移除WEB应用容器

  ```shell

  docker rm distracted_rhodes

  ```
