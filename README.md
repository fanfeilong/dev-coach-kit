# dev-coach-kit

软件开发教学指南+工具包

## 📖 文档

### 🧭 初始化指南
[如何初始化Github账号和团队账号](./doc/1.init.md)

## 🤖 自动化工具

### 📊 团队信息收集器
位于 `src/team_info_collector.py` 的自动化脚本，帮助教师从 GitHub Issues 中批量收集和整理学生团队信息。

**主要功能：**
- 🔍 自动从 GitHub Issues 评论中提取团队信息
- 📊 数据验证和重复检查（可配置成员数限制）
- 💾 导出 CSV 和 JSON 格式报告（可选择格式）
- 📈 生成统计分析
- 🔧 灵活的命令行配置（无需配置文件）
- ⚠️ 可选的数据验证（支持跳过验证）

**快速开始：**
```bash
cd src
pip install -r requirements.txt
export GITHUB_TOKEN=your_github_token_here

# 基本使用
python team_info_collector.py --repo owner/repo --issue 1

# 配置团队规模验证
python team_info_collector.py --repo owner/repo --issue 1 --min-members 2 --max-members 4

# 只导出CSV格式
python team_info_collector.py --repo owner/repo --issue 1 --no-json
```

详细使用说明请参考 [团队信息收集脚本使用指南](./doc/2.team_info_collector.md)。

## 🧪 测试

### 📋 运行测试
```bash
cd tests
python test_team_info_collector.py --mode test
```

### 📊 测试功能
- 单元测试（数据解析、验证、导出）
- 真实API演示
- 格式展示

详细测试说明请参考 [tests/README.md](./tests/README.md)。

---

## 📋 项目结构

```
dev-coach-kit/
├── data/                        # 数据输出目录
│   ├── team_info_*.csv         # 团队信息 CSV 文件
│   └── team_info_*.json        # 团队信息 JSON 文件
├── doc/
│   ├── 1.init.md               # GitHub 账号和团队初始化指南
│   └── 2.team_info_collector.md # 团队信息收集脚本使用指南
├── src/
│   ├── team_info_collector.py  # 团队信息收集主脚本
│   └── requirements.txt        # 依赖列表
├── tests/
│   ├── test_team_info_collector.py  # 测试用例
│   └── README.md              # 测试文档
└── README.md                   # 项目总览
```
