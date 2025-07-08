#!/usr/bin/env python3
"""
测试多视图HTML功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from team_info_collector import GitHubTeamInfoCollector, TeamInfo, TeamMember
from datetime import datetime

def create_test_data():
    """创建测试数据"""
    teams = [
        TeamInfo(
            team_name="测试团队1",
            members=[
                TeamMember("张三", "zhangsan", "https://github.com/zhangsan"),
                TeamMember("李四", "lisi", "https://github.com/lisi"),
                TeamMember("王五", "wangwu", "https://github.com/wangwu")
            ],
            team_github_account="test-team-1",
            team_repo_url="https://github.com/test-team-1/project",
            submission_time="2024-01-15 10:30:00",
            comment_id=1,
            comment_author="张三"
        ),
        TeamInfo(
            team_name="测试团队2",
            members=[
                TeamMember("赵六", "zhaoliu", "https://github.com/zhaoliu"),
                TeamMember("钱七", "qianqi", "https://github.com/qianqi")
            ],
            team_github_account="test-team-2",
            team_repo_url="https://github.com/test-team-2/project",
            submission_time="2024-01-15 11:00:00",
            comment_id=2,
            comment_author="赵六"
        ),
        TeamInfo(
            team_name="测试团队3",
            members=[
                TeamMember("孙八", "sunba", "https://github.com/sunba"),
                TeamMember("周九", "zhoujiu", "https://github.com/zhoujiu"),
                TeamMember("吴十", "wushi", "https://github.com/wushi"),
                TeamMember("郑十一", "zhengshiyi", "https://github.com/zhengshiyi")
            ],
            team_github_account="test-team-3",
            team_repo_url="https://github.com/test-team-3/project",
            submission_time="2024-01-15 12:00:00",
            comment_id=3,
            comment_author="孙八"
        )
    ]
    return teams

def test_html_multiple_views():
    """测试多视图HTML功能"""
    print("🧪 测试多视图HTML功能...")
    
    # 创建测试数据
    teams = create_test_data()
    
    # 创建收集器实例
    collector = GitHubTeamInfoCollector("dummy-token")
    
    # 确保输出目录存在
    output_dir = "build"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成HTML报告
    html_filename = os.path.join(output_dir, "test_multiple_views_report.html")
    collector.export_to_html(teams, html_filename)
    
    # 检查文件是否生成
    if os.path.exists(html_filename):
        print(f"✅ HTML报告已生成: {html_filename}")
        
        # 检查文件内容
        with open(html_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查是否包含所有视图
        checks = [
            ("完整表格视图", "table-view"),
            ("紧凑表格视图", "compact-view"), 
            ("卡片视图", "cards-view"),
            ("切换按钮", "view-toggle"),
            ("JavaScript功能", "switchView"),
            ("CSS样式", "table-container"),
            ("团队卡片", "team-cards")
        ]
        
        all_passed = True
        for check_name, check_content in checks:
            if check_content in content:
                print(f"✅ {check_name} - 通过")
            else:
                print(f"❌ {check_name} - 失败")
                all_passed = False
        
        if all_passed:
            print("🎉 所有HTML功能测试通过！")
            print(f"📄 请打开 {html_filename} 查看多视图效果")
        else:
            print("⚠️ 部分HTML功能测试失败")
            
    else:
        print(f"❌ HTML报告生成失败: {html_filename}")

def test_view_switching():
    """测试视图切换功能"""
    print("\n🧪 测试视图切换功能...")
    
    # 创建测试数据
    teams = create_test_data()
    collector = GitHubTeamInfoCollector("dummy-token")
    
    # 生成HTML
    output_dir = "build"
    os.makedirs(output_dir, exist_ok=True)
    html_filename = os.path.join(output_dir, "test_view_switching.html")
    collector.export_to_html(teams, html_filename)
    
    # 检查JavaScript代码
    with open(html_filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查JavaScript函数
    if "function switchView" in content and "classList.remove" in content and "classList.add" in content:
        print("✅ JavaScript切换功能 - 通过")
    else:
        print("❌ JavaScript切换功能 - 失败")
    
    # 检查CSS类
    if "view-section" in content and "active" in content:
        print("✅ CSS视图控制 - 通过")
    else:
        print("❌ CSS视图控制 - 失败")

def test_responsive_design():
    """测试响应式设计"""
    print("\n🧪 测试响应式设计...")
    
    teams = create_test_data()
    collector = GitHubTeamInfoCollector("dummy-token")
    
    output_dir = "build"
    os.makedirs(output_dir, exist_ok=True)
    html_filename = os.path.join(output_dir, "test_responsive.html")
    collector.export_to_html(teams, html_filename)
    
    with open(html_filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查响应式CSS
    responsive_checks = [
        ("媒体查询", "@media"),
        ("视口设置", "viewport"),
        ("表格容器", "table-container"),
        ("横向滚动", "overflow-x"),
        ("网格布局", "grid-template-columns")
    ]
    
    all_passed = True
    for check_name, check_content in responsive_checks:
        if check_content in content:
            print(f"✅ {check_name} - 通过")
        else:
            print(f"❌ {check_name} - 失败")
            all_passed = False
    
    if all_passed:
        print("🎉 响应式设计测试通过！")

if __name__ == "__main__":
    print("🚀 开始测试多视图HTML功能...\n")
    
    test_html_multiple_views()
    test_view_switching()
    test_responsive_design()
    
    print("\n✨ 测试完成！")
    print("💡 提示：打开生成的HTML文件，测试以下功能：")
    print("   1. 点击不同的视图按钮，查看切换效果")
    print("   2. 调整浏览器窗口大小，查看响应式效果")
    print("   3. 在移动设备上查看，测试移动端适配") 