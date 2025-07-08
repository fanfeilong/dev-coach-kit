#!/usr/bin/env python3
"""
HTML多视图功能演示
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from team_info_collector import GitHubTeamInfoCollector, TeamInfo, TeamMember

def create_demo_data():
    """创建演示数据"""
    teams = [
        TeamInfo(
            team_name="创新团队Alpha",
            members=[
                TeamMember("张三", "zhangsan2024", "https://github.com/zhangsan2024"),
                TeamMember("李四", "lisi-dev", "https://github.com/lisi-dev"),
                TeamMember("王五", "wangwu-coder", "https://github.com/wangwu-coder")
            ],
            team_github_account="team-alpha-2024",
            team_repo_url="https://github.com/team-alpha-2024/innovative-project",
            submission_time="2024-01-15 10:30:00",
            comment_id=1,
            comment_author="张三"
        ),
        TeamInfo(
            team_name="技术团队Beta",
            members=[
                TeamMember("赵六", "zhaoliu-tech", "https://github.com/zhaoliu-tech"),
                TeamMember("钱七", "qianqi-ai", "https://github.com/qianqi-ai"),
                TeamMember("孙八", "sunba-ml", "https://github.com/sunba-ml"),
                TeamMember("周九", "zhoujiu-backend", "https://github.com/zhoujiu-backend")
            ],
            team_github_account="team-beta-tech",
            team_repo_url="https://github.com/team-beta-tech/ai-platform",
            submission_time="2024-01-15 11:15:00",
            comment_id=2,
            comment_author="赵六"
        ),
        TeamInfo(
            team_name="设计团队Gamma",
            members=[
                TeamMember("吴十", "wushi-design", "https://github.com/wushi-design"),
                TeamMember("郑十一", "zhengshiyi-ui", "https://github.com/zhengshiyi-ui")
            ],
            team_github_account="team-gamma-design",
            team_repo_url="https://github.com/team-gamma-design/ux-design-system",
            submission_time="2024-01-15 12:00:00",
            comment_id=3,
            comment_author="吴十"
        ),
        TeamInfo(
            team_name="全栈团队Delta",
            members=[
                TeamMember("王十二", "wangshier-fullstack", "https://github.com/wangshier-fullstack"),
                TeamMember("李十三", "lishisan-devops", "https://github.com/lishisan-devops"),
                TeamMember("张十四", "zhangshisi-frontend", "https://github.com/zhangshisi-frontend"),
                TeamMember("刘十五", "liushiwu-backend", "https://github.com/liushiwu-backend"),
                TeamMember("陈十六", "chenshiliu-mobile", "https://github.com/chenshiliu-mobile")
            ],
            team_github_account="team-delta-fullstack",
            team_repo_url="https://github.com/team-delta-fullstack/comprehensive-app",
            submission_time="2024-01-15 13:30:00",
            comment_id=4,
            comment_author="王十二"
        )
    ]
    return teams

def main():
    """主函数"""
    print("🎨 HTML多视图功能演示")
    print("=" * 50)
    
    # 创建演示数据
    teams = create_demo_data()
    print(f"📊 创建了 {len(teams)} 个演示团队")
    
    # 创建收集器实例
    collector = GitHubTeamInfoCollector("demo-token")
    
    # 确保输出目录存在
    output_dir = "build"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成HTML报告
    html_filename = os.path.join(output_dir, "demo_multiple_views.html")
    collector.export_to_html(teams, html_filename)
    
    print(f"✅ HTML演示报告已生成: {html_filename}")
    print("\n🎯 演示功能说明：")
    print("1. 📋 完整表格视图 - 显示所有详细信息，支持横向滚动")
    print("2. 📊 紧凑表格视图 - 简化结构，快速浏览团队概况")
    print("3. 🃏 卡片视图 - 美观的卡片布局，适合移动设备")
    print("\n💡 使用提示：")
    print("- 点击顶部的视图切换按钮体验不同视图")
    print("- 调整浏览器窗口大小查看响应式效果")
    print("- 在移动设备上打开，体验移动端适配")
    print("- 卡片视图特别适合小屏幕设备")
    
    # 显示统计信息
    total_members = sum(len(team.members) for team in teams)
    print(f"\n📈 演示数据统计：")
    print(f"- 团队数量：{len(teams)}")
    print(f"- 成员总数：{total_members}")
    print(f"- 平均团队规模：{total_members/len(teams):.1f}人")
    
    print(f"\n🚀 请打开 {html_filename} 开始体验多视图功能！")

if __name__ == "__main__":
    main() 