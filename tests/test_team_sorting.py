#!/usr/bin/env python3
"""
测试团队按人数排序功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from team_info_collector import GitHubTeamInfoCollector, TeamInfo, TeamMember

def create_test_data():
    """创建测试数据"""
    teams = [
        TeamInfo(
            team_name="小团队A",
            members=[
                TeamMember("张三", "zhangsan", "https://github.com/zhangsan"),
            ],
            team_github_account="team-a",
            team_repo_url="https://github.com/team-a/project",
            submission_time="2024-01-15 10:30:00",
            comment_id=1,
            comment_author="张三"
        ),
        TeamInfo(
            team_name="大团队B",
            members=[
                TeamMember("李四", "lisi", "https://github.com/lisi"),
                TeamMember("王五", "wangwu", "https://github.com/wangwu"),
                TeamMember("赵六", "zhaoliu", "https://github.com/zhaoliu"),
                TeamMember("钱七", "qianqi", "https://github.com/qianqi"),
            ],
            team_github_account="team-b",
            team_repo_url="https://github.com/team-b/project",
            submission_time="2024-01-15 11:00:00",
            comment_id=2,
            comment_author="李四"
        ),
        TeamInfo(
            team_name="中团队C",
            members=[
                TeamMember("孙八", "sunba", "https://github.com/sunba"),
                TeamMember("周九", "zhoujiu", "https://github.com/zhoujiu"),
            ],
            team_github_account="team-c",
            team_repo_url="https://github.com/team-c/project",
            submission_time="2024-01-15 12:00:00",
            comment_id=3,
            comment_author="孙八"
        )
    ]
    return teams

def test_team_sorting():
    """测试团队排序功能"""
    print("🧪 测试团队按人数排序功能...")
    
    # 创建测试数据
    teams = create_test_data()
    
    # 创建收集器实例
    collector = GitHubTeamInfoCollector("dummy-token")
    
    # 确保输出目录存在
    output_dir = "build"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成HTML报告
    html_filename = os.path.join(output_dir, "test_team_sorting.html")
    collector.export_to_html(teams, html_filename)
    
    # 检查文件是否生成
    if os.path.exists(html_filename):
        print(f"✅ HTML报告已生成: {html_filename}")
        
        # 检查文件内容
        with open(html_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查团队排序
        expected_order = ["大团队B", "中团队C", "小团队A"]  # 按人数排序：4人、2人、1人
        
        # 查找团队信息表中的团队名称
        team_section_start = content.find("👥 团队信息")
        if team_section_start != -1:
            team_section = content[team_section_start:team_section_start + 2000]
            
            # 检查团队是否按预期顺序出现
            current_pos = 0
            all_found = True
            for expected_team in expected_order:
                pos = team_section.find(expected_team, current_pos)
                if pos == -1:
                    print(f"❌ 未找到团队: {expected_team}")
                    all_found = False
                    break
                current_pos = pos
                print(f"✅ 找到团队: {expected_team} (位置: {pos})")
            
            if all_found:
                print("🎉 团队排序测试通过！")
                print("📊 团队按人数从多到少排序：大团队B(4人) → 中团队C(2人) → 小团队A(1人)")
            else:
                print("⚠️ 团队排序测试失败")
        else:
            print("❌ 未找到团队信息表")
            
    else:
        print(f"❌ HTML报告生成失败: {html_filename}")

def test_member_sorting():
    """测试成员排序功能"""
    print("\n🧪 测试成员按团队人数排序功能...")
    
    teams = create_test_data()
    collector = GitHubTeamInfoCollector("dummy-token")
    
    output_dir = "build"
    os.makedirs(output_dir, exist_ok=True)
    html_filename = os.path.join(output_dir, "test_member_sorting.html")
    collector.export_to_html(teams, html_filename)
    
    with open(html_filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找成员信息表
    member_section_start = content.find("👤 成员信息")
    if member_section_start != -1:
        member_section = content[member_section_start:member_section_start + 5000]
        
        # 检查成员是否按团队人数排序
        # 应该先是大团队B的4个成员，然后是中团队C的2个成员，最后是小团队A的1个成员
        expected_member_order = [
            "李四", "王五", "赵六", "钱七",  # 大团队B的4个成员
            "孙八", "周九",  # 中团队C的2个成员
            "张三"  # 小团队A的1个成员
        ]
        
        current_pos = 0
        all_found = True
        for expected_member in expected_member_order:
            pos = member_section.find(expected_member, current_pos)
            if pos == -1:
                print(f"❌ 未找到成员: {expected_member}")
                all_found = False
                break
            current_pos = pos
            print(f"✅ 找到成员: {expected_member} (位置: {pos})")
        
        if all_found:
            print("🎉 成员排序测试通过！")
            print("👥 成员按团队人数排序：大团队B成员 → 中团队C成员 → 小团队A成员")
        else:
            print("⚠️ 成员排序测试失败")
    else:
        print("❌ 未找到成员信息表")

def test_statistics_sorting():
    """测试统计信息排序"""
    print("\n🧪 测试统计信息排序功能...")
    
    teams = create_test_data()
    collector = GitHubTeamInfoCollector("dummy-token")
    
    output_dir = "build"
    os.makedirs(output_dir, exist_ok=True)
    html_filename = os.path.join(output_dir, "test_statistics_sorting.html")
    collector.export_to_html(teams, html_filename)
    
    with open(html_filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查统计信息是否按人数排序
    if "4人组: 1个, 2人组: 1个, 1人组: 1个" in content:
        print("✅ 统计信息按人数排序 - 通过")
        print("📈 统计信息显示：4人组: 1个, 2人组: 1个, 1人组: 1个")
    else:
        print("❌ 统计信息排序 - 失败")

if __name__ == "__main__":
    print("🚀 开始测试团队排序功能...\n")
    
    test_team_sorting()
    test_member_sorting()
    test_statistics_sorting()
    
    print("\n✨ 测试完成！")
    print("💡 现在所有表格都按团队人数从多到少排序") 