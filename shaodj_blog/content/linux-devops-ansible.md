Title: DevOps工程师最常用的可重用Playbook
Slug: linux-devops-ansible-playbook
Date: 2025-02-21 16:18
Category: 运维
Tags: blog, linux, python, devops

最重要常用的 7个 Ansible Playbook
```python
ansible-playbook -i lists-hosts ops.yaml -e "host=OPK-JUMPS" 
```

# 1. 安装常用软件包的 Playbook
此 Playbook 确保在所有服务器上安装常用的系统工具。


```python
---
- name: 安装常用软件包
  hosts: "{{ host }}"
  become: yes
  tasks:
    - name: 更新软件包列表
      package:
        update_cache:  yes
    - name: 安装必备软件包
      package:
        name:
          - curl
          - vim
          - git
          - unzip
        state: present
```
- become: yes: 确保任务以 sudo 权限执行。


# 2. 用户账户管理的 Playbook
此 Playbook 创建具有特定权限的用户账户。

```python
---
- name: 管理用户账号
  hosts: "{{ host }}"
  become: yes
  tasks:
    - name: 创建新用户
      user:
        name: devops
        shell: /bin/bash
        state: present
        groups: wheel
    - name: 为用户设置密码
      authorized_key:
        user: devops
        key: "{{ lookup('file', '/root/.ssh/id_rsa.pub''') }}"
        state: present
```
- user 模块: 创建新用户（‘devops’）并将其分配到 ‘sudo’ 组。
- authorized_key 模块: 添加 SSH 密钥以保障安全访问。
 
# 3. 配置 Nginx 的 Playbook
使用此 Playbook 安装并配置 Nginx Web 服务器。
```python
---
- name: 安装并配置Nginx
  hosts: "{{ host }}"
  become: yes
  tasks:
    - name: 安装Nginx
      package:
        name: nginx
        state: present
    - name: 复制Nginx配置文件
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
    - name: 重启Nginx
      service:
        name: nginx
        state: restarted
```
- template 模块: 将 Jinja2 模板复制到服务器以实现动态配置。
- service 模块: 确保 Nginx 在配置更改后重启。

# 4. 防火墙配置的 Playbook
此 Playbook 使用 UFW 配置基本防火墙。

```python
---
- name: 配置UFW防火墙
  hosts: "{{ host }}"
  become: yes
  tasks:
    - name: 允许SSH连接
      ufw:
        rule: allow
        port: 22
    - name: 允许HTTP和HTTPS流量
      ufw:
        rule: allow
        port: "{{ item }}"
      loop:
        - 80
        - 443
    - name: 启用UFW
      ufw:
        state: enabled
```
- ufw 模块: 配置 Uncomplicated Firewall (UFW)，允许 SSH (22) 和 Web 流量 (80, 443) 等必要端口。


# 5. 应用部署的 Playbook
使用此可重用 Playbook 自动化应用部署。
```python
---
- name: 部署PythonWeb应用
  hosts: "{{ host }}"
  become: yes
  tasks:
    - name: 安装Python依赖
      package:
        name:
          - python3
          - python3-pip
        state: present
    - name: 安装所需的Python包
      pip:
        name:
          - flask
          - gunicorn
    - name: 复制应用代码
      copy:
        src: /local/path/to/app
        dest: /var/www/myapp
    - name: 启动应用
      shell: |
        nohup gunicorn -b 0.0.0.0:8000 app:app &
      args:
        chdir: /var/www/myapp
```
- pip 模块: 安装 Flask 和 Gunicorn 等 Python 包。
- shell 模块: 使用 Gunicorn 作为后台进程启动应用。

# 6. 数据库设置的 Playbook
快速设置并保护 MySQL 数据库。
```python
---
- name: 设置MySQL
  hosts: db_servers
  become: yes
  tasks:
    - name: 安装MySQL服务器
      package:
        name: mysql-server
        state: present
    - name: 设置MySQLroot密码
      mysql_user:
        login_user: root
        login_password: ""
        name: root
        password: secure_password
        host_all: true
        state: present
```
- mysql_user 模块: 创建并保护 MySQL 的 root 用户。


# 7. 系统监控的 Playbook
自动化安装 Prometheus 和 Node Exporter 等监控工具。
```python
---
- name: 设置系统监控
  hosts: "{{ host }}"
  become: yes
  tasks:
    - name: 安装NodeExporter
      get_url:
        url: https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz
        dest: /tmp/node_exporter.tar.gz
    - name: 解压NodeExporter
      unarchive:
        src: /tmp/node_exporter.tar.gz
        dest: /usr/local/bin/
        extra_opts: ["--strip-components=1"]  # 去掉一层目录结构
        remote_src: yes
    - name: 启动NodeExporter
      shell: |
        nohup /usr/local/bin/node_exporter &
```
- get_url 模块: 下载 Node Exporter 二进制文件。
- unarchive 模块: 将二进制文件解压到指定位置。



