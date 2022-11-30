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
  
  > `git submodule init` 用来初始化本地配置文件，
  > 
  >  `git submodule update` 则从该项目中抓取所有数据并检出父项目中列出的合适的提交。

- clone最新代码
  
  ```shell
  git clone --depth 1 --recursive https://github.com/***.git
  ```
  
  > 如果给 `git clone` 命令传递 `--recurse-submodules` 选项，它就会自动初始化并更新仓库中的每一个子模块， 包括可能存在的嵌套子模块。      

- git pull --rebase
  
  > 多人基于同一个远程分支开发的时候，如果想要顺利 push 又不自动生成 merge commit，建议在每次提交都按照如下顺序操作：
  
  ```shell
  # 把本地发生改动的文件贮藏一下
  $ git stash
  
  # 把远程最新的 commit 以变基的方式同步到本地
  $ git pull --rebase
  
  # 把本地贮藏的文件弹出，继续修改
  $ git stash pop
  
  # 将内容写入暂存区
  $ git add
  
  # 把暂存区内容添加到本地仓库
  $ git commit 
  
  # 防止过程中又有人在远程提交最新的commit
  $ git pull
  
  # 把本地的 commit 推送到远程
  $ git push
  ```

- 分支合并
  
  - git merge
    
    > 你需要另一个分支的所有代码变动
    
    ```shell
    git checkout master
    git merge contact-form
    ```
    
    > 把“contact-form”分支的改动合并到“master”中去：
    > 
    > 1. 切换到那个需要接收改动的分支上
    > 
    > 2. 执行“git merge”命令，并且在后面加上那个将要合并进来的分支名称
  
  - git 
    
    > 你只需要部分代码变动（某几个提交）
    
    ```shell
    git cherry-pick <commitHash>
    git cherry-pick <HashA> <HashB>
    git cherry-pick --abort
    ```
    
    > - 将指定的提交`commitHash`，应用于当前分支。这会在当前分支产生一个新的提交，当然它们的哈希值会不一样。
    > 
    > - A 和 B 两个提交应用到当前分支。
    > 
    > - 放弃本次cherry-pick
    > 
    > `git cherry-pick`命令的常用配置项如下。
    > 
    > **（1）`-e`，`--edit`**
    > 
    > 打开外部编辑器，编辑提交信息。
    > 
    > **（2）`-n`，`--no-commit`**
    > 
    > 只更新工作区和暂存区，不产生新的提交。
    > 
    > **（3）`-x`**
    > 
    > 在提交信息的末尾追加一行`(cherry picked from commit ...)`，方便以后查到这个提交是如何产生的。
    > 
    > **（4）`-s`，`--signoff`**
    > 
    > 在提交信息的末尾追加一行操作者的签名，表示是谁进行了这个操作。
    > 
    > **（5）`-m parent-number`，`--mainline parent-number`**
    > 
    > 如果原始提交是一个合并节点，来自于两个分支的合并，那么 Cherry pick 默认将失败，因为它不知道应该采用哪个分支的代码变动。

## 参考文献

[Git - 子模块](https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E5%AD%90%E6%A8%A1%E5%9D%97)

[git cherry-pick 教程 - 阮一峰的网络日志](https://www.ruanyifeng.com/blog/2020/04/git-cherry-pick.html)