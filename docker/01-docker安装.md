# docker 安装

## 添加Docker镜像

### 添加GPC密钥

- 阿里源

  ```shell

  curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | apt-key add -

  ```

- 清华源

  ```shell

  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

  ```

### 添加Docker软件源

- 阿里源
  
  ```shell

  sudo add-apt-repository "deb [arch=amd64] http://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"

  ```

- 清华源

  ```shell

  sudo add-apt-repository "deb [arch=amd64] https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu $(lsb_release -cs) stable"

  ```

## 安装Docker

  ```shell

  sudo apt -y update

  sudo apt install docker-ce
  
  ```

## 重启Docker服务

  ```shell

  service docker restart

  ```

# docker-compose 安装

  ```shell

  # 在github下载指定版本的docker-compose
  wget https://github.com/docker/compose/releases/download/v2.29.0/docker-compose-linux-x86_64

  # 安装docker-compose
  cp docker-compose-linux-x86_64 /usr/local/bin/docker-compose

  ```

