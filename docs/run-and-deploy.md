# 本地运行与 GitHub Actions 部署

## 1. 本地运行

项目已经包含一个本地 SQLite 数据库文件：`instance/internship.sqlite3`。按照以下步骤即可在本机启动应用：

```bash
cd /Users/yinliu/Documents/python-internshipSystem
python3 -m venv .venv
source .venv/bin/activate
python run.py
```

启动后打开浏览器访问：

```
http://127.0.0.1:5000
```

如果你想自定义数据库路径，可以在启动前设置环境变量：

```bash
export APP_DB_BACKEND=sqlite
export APP_DB_NAME=instance/custom.sqlite3
```

## 2. GitHub Actions 自动构建与推送 Docker 镜像

如果你希望通过 GitHub Actions 构建并推送镜像，本仓库已添加以下工作流：

- `.github/workflows/docker-publish.yml`
- `Dockerfile`

工作流会在 `main` 分支 push 或手动触发时执行，构建镜像并推送到 GitHub Container Registry。

### 2.1 镜像名称

当前配置的镜像名称是：

```
ghcr.io/lynn61liu/python-internshipsystem:latest
```

> 如果你是其他 GitHub 用户或组织，请将 `lynn61liu` 替换为你的用户名或组织名。

### 2.2 手动拉取镜像

在服务器上手动拉取镜像：

```bash
docker pull ghcr.io/lynn61liu/python-internshipsystem:latest
```

或者如果你希望固定版本标签，可以在工作流中添加额外 tag，例如 `v1.0.0`，并手动拉取：

```bash
docker pull ghcr.io/lynn61liu/python-internshipsystem:v1.0.0
```

## 3. 运行容器

拉取镜像后，使用下面命令运行容器：

```bash
docker run -d --name internship-system -p 5000:5000 ghcr.io/lynn61liu/python-internshipsystem:latest
```

如果你希望上传和保留本地数据库文件，请为 `instance` 目录挂载一个持久卷：

```bash
docker run -d --name internship-system -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  ghcr.io/lynn61liu/python-internshipsystem:latest
```
