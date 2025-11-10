
以下是 pip（Python 包管理工具）的常用命令及其示例：

## 1. 安装包

### 安装最新版本

```bash
pip install <包名>
```

示例：

```bash
pip install requests
```

### 安装指定版本

```bash
pip install <包名>==<版本号>
```

示例：

```bash
pip install requests==2.26.0
```

### 安装多个包（从文件）

```bash
pip install -r requirements.txt
```

示例：

```bash
# requirements.txt 文件内容示例
requests==2.26.0
numpy>=1.21.0
```

## 2. 卸载包

```bash
pip uninstall <包名>
```

示例：

```bash
pip uninstall requests
```

## 3. 查看已安装的包

### 列出所有已安装的包

```bash
pip list
```

### 查看特定包的版本

```bash
pip show <包名>
```

示例：

```bash

pip show requests
```

## 4. 更新包

### 更新到最新版本

```bash
pip install --upgrade <包名>
```

示例：

```bash
pip install --upgrade requests
```

### 更新 pip 本身

```bash
pip install --upgrade pip
```

## 5. 搜索包

```bash
pip search <关键词>
```

示例：

```bash

pip search requests
```
注意：pip search 可能在部分新版中不可用，推荐直接查阅 PyPI。

## 6. 生成和冻结依赖文件

### 生成当前环境的依赖文件

```bash
pip freeze > requirements.txt
```

### 使用冻结的依赖文件重新安装环境

```bash
pip install -r requirements.txt
```

## 7. 检查依赖

```bash
pip check
```

检查当前环境中是否存在依赖问题（如版本冲突）。

## 8. 安装本地包

```bash
pip install <路径>
```

示例：

```bash
pip install ./my_package/
```

## 9. 使用代理安装

如果网络受限，可以使用代理：

```bash
pip install <包名> --proxy="http://<代理地址>:<端口>"
```

示例：

```bash

pip install requests --proxy="http://127.0.0.1:8080"
```

## 10. 使用特定的源

可以使用国内镜像源加速安装，例如清华源或阿里源：

### 临时使用

```bash
pip install <包名> -i <镜像地址>
```

示例：

```bash
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 设置全局源

```bash
pip config set global.index-url <镜像地址>
```

示例：

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 11. 查看帮助

```bash
pip --help
```

常见镜像源
清华源：https://pypi.tuna.tsinghua.edu.cn/simple
阿里源：https://mirrors.aliyun.com/pypi/simple/
豆瓣源：https://pypi.douban.com/simple

## 12. 实用示例

1. 安装 Flask，并将依赖保存到文件

```bash
pip install flask
pip freeze > requirements.txt
```

2. 使用依赖文件还原环境

```bash
pip install -r requirements.txt
```

3. 设置国内镜像，并安装包

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install pandas
```

这些是 pip 的核心命令和使用场景，结合实际需要可以轻松管理 Python 包！