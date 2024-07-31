# Docker 运行

## Docker Hello World

  ```shell

  docker run ubuntu:15.10 /bin/echo "Hello world"

  ```

## 运行交互式的容器

  ```shell

  docker run -i -t ubuntu:15.10 /bin/bash

  ```

    - `-t`: 在新的容器内指定一个伪终端或终端
    - `-i`: 允许你对容器内的标准输入(STDIN)进行交互

> 可以通过运行`exit`或者`CTRL+D`来退出容器

## 启动容器（后台模式）

以进程的方式运行一个容器

  ```shell

  docker run -d ubuntu:15.10 /bin/sh -c "while true; do echo hello world; sleep 1; done"

  ```

  docker 7种状态
  - `created` (已创建)
  - `restarting` (重启中)
  - `running 或 up` (运行中)
  - `removing` (迁移中)
  - `paused` (暂停)
  - `exited` (停止)
  - `dead` (死亡)

**docker 日志**

  ```shell

  docker logs competent_einstein

  # 查看实时日志
  docker logs -f --tail 100 competent_einstein

  ```

## 停止docker

  ```shell

  docker stop com

  ```
