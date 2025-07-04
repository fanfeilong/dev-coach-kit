#!/usr/bin/env python3
"""
GitHub 团队信息收集器测试用例

测试功能：
- 基本的团队信息收集功能
- 数据解析和验证
- 输出文件生成
- 错误处理
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from team_info_collector import GitHubTeamInfoCollector, TeamMember, TeamInfo


class TestGitHubTeamInfoCollector:
    """GitHub 团队信息收集器测试类"""
    
    def __init__(self):
        self.test_token = "test_token"
        self.collector = GitHubTeamInfoCollector(self.test_token)
    
    def test_parse_team_info_valid(self):
        """测试有效的团队信息解析"""
        comment_body = """
## 团队信息提交

**团队名称：** Team Alpha

**团队成员信息：**
| 成员姓名 | 个人 GitHub ID | 个人 GitHub 链接 |
|----------|----------------|------------------|
| 张三     | zhangsan       | https://github.com/zhangsan |
| 李四     | lisi           | https://github.com/lisi     |
| 王五     | wangwu         | https://github.com/wangwu   |

**团队 GitHub 账户：** team-alpha  
**团队项目仓库：** https://github.com/team-alpha/project

**提交时间：** 2025-01-15
"""
        
        team_info = self.collector.parse_team_info(comment_body, 123, "test_user")
        
        assert team_info is not None, "团队信息解析应该成功"
        assert team_info.team_name == "Team Alpha", f"团队名称错误: {team_info.team_name}"
        assert len(team_info.members) == 3, f"成员数量错误: {len(team_info.members)}"
        assert team_info.team_github_account == "team-alpha", f"团队账户错误: {team_info.team_github_account}"
        assert team_info.team_repo_url == "https://github.com/team-alpha/project", f"仓库地址错误: {team_info.team_repo_url}"
        assert team_info.submission_time == "2025-01-15", f"提交时间错误: {team_info.submission_time}"
        
        # 验证成员信息
        expected_members = [
            ("张三", "zhangsan", "https://github.com/zhangsan"),
            ("李四", "lisi", "https://github.com/lisi"),
            ("王五", "wangwu", "https://github.com/wangwu")
        ]
        
        for i, (name, github_id, github_url) in enumerate(expected_members):
            member = team_info.members[i]
            assert member.name == name, f"成员{i+1}姓名错误: {member.name}"
            assert member.github_id == github_id, f"成员{i+1} GitHub ID错误: {member.github_id}"
            assert member.github_url == github_url, f"成员{i+1} GitHub URL错误: {member.github_url}"
        
        print("✅ 测试通过: 有效团队信息解析")
        return True
    
    def test_parse_team_info_invalid(self):
        """测试无效的团队信息解析"""
        invalid_comments = [
            "这是一个普通的评论",
            "**团队名称：** Team Test",  # 缺少成员表格
            "| 成员姓名 | GitHub ID | 链接 |\n|------|------|------|\n| 张三 | zhangsan | https://github.com/zhangsan |",  # 缺少团队名称
        ]
        
        for comment in invalid_comments:
            team_info = self.collector.parse_team_info(comment, 123, "test_user")
            assert team_info is None, f"无效评论应该返回None: {comment[:50]}..."
        
        print("✅ 测试通过: 无效团队信息解析")
        return True
    
    def test_validate_teams(self):
        """测试团队信息验证"""
        # 创建测试团队数据
        teams = [
            TeamInfo(
                team_name="Team Alpha",
                members=[TeamMember("张三", "zhangsan", "https://github.com/zhangsan")],
                team_github_account="team-alpha",
                team_repo_url="https://github.com/team-alpha/project",
                submission_time="2025-01-15",
                comment_id=123,
                comment_author="user1"
            ),
            TeamInfo(
                team_name="Team Alpha",  # 重复的团队名称
                members=[TeamMember("李四", "lisi", "https://github.com/lisi")],
                team_github_account="team-alpha-2",
                team_repo_url="invalid_url",  # 无效的URL
                submission_time="2025-01-15",
                comment_id=124,
                comment_author="user2"
            ),
            TeamInfo(
                team_name="",  # 空的团队名称
                members=[],  # 空的成员列表
                team_github_account="",
                team_repo_url="",
                submission_time="",
                comment_id=125,
                comment_author="user3"
            )
        ]
        
        issues = self.collector.validate_teams(teams, min_members=1, max_members=3)
        
        assert len(issues['duplicate_teams']) > 0, "应该检测到重复的团队名称"
        assert len(issues['invalid_urls']) > 0, "应该检测到无效的URL"
        assert len(issues['missing_info']) > 0, "应该检测到缺失的信息"
        
        print("✅ 测试通过: 团队信息验证")
        return True
    
    def test_export_functions(self):
        """测试导出功能"""
        # 创建测试团队数据
        teams = [
            TeamInfo(
                team_name="Test Team",
                members=[
                    TeamMember("张三", "zhangsan", "https://github.com/zhangsan"),
                    TeamMember("李四", "lisi", "https://github.com/lisi")
                ],
                team_github_account="test-team",
                team_repo_url="https://github.com/test-team/project",
                submission_time="2025-01-15",
                comment_id=123,
                comment_author="test_user"
            )
        ]
        
        # 使用临时目录测试导出
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_file = Path(temp_dir) / "test_teams.csv"
            json_file = Path(temp_dir) / "test_teams.json"
            
            # 测试CSV导出
            self.collector.export_to_csv(teams, str(csv_file))
            assert csv_file.exists(), "CSV 文件应该被创建"
            
            # 测试JSON导出
            self.collector.export_to_json(teams, str(json_file))
            assert json_file.exists(), "JSON 文件应该被创建"
            
            # 验证文件内容
            csv_content = csv_file.read_text(encoding='utf-8')
            assert "Test Team" in csv_content, "CSV 文件应该包含团队名称"
            assert "张三" in csv_content, "CSV 文件应该包含成员信息"
            
            json_content = json_file.read_text(encoding='utf-8')
            assert "Test Team" in json_content, "JSON 文件应该包含团队名称"
            assert "export_time" in json_content, "JSON 文件应该包含导出时间"
        
        print("✅ 测试通过: 导出功能")
        return True
    
    def test_with_mock_api(self):
        """测试模拟API调用"""
        # 模拟API响应
        mock_comments = [
            {
                'id': 123,
                'body': """
## 团队信息提交

**团队名称：** Mock Team

**团队成员信息：**
| 成员姓名 | 个人 GitHub ID | 个人 GitHub 链接 |
|----------|----------------|------------------|
| 测试用户 | testuser       | https://github.com/testuser |

**团队 GitHub 账户：** mock-team  
**团队项目仓库：** https://github.com/mock-team/project

**提交时间：** 2025-01-15
                """,
                'user': {'login': 'testuser'}
            }
        ]
        
        # 模拟API请求
        with patch.object(self.collector, 'get_issue_comments', return_value=mock_comments):
            teams = self.collector.collect_team_info("test/repo", 1)
            
            assert len(teams) == 1, f"应该收集到1个团队，实际收集到{len(teams)}个"
            team = teams[0]
            assert team.team_name == "Mock Team", f"团队名称错误: {team.team_name}"
            assert len(team.members) == 1, f"成员数量错误: {len(team.members)}"
            assert team.members[0].name == "测试用户", f"成员名称错误: {team.members[0].name}"
        
        print("✅ 测试通过: 模拟API调用")
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始运行 GitHub 团队信息收集器测试...")
        print("=" * 50)
        
        tests = [
            self.test_parse_team_info_valid,
            self.test_parse_team_info_invalid,
            self.test_validate_teams,
            self.test_export_functions,
            self.test_with_mock_api
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ 测试失败: {test.__name__}")
                print(f"   错误: {e}")
        
        print("=" * 50)
        print(f"🎉 测试完成: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("✅ 所有测试都通过了！")
            return True
        else:
            print("❌ 部分测试失败，请检查代码")
            return False


def run_demo_with_real_api():
    """使用真实API进行演示（需要有效的GitHub Token）"""
    print("\n🚀 GitHub 团队信息收集器 - 真实API演示")
    print("=" * 50)
    
    # 检查是否设置了 GitHub Token
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ 请设置环境变量 GITHUB_TOKEN 来运行真实API演示")
        print("   export GITHUB_TOKEN=your_github_token_here")
        return False
    
    # 示例参数（请根据实际情况修改）
    repo = "microsoft/vscode"  # 替换为有团队信息的仓库
    issue_number = 1  # 替换为实际的 Issue 编号
    
    print(f"📍 仓库: {repo}")
    print(f"📍 Issue: #{issue_number}")
    print("⚠️  注意：这将调用真实的 GitHub API")
    
    try:
        # 创建收集器实例
        collector = GitHubTeamInfoCollector(token)
        
        # 收集团队信息
        teams = collector.collect_team_info(repo, issue_number)
        
        if teams:
            print(f"\n✅ 成功收集到 {len(teams)} 个团队的信息")
            
            # 显示团队概览
            for i, team in enumerate(teams, 1):
                print(f"\n📋 团队 {i}: {team.team_name}")
                print(f"   👥 成员数: {len(team.members)}")
                print(f"   📅 提交时间: {team.submission_time}")
                print(f"   🏷️ 评论作者: {team.comment_author}")
            
            # 数据验证
            issues = collector.validate_teams(teams, min_members=1, max_members=5)
            if any(issues.values()):
                print("\n⚠️ 发现数据质量问题:")
                for category, problems in issues.items():
                    if problems:
                        print(f"   {category}: {len(problems)} 个问题")
            
            # 导出数据到测试目录
            print(f"\n💾 导出数据到测试目录...")
            test_dir = Path(__file__).parent / "output"
            test_dir.mkdir(exist_ok=True)
            
            csv_file = test_dir / "demo_teams.csv"
            json_file = test_dir / "demo_teams.json"
            
            collector.export_to_csv(teams, str(csv_file))
            collector.export_to_json(teams, str(json_file))
            
            print(f"\n🎉 演示完成！生成的文件:")
            print(f"   📄 {csv_file}")
            print(f"   📄 {json_file}")
            
            return True
            
        else:
            print("❌ 未找到任何团队信息")
            print("💡 请确保 Issue 中有符合格式的团队信息回复")
            return False
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        print("💡 请检查仓库名称、Issue 编号和 Token 权限")
        return False


def show_expected_format():
    """显示期望的团队信息格式"""
    print("📝 期望的团队信息格式:")
    print("=" * 50)
    format_example = """
## 团队信息提交

**团队名称：** Team Delta

**团队成员信息：**
| 成员姓名 | 个人 GitHub ID | 个人 GitHub 链接 |
|----------|----------------|------------------|
| 张三     | zhangsan       | https://github.com/zhangsan |
| 李四     | lisi           | https://github.com/lisi     |
| 王五     | wangwu         | https://github.com/wangwu   |

**团队 GitHub 账户：** sw-team-delta  
**团队项目仓库：** https://github.com/sw-team-delta/sw-project-demo

**提交时间：** 2025-01-15
"""
    print(format_example)
    print("=" * 50)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub 团队信息收集器测试')
    parser.add_argument('--mode', choices=['test', 'demo', 'format'], default='test',
                        help='运行模式: test(单元测试), demo(真实API演示), format(显示格式)')
    
    args = parser.parse_args()
    
    if args.mode == 'test':
        # 运行单元测试
        test_suite = TestGitHubTeamInfoCollector()
        success = test_suite.run_all_tests()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'demo':
        # 运行真实API演示
        success = run_demo_with_real_api()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'format':
        # 显示期望格式
        show_expected_format()
        sys.exit(0) 