# dev-coach-kit

软件开发教学指南+工具包

## 📖 文档指南

### 🧭 初始化指南
[GitHub账号和团队初始化指南](./doc/1.init.md)

### 📊 工具使用指南
[团队信息收集脚本使用指南](./doc/2.team_info_collector.md)

### 🎨 解决方案文档
[HTML多视图解决方案](./doc/3.html_multiple_views_solution.md)

### 🔧 Git 使用指南
[Git 基础教程与最佳实践](./doc/4.git.md)

## 🛠️ 工具包

### 📊 团队信息收集器
位于 `src/team_info_collector.py` 的自动化脚本，帮助教师从 GitHub Issues 中批量收集和整理学生团队信息。

**主要功能：**
- 🔍 自动从 GitHub Issues 评论中提取团队信息
- 📊 数据验证和重复检查
- 💾 导出 CSV 和 JSON 格式报告
- 📈 生成统计分析
- 🔧 灵活的命令行配置

**快速开始：**
```bash
cd src
pip install -r requirements.txt
export GITHUB_TOKEN=your_github_token_here
python team_info_collector.py --repo owner/repo --issue 1
```

## 🧪 测试

### 📋 运行测试
```bash
cd tests
python test_team_info_collector.py --mode test
```

---

## 📋 项目结构

```
dev-coach-kit/
├── doc/                        # 文档指南
│   ├── 1.init.md              # GitHub 账号和团队初始化指南
│   ├── 2.team_info_collector.md # 团队信息收集脚本使用指南
│   ├── 3.html_multiple_views_solution.md # HTML多视图解决方案
│   ├── 4.git.md               # Git 基础教程与最佳实践
│   └── images/                # 文档图片资源
├── src/                       # 工具包
│   ├── team_info_collector.py # 团队信息收集主脚本
│   └── requirements.txt       # 依赖列表
├── tests/                     # 测试用例
│   ├── test_team_info_collector.py # 测试用例
│   └── README.md             # 测试文档
├── data/                      # 数据输出目录
│   ├── team_info_*.csv       # 团队信息 CSV 文件
│   └── team_info_*.json      # 团队信息 JSON 文件
└── README.md                  # 项目总览
```
