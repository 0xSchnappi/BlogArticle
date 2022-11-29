# git config

## ssh and https

- ssh use ssh 
  
  ```shell
  ssh-keygen -t rsa -C "example@qq.com"
  cat ~/.ssh/id_rsa.pub
  ```
  
  > [Github] SSH and GPG keys and click New SSH key 

- https use token
  
  ```shell
  git config --global credential.helper store
  ```
  
  > [Github] Settings/Developer settings/Personal access tokens/Tokens(classic)
  > 用户名可以是GitHub的用户名，也可以是GitHub的注册邮箱，密码就是这个Token

- git 拉取子模块
  
  ```shell
  git submodule update --init
  ```

- 