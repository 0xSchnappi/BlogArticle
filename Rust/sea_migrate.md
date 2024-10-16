# sea migrate
## install sea
```shell
cargo install sea-orm-cli
```
## 创建迁移目录
```shell
sea migrate init -d ./src/migrator
```
为了速度我们可以删除目录下的Cargo.toml和README.md文件
生成author表和book表
```shell
sea migrate generate -d ./src/migrator create_author_table
sea migrate generate -d ./src/migrator create_book_table 
```
生成数据库实例
```shell
sea generate entity -o src/entities -u mysql://username:password@localhost:3306/bookstore
```

# RSETful API 风格
| 方法 | 描述 |
| --- | --- |
| GET(SELECT) | 冲服务器取出资源(一项或多项) |
| POST(CREATE) | 在服务器新建一个资源 |
| PUT(UPDATE) | 在服务器更新资源(客户端提供完整资源数据) |
| PATCH(UPDATE) | 在服务器更新资源(客户端提供需要修改的资源数据) |
| DELETE(DELETE) | 从服务器删除资源 |
[参考资料](https://cloud.tencent.com/developer/article/2360813)