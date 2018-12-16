# w_lib
python 常用库集合

快速搭建项目

## 快速体验

> * python demo.py
>   * python demo.py table           # 终端表格
>   * python demo.py log             # 日志
>   * python demo.py hello "world"   
>   * python demo.py test_easyrun    # 执行 shell 命令
>   * python demo.py test_schema     # 参数检查

## 了解更多

> * https://github.com/meetbill/MyPythonLib

## 参加步骤

* 在 GitHub 上 `fork` 到自己的仓库，然后 `clone` 到本地，并设置用户信息。
```
$ git clone https://github.com/meetbill/w_lib.git
$ cd w_lib
$ git config user.name "yourname"
$ git config user.email "your email"
```
* 修改代码后提交，并推送到自己的仓库。
```
$ #do some change on the content
$ git commit -am "Fix issue #1: change helo to hello"
$ git push
```
* 在 GitHub 网站上提交 pull request。
* 定期使用项目仓库内容更新自己仓库内容。
```
$ git remote add upstream https://github.com/meetbill/w_lib.git
$ git fetch upstream
$ git checkout master
$ git rebase upstream/master
$ git push -f origin master
```
