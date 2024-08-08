# docker Dockerfile

## Dockerfile 命令

| Dockerfile 指令 | 说明 |
| --- | --- |
| From | 指定基础镜像 |
| LABEL | 添加镜像的元数据，使用键值对的形式。 比如可以添加镜像的作者 `LABEL org.opencontainers.image.authors="runoob"` |
| RUN | 在构建过程中在镜像中执行的命令。shell格式(`RUN <命令行命令>`)，比如`RUN sudo apt update`;exec格式(`RUN ["可执行文件", "参数1", "参数2"]`)，比如`RUN ["./test.php", "dev", "offline"]` |
| CMD | 容器创建时的默认命令(可以被覆盖) |
| ENTRYPOINT | 设置容器创建时的主要命令。(不可被覆盖) |
| EXPOSE | 容器运行时监听的特定网络端口 |
| ENV | 在容器内部设置环境变量 |
| ADD | 将文件、目录或远程URL复制到镜像中(优点：在执行 <源文件> 为 tar 压缩文件的话，压缩格式为 gzip, bzip2 以及 xz 的情况下，会自动复制并解压到 <目标路径>) |
| COPY | 将文件或目录复制到镜像中 |
| VOLUME | 为容器创建挂载点或声明卷(格式：`VOLUME ["<路径1>", "<路径2>", ...]`或`VOLUME <路径>`) |
| WORKDIR | 设置后续指令的工作目录 |
| USER | 指定后续指令的用户上下文，**用户和用户组必须提前已经存在**。(格式：USER <用户名>[:<用户组>]) |
| ARG | 定义在构建过程中传递给构建器的变量，可使用"docker build"命令设置。(与ENV作用一致，不过作用域不一样，ARG设置的环境变量仅对Dockerfile内有效) |
| ONBUILD | 当该镜像被用作另一个构建过程的基础时，添加触发器，(格式：`ONBUILD <其他指令>`)。 Dockerfile 里用 ONBUILD 指定的命令，在本次构建镜像的过程中不会执行（假设镜像为 test-build）。当有新的 Dockerfile 使用了之前构建的镜像 FROM test-build ，这时执行新镜像的 Dockerfile 构建时候，会执行 test-build 的 Dockerfile 里的 ONBUILD 指定的命令。 |
| STOPSIGNAL | 设置发送给容器以退出的系统调用信号 |
| HEALTHCHECK | 周期性检查容易健康状态的命令，用于指定某个程序或者指令来监控 docker 容器服务的运行状态。 |
| SHELL | 覆盖Docker中默认的shell |


