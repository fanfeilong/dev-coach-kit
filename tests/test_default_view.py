#!/usr/bin/env python3
"""
测试默认视图设置
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from team_info_collector import GitHubTeamInfoCollector, TeamInfo, TeamMember

def create_test_data():
    """创建测试数据"""
    teams = [
        TeamInfo(
            team_name="测试团队",
            members=[
                TeamMember("张三", "zhangsan", "https://github.com/zhangsan"),
                TeamMember("李四", "lisi", "https://github.com/lisi")
            ],
            team_github_account="test-team",
            team_repo_url="https://github.com/test-team/project",
            submission_time="2024-01-15 10:30:00",
            comment_id=1,
            comment_author="张三"
        )
    ]
    return teams

def test_default_view():
    """测试默认视图设置"""
    print("🧪 测试默认视图设置...")
    
    # 创建测试数据
    teams = create_test_data()
    
    # 创建收集器实例
    collector = GitHubTeamInfoCollector("dummy-token")
    
    # 确保输出目录存在
    output_dir = "build"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成HTML报告
    html_filename = os.path.join(output_dir, "test_default_view.html")
    collector.export_to_html(teams, html_filename)
    
    # 检查文件是否生成
    if os.path.exists(html_filename):
        print(f"✅ HTML报告已生成: {html_filename}")
        
        # 检查文件内容
        with open(html_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查默认视图设置
        checks = [
            ("紧凑表格按钮为默认", "switchView('compact')" in content and "class=\"active\"" in content),
            ("紧凑视图为默认显示", "id=\"compact-view\" class=\"view-section active\"" in content),
            ("包含团队信息表", "👥 团队信息" in content),
            ("包含成员信息表", "👤 成员信息" in content),
            ("按钮顺序正确", content.find("紧凑表格") < content.find("完整表格"))
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name} - 通过")
            else:
                print(f"❌ {check_name} - 失败")
                all_passed = False
        
        if all_passed:
            print("🎉 默认视图设置测试通过！")
            print("📊 紧凑表格视图现在是默认视图")
            print("📋 包含团队信息和成员信息两张表")
        else:
            print("⚠️ 部分默认视图设置测试失败")
            
    else:
        print(f"❌ HTML报告生成失败: {html_filename}")

def test_compact_tables():
    """测试紧凑表格包含两张表"""
    print("\n🧪 测试紧凑表格包含两张表...")
    
    teams = create_test_data()
    collector = GitHubTeamInfoCollector("dummy-token")
    
    output_dir = "build"
    os.makedirs(output_dir, exist_ok=True)
    html_filename = os.path.join(output_dir, "test_compact_tables.html")
    collector.export_to_html(teams, html_filename)
    
    with open(html_filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含两张表
    table_checks = [
        ("团队信息表标题", "👥 团队信息" in content),
        ("成员信息表标题", "👤 成员信息" in content),
        ("团队表列头", "团队名称" in content and "成员数量" in content),
        ("成员表列头", "成员姓名" in content and "GitHub ID" in content),
        ("表格数据", "测试团队" in content and "张三" in content)
    ]
    
    all_passed = True
    for check_name, check_result in table_checks:
        if check_result:
            print(f"✅ {check_name} - 通过")
        else:
            print(f"❌ {check_name} - 失败")
            all_passed = False
    
    if all_passed:
        print("🎉 紧凑表格两张表测试通过！")

if __name__ == "__main__":
    print("🚀 开始测试默认视图设置...\n")
    
    test_default_view()
    test_compact_tables()
    
    print("\n✨ 测试完成！")
    print("💡 现在HTML报告默认显示紧凑表格视图，包含团队和个人两张表") 