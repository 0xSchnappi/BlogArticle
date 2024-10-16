# Docker Compose

## Compose 安装

  ```shell
  sudo curl -L "https://github.com/docker/compose/releases/download/v2.2.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose     # 下载docker-compose

  sudo chmod +x /usr/local/bin/docker-compose       # docker-compose设置执行权限

  sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose      # 创建软连接
  ```

## 创建 docker-compose.yml
在`src/composetest`目录创建docker-compose.yml文件，