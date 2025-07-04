# 🧪 测试用例

本目录包含 GitHub 团队信息收集器的测试用例。

## 📋 测试文件

- `test_team_info_collector.py` - 主测试文件，包含单元测试和演示功能

## 🚀 运行测试

### 1. 单元测试（推荐）

```bash
# 进入测试目录
cd tests

# 运行所有单元测试
python test_team_info_collector.py --mode test
```

### 2. 真实API演示

```bash
# 设置 GitHub Token
export GITHUB_TOKEN=your_github_token_here

# 运行真实API演示（需要有效的GitHub仓库和Issue）
python test_team_info_collector.py --mode demo
```

### 3. 显示期望格式

```bash
# 显示期望的团队信息格式
python test_team_info_collector.py --mode format
```

## 📊 测试功能

### 单元测试包含：

1. **有效团队信息解析测试**
   - 测试正确格式的团队信息解析
   - 验证团队名称、成员信息、GitHub账户等字段

2. **无效团队信息解析测试**
   - 测试各种无效格式的处理
   - 确保错误输入返回 None

3. **数据验证测试**
   - 测试重复团队名称检测
   - 测试无效URL检测
   - 测试缺失信息检测

4. **导出功能测试**
   - 测试CSV导出功能
   - 测试JSON导出功能
   - 验证文件内容正确性

5. **模拟API调用测试**
   - 使用模拟数据测试完整流程
   - 验证API响应处理

## 📁 测试输出

测试过程中生成的文件会存储在：
- `tests/output/` - 演示模式生成的文件
- 临时目录 - 单元测试使用的临时文件

## 🐛 故障排除

### 常见问题

1. **模块导入错误**
   ```
   ModuleNotFoundError: No module named 'team_info_collector'
   ```
   解决：确保从 `tests` 目录运行测试，脚本会自动添加 `src` 目录到 Python 路径

2. **API权限错误**
   ```
   ❌ 请设置环境变量 GITHUB_TOKEN
   ```
   解决：设置有效的 GitHub Token

3. **依赖包缺失**
   ```
   ModuleNotFoundError: No module named 'requests'
   ```
   解决：安装依赖包
   ```bash
   cd src
   pip install -r requirements.txt
   ```

## 📈 测试示例输出

### 单元测试成功输出：
```
🧪 开始运行 GitHub 团队信息收集器测试...
==================================================
✅ 测试通过: 有效团队信息解析
✅ 测试通过: 无效团队信息解析
✅ 测试通过: 团队信息验证
✅ 测试通过: 导出功能
✅ 测试通过: 模拟API调用
==================================================
🎉 测试完成: 5/5 个测试通过
✅ 所有测试都通过了！
```

### 真实API演示输出：
```
🚀 GitHub 团队信息收集器 - 真实API演示
==================================================
📍 仓库: microsoft/vscode
📍 Issue: #1
⚠️  注意：这将调用真实的 GitHub API
📄 共获取到 3 条评论
✅ 成功解析团队: Team Alpha
📊 共收集到 1 个团队信息

✅ 成功收集到 1 个团队的信息

📋 团队 1: Team Alpha
   👥 成员数: 3
   📅 提交时间: 2025-01-15
   🏷️ 评论作者: student1

💾 导出数据到测试目录...
💾 CSV 文件已保存: tests/output/demo_teams.csv
💾 JSON 文件已保存: tests/output/demo_teams.json

🎉 演示完成！生成的文件:
   📄 tests/output/demo_teams.csv
   📄 tests/output/demo_teams.json
```

## 🔧 开发和调试

如果需要调试或修改测试用例：

1. 编辑 `test_team_info_collector.py`
2. 添加新的测试方法到 `TestGitHubTeamInfoCollector` 类
3. 在 `run_all_tests` 方法中添加新测试到测试列表
4. 运行测试验证修改 