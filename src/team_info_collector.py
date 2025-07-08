#!/usr/bin/env python3
"""
GitHub 团队信息收集自动化脚本

功能：
- 从指定的 GitHub Issue 中提取所有团队信息回复
- 解析团队信息并转换为结构化数据
- 支持导出为 CSV 和 JSON 格式
- 提供数据验证和重复检查

使用方法：
python team_info_collector.py --repo owner/repo --issue 123 --token YOUR_TOKEN
"""

import os
import re
import json
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import requests
from dataclasses import dataclass, asdict
import markdown


@dataclass
class TeamMember:
    name: str
    github_id: str
    github_url: str


@dataclass
class TeamInfo:
    team_name: str
    members: List[TeamMember]
    team_github_account: str
    team_repo_url: str
    submission_time: str
    comment_id: int
    comment_author: str


class GitHubTeamInfoCollector:
    """GitHub 团队信息收集器"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_issue_comments(self, repo: str, issue_number: int) -> List[Dict]:
        """获取 Issue 的所有评论"""
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
        
        comments = []
        page = 1
        
        while True:
            params = {'page': page, 'per_page': 100}
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                print(f"❌ 获取评论失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                break
            
            page_comments = response.json()
            if not page_comments:
                break
                
            comments.extend(page_comments)
            page += 1
        
        print(f"📄 共获取到 {len(comments)} 条评论")
        return comments
    
    def parse_team_info(self, comment_body: str, comment_id: int, author: str) -> Optional[TeamInfo]:
        """解析评论中的团队信息"""
        
        # 检查是否包含团队信息标识
        if "团队信息提交" not in comment_body and "团队名称" not in comment_body:
            return None
        
        try:
            # 提取团队名称
            team_name_match = re.search(r'\*\*团队名称[：:]\*\*\s*(.+)', comment_body)
            if not team_name_match:
                return None
            team_name = team_name_match.group(1).strip()
            
            # 提取团队成员信息（表格格式）
            members = []
            table_pattern = r'\|([^|]+)\|([^|]+)\|([^|]+)\|'
            table_matches = re.findall(table_pattern, comment_body)
            
            for match in table_matches:
                name = match[0].strip()
                github_id = match[1].strip()
                github_url = match[2].strip()
                
                # 跳过表头和分隔行
                if (name in ['成员姓名', '-------', '姓名'] or 
                    github_id in ['个人 GitHub ID', '-------', 'GitHub ID'] or
                    '---' in name or '---' in github_id or '---' in github_url):
                    continue
                
                if name and github_id and github_url:
                    members.append(TeamMember(name, github_id, github_url))
            
            # 提取团队 GitHub 账户
            team_github_match = re.search(r'\*\*团队 GitHub 账户[：:]\*\*\s*(.+)', comment_body)
            team_github_account = team_github_match.group(1).strip() if team_github_match else ""
            
            # 提取团队仓库地址
            team_repo_match = re.search(r'\*\*团队项目仓库[：:]\*\*\s*(.+)', comment_body)
            team_repo_url = team_repo_match.group(1).strip() if team_repo_match else ""
            
            # 提取提交时间
            time_match = re.search(r'\*\*提交时间[：:]\*\*\s*(.+)', comment_body)
            submission_time = time_match.group(1).strip() if time_match else ""
            
            if team_name and members:
                return TeamInfo(
                    team_name=team_name,
                    members=members,
                    team_github_account=team_github_account,
                    team_repo_url=team_repo_url,
                    submission_time=submission_time,
                    comment_id=comment_id,
                    comment_author=author
                )
        
        except Exception as e:
            print(f"⚠️ 解析评论失败 (ID: {comment_id}): {e}")
        
        return None
    
    def collect_team_info(self, repo: str, issue_number: int) -> List[TeamInfo]:
        """收集所有团队信息"""
        print(f"🔍 开始收集 {repo} 仓库 Issue #{issue_number} 中的团队信息...")
        
        comments = self.get_issue_comments(repo, issue_number)
        teams = []
        
        for comment in comments:
            team_info = self.parse_team_info(
                comment['body'], 
                comment['id'], 
                comment['user']['login']
            )
            
            if team_info:
                teams.append(team_info)
                print(f"✅ 成功解析团队: {team_info.team_name}")
        
        print(f"📊 共收集到 {len(teams)} 个团队信息")
        return teams
    
    def export_to_csv(self, teams: List[TeamInfo], filename: str):
        """导出为 CSV 格式（团队信息，含编号）"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入表头
            writer.writerow([
                '团队编号', '团队名称', '成员1姓名', '成员1GitHub', '成员1链接',
                '成员2姓名', '成员2GitHub', '成员2链接',
                '成员3姓名', '成员3GitHub', '成员3链接',
                '团队GitHub账户', '团队仓库地址', '提交时间', '评论作者'
            ])
            
            # 写入数据（按编号顺序）
            for idx, team in enumerate(teams, 1):
                row = [str(idx), team.team_name]
                # 处理成员信息（最多3个成员）
                for i in range(3):
                    if i < len(team.members):
                        member = team.members[i]
                        row.extend([member.name, member.github_id, member.github_url])
                    else:
                        row.extend(['', '', ''])
                row.extend([
                    team.team_github_account,
                    team.team_repo_url,
                    team.submission_time,
                    team.comment_author
                ])
                writer.writerow(row)
        print(f"💾 团队信息 CSV 文件已保存: {filename} (UTF-8 with BOM，Excel 兼容)")

    def export_members_to_csv(self, teams: List[TeamInfo], filename: str):
        """导出为 CSV 格式（成员信息，含编号）"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            # 写入表头
            writer.writerow([
                '成员编号', '团队名称', '成员姓名', 'GitHub ID', 'GitHub 链接',
                '团队GitHub账户', '团队仓库地址', '提交时间', '评论作者'
            ])
            # 写入数据（每个成员一行，按编号顺序）
            idx = 1
            for team in teams:
                for member in team.members:
                    row = [str(idx), team.team_name, member.name, member.github_id, member.github_url,
                           team.team_github_account, team.team_repo_url, team.submission_time, team.comment_author]
                    writer.writerow(row)
                    idx += 1
        print(f"💾 成员信息 CSV 文件已保存: {filename} (UTF-8 with BOM，Excel 兼容)")
    
    def export_to_json(self, teams: List[TeamInfo], filename: str):
        """导出为 JSON 格式（团队信息）"""
        data = {
            'export_time': datetime.now().isoformat(),
            'total_teams': len(teams),
            'total_members': sum(len(team.members) for team in teams),
            'teams': [asdict(team) for team in teams]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 团队信息 JSON 文件已保存: {filename}")
    
    def export_members_to_json(self, teams: List[TeamInfo], filename: str):
        """导出为 JSON 格式（成员信息）"""
        members_data = []
        
        for team in teams:
            for member in team.members:
                member_info = {
                    'team_name': team.team_name,
                    'member_name': member.name,
                    'github_id': member.github_id,
                    'github_url': member.github_url,
                    'team_github_account': team.team_github_account,
                    'team_repo_url': team.team_repo_url,
                    'submission_time': team.submission_time,
                    'comment_author': team.comment_author
                }
                members_data.append(member_info)
        
        data = {
            'export_time': datetime.now().isoformat(),
            'total_members': len(members_data),
            'members': members_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 成员信息 JSON 文件已保存: {filename}")
    
    def export_to_markdown(self, teams: List[TeamInfo], filename: str):
        """导出为 Markdown 格式（包含团队和成员信息，含编号和汇总）"""
        # 汇总统计
        total_teams = len(teams)
        total_members = sum(len(team.members) for team in teams)
        group_sizes = {}
        for team in teams:
            n = len(team.members)
            group_sizes[n] = group_sizes.get(n, 0) + 1
        group_size_summary = ', '.join([f"{size}人组: {count}个" for size, count in sorted(group_sizes.items())])

        with open(filename, 'w', encoding='utf-8') as f:
            # 写入标题和统计信息
            f.write(f"# 📊 团队信息汇总报告\n\n")
            f.write(f"**导出时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**统计信息：**\n")
            f.write(f"- 总团队数：{total_teams}\n")
            f.write(f"- 总成员数：{total_members}\n")
            f.write(f"- 团队规模分布：{group_size_summary}\n\n")
            
            # 团队信息表格
            f.write("## 👥 团队信息\n\n")
            f.write("| 团队编号 | 团队名称 | 成员1姓名 | 成员1GitHub | 成员1链接 | 成员2姓名 | 成员2GitHub | 成员2链接 | 成员3姓名 | 成员3GitHub | 成员3链接 | 团队GitHub账户 | 团队仓库地址 | 提交时间 | 评论作者 |\n")
            f.write("|----------|----------|-----------|-------------|-----------|-----------|-------------|-----------|-----------|-------------|-----------|----------------|--------------|----------|----------|\n")
            for idx, team in enumerate(teams, 1):
                members_info = []
                for i in range(3):
                    if i < len(team.members):
                        member = team.members[i]
                        members_info.extend([member.name, member.github_id, member.github_url])
                    else:
                        members_info.extend(['', '', ''])
                row = [str(idx), team.team_name, *members_info, team.team_github_account, team.team_repo_url, team.submission_time, team.comment_author]
                f.write("| " + " | ".join(row) + " |\n")
            f.write("\n")
            # 成员信息表格
            f.write("## 👤 成员信息\n\n")
            f.write("| 成员编号 | 团队名称 | 成员姓名 | GitHub ID | GitHub 链接 | 团队GitHub账户 | 团队仓库地址 | 提交时间 | 评论作者 |\n")
            f.write("|----------|----------|----------|-----------|-------------|----------------|--------------|----------|----------|\n")
            idx = 1
            for team in teams:
                for member in team.members:
                    row = [str(idx), team.team_name, member.name, member.github_id, member.github_url, team.team_github_account, team.team_repo_url, team.submission_time, team.comment_author]
                    f.write("| " + " | ".join(row) + " |\n")
                    idx += 1
            f.write("\n")
            # 添加说明
            f.write("---\n\n")
            f.write("*本报告由 GitHub 团队信息收集器自动生成*")
        print(f"💾 Markdown 报告已保存: {filename}")
    
    def export_to_html(self, teams: List[TeamInfo], filename: str):
        """导出为 HTML 格式（包含团队和成员信息，含编号和汇总）"""
        # 汇总统计
        total_teams = len(teams)
        total_members = sum(len(team.members) for team in teams)
        group_sizes = {}
        for team in teams:
            n = len(team.members)
            group_sizes[n] = group_sizes.get(n, 0) + 1
        group_size_summary = ', '.join([f"{size}人组: {count}个" for size, count in sorted(group_sizes.items())])

        # 生成Markdown内容
        md_content = f"""# 📊 团队信息汇总报告

**导出时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**统计信息：**
- 总团队数：{total_teams}
- 总成员数：{total_members}
- 团队规模分布：{group_size_summary}

## 👥 团队信息

| 团队编号 | 团队名称 | 成员1姓名 | 成员1GitHub | 成员1链接 | 成员2姓名 | 成员2GitHub | 成员2链接 | 成员3姓名 | 成员3GitHub | 成员3链接 | 团队GitHub账户 | 团队仓库地址 | 提交时间 | 评论作者 |
|----------|----------|-----------|-------------|-----------|-----------|-------------|-----------|-----------|-------------|-----------|----------------|--------------|----------|----------|
"""
        
        for idx, team in enumerate(teams, 1):
            members_info = []
            for i in range(3):
                if i < len(team.members):
                    member = team.members[i]
                    members_info.extend([member.name, member.github_id, member.github_url])
                else:
                    members_info.extend(['', '', ''])
            row = [str(idx), team.team_name, *members_info, team.team_github_account, team.team_repo_url, team.submission_time, team.comment_author]
            md_content += "| " + " | ".join(row) + " |\n"
        
        md_content += "\n## 👤 成员信息\n\n"
        md_content += "| 成员编号 | 团队名称 | 成员姓名 | GitHub ID | GitHub 链接 | 团队GitHub账户 | 团队仓库地址 | 提交时间 | 评论作者 |\n"
        md_content += "|----------|----------|----------|-----------|-------------|----------------|--------------|----------|----------|\n"
        
        idx = 1
        for team in teams:
            for member in team.members:
                row = [str(idx), team.team_name, member.name, member.github_id, member.github_url, team.team_github_account, team.team_repo_url, team.submission_time, team.comment_author]
                md_content += "| " + " | ".join(row) + " |\n"
                idx += 1
        
        md_content += "\n---\n\n*本报告由 GitHub 团队信息收集器自动生成*"

        # 生成多种视图的HTML内容
        html_content = self._generate_html_with_multiple_views(teams, md_content)
        
        # 添加CSS样式
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>团队信息汇总报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e3f2fd;
        }}
        .stats {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .stats strong {{
            color: #2c3e50;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-style: italic;
        }}
        /* 表格容器，支持横向滚动 */
        .table-container {{
            overflow-x: auto;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .table-container table {{
            margin: 0;
            min-width: 800px; /* 确保表格有最小宽度 */
        }}
        /* 团队信息卡片样式 */
        .team-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .team-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .team-card h3 {{
            color: #2c3e50;
            margin: 0 0 10px 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }}
        .team-info {{
            margin-bottom: 15px;
        }}
        .team-info p {{
            margin: 5px 0;
            font-size: 14px;
        }}
        .team-info strong {{
            color: #34495e;
        }}
        .members-list {{
            list-style: none;
            padding: 0;
        }}
        .members-list li {{
            padding: 8px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }}
        .member-name {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .member-github {{
            color: #7f8c8d;
            font-size: 12px;
        }}
        /* 切换按钮样式 */
        .view-toggle {{
            margin: 20px 0;
            text-align: center;
        }}
        .view-toggle button {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        .view-toggle button:hover {{
            background: #2980b9;
        }}
        .view-toggle button.active {{
            background: #2c3e50;
        }}
        .view-section {{
            display: none;
        }}
        .view-section.active {{
            display: block;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .container {{
                padding: 15px;
            }}
            .team-cards {{
                grid-template-columns: 1fr;
            }}
            table {{
                font-size: 12px;
            }}
            th, td {{
                padding: 4px 6px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
    <script>
        // 切换视图功能
        function switchView(viewType) {{
            // 隐藏所有视图
            document.querySelectorAll('.view-section').forEach(section => {{
                section.classList.remove('active');
            }});
            // 显示选中的视图
            document.getElementById(viewType + '-view').classList.add('active');
            // 更新按钮状态
            document.querySelectorAll('.view-toggle button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"💾 HTML 报告已保存: {filename}")
    
    def _generate_html_with_multiple_views(self, teams: List[TeamInfo], markdown_content: str) -> str:
        """生成包含多种视图的HTML内容"""
        # 转换Markdown为HTML（表格视图）
        table_html = markdown.markdown(markdown_content, extensions=['tables'])
        
        # 生成卡片视图HTML
        cards_html = self._generate_cards_view(teams)
        
        # 生成紧凑表格视图HTML
        compact_html = self._generate_compact_table_view(teams)
        
        # 组合所有视图
        html_content = f"""
        <h1>📊 团队信息汇总报告</h1>
        
        <div class="view-toggle">
            <button onclick="switchView('compact')" class="active">📊 紧凑表格</button>
            <button onclick="switchView('table')">📋 完整表格</button>
            <button onclick="switchView('cards')">🃏 卡片视图</button>
        </div>
        
        <div id="compact-view" class="view-section active">
            <div class="table-container">
                {compact_html}
            </div>
        </div>
        
        <div id="table-view" class="view-section">
            <div class="table-container">
                {table_html}
            </div>
        </div>
        
        <div id="cards-view" class="view-section">
            {cards_html}
        </div>
        """
        
        return html_content
    
    def _generate_cards_view(self, teams: List[TeamInfo]) -> str:
        """生成卡片视图HTML"""
        cards_html = '<div class="team-cards">'
        
        for idx, team in enumerate(teams, 1):
            cards_html += f"""
            <div class="team-card">
                <h3>#{idx} {team.team_name}</h3>
                <div class="team-info">
                    <p><strong>团队GitHub账户：</strong>{team.team_github_account}</p>
                    <p><strong>团队仓库地址：</strong><a href="{team.team_repo_url}" target="_blank">{team.team_repo_url}</a></p>
                    <p><strong>提交时间：</strong>{team.submission_time}</p>
                    <p><strong>评论作者：</strong>{team.comment_author}</p>
                </div>
                <h4>团队成员：</h4>
                <ul class="members-list">
            """
            
            for member in team.members:
                cards_html += f"""
                    <li>
                        <div class="member-name">{member.name}</div>
                        <div class="member-github">
                            <a href="{member.github_url}" target="_blank">@{member.github_id}</a>
                        </div>
                    </li>
                """
            
            cards_html += """
                </ul>
            </div>
            """
        
        cards_html += '</div>'
        return cards_html
    
    def _generate_compact_table_view(self, teams: List[TeamInfo]) -> str:
        """生成紧凑表格视图HTML"""
        # 汇总统计
        total_teams = len(teams)
        total_members = sum(len(team.members) for team in teams)
        group_sizes = {}
        for team in teams:
            n = len(team.members)
            group_sizes[n] = group_sizes.get(n, 0) + 1
        group_size_summary = ', '.join([f"{size}人组: {count}个" for size, count in sorted(group_sizes.items())])
        
        compact_html = f"""
        <div class="stats">
            <strong>统计信息：</strong> 总团队数：{total_teams} | 总成员数：{total_members} | 团队规模分布：{group_size_summary}
        </div>
        
        <h2>👥 团队信息</h2>
        <table>
            <thead>
                <tr>
                    <th>编号</th>
                    <th>团队名称</th>
                    <th>成员数量</th>
                    <th>团队成员</th>
                    <th>团队GitHub账户</th>
                    <th>团队仓库地址</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for idx, team in enumerate(teams, 1):
            members_text = ', '.join([f"{member.name}(@{member.github_id})" for member in team.members])
            compact_html += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{team.team_name}</td>
                    <td>{len(team.members)}</td>
                    <td>{members_text}</td>
                    <td>{team.team_github_account}</td>
                    <td><a href="{team.team_repo_url}" target="_blank">查看仓库</a></td>
                </tr>
            """
        
        compact_html += """
            </tbody>
        </table>
        
        <h2>👤 成员信息</h2>
        <table>
            <thead>
                <tr>
                    <th>成员编号</th>
                    <th>团队名称</th>
                    <th>成员姓名</th>
                    <th>GitHub ID</th>
                    <th>GitHub 链接</th>
                    <th>团队GitHub账户</th>
                    <th>团队仓库地址</th>
                </tr>
            </thead>
            <tbody>
        """
        
        idx = 1
        for team in teams:
            for member in team.members:
                compact_html += f"""
                    <tr>
                        <td>{idx}</td>
                        <td>{team.team_name}</td>
                        <td>{member.name}</td>
                        <td>{member.github_id}</td>
                        <td><a href="{member.github_url}" target="_blank">@{member.github_id}</a></td>
                        <td>{team.team_github_account}</td>
                        <td><a href="{team.team_repo_url}" target="_blank">查看仓库</a></td>
                    </tr>
                """
                idx += 1
        
        compact_html += """
            </tbody>
        </table>
        """
        
        return compact_html
    
    def validate_teams(self, teams: List[TeamInfo], min_members: int = 1, max_members: int = 5) -> Dict[str, List[str]]:
        """验证团队信息并返回问题列表"""
        issues = {
            'missing_info': [],
            'duplicate_teams': [],
            'invalid_urls': [],
            'member_count_issues': []
        }
        
        team_names = set()
        
        for team in teams:
            # 检查重复团队名称
            if team.team_name in team_names:
                issues['duplicate_teams'].append(team.team_name)
            team_names.add(team.team_name)
            
            # 检查必填信息
            if not team.team_name or not team.members:
                issues['missing_info'].append(f"团队 {team.team_name} 信息不完整")
            
            # 检查成员数量
            if len(team.members) < min_members:
                issues['member_count_issues'].append(f"团队 {team.team_name} 成员数量过少 ({len(team.members)} < {min_members})")
            elif len(team.members) > max_members:
                issues['member_count_issues'].append(f"团队 {team.team_name} 成员数量过多 ({len(team.members)} > {max_members})")
            
            # 检查 URL 格式
            if team.team_repo_url and not team.team_repo_url.startswith('https://github.com/'):
                issues['invalid_urls'].append(f"团队 {team.team_name} 的仓库地址格式不正确")
        
        return issues


def main():
    parser = argparse.ArgumentParser(description='GitHub 团队信息收集器')
    parser.add_argument('--repo', required=True, help='GitHub 仓库 (格式: owner/repo)')
    parser.add_argument('--issue', type=int, required=True, help='Issue 编号')
    parser.add_argument('--token', help='GitHub Token (也可通过环境变量 GITHUB_TOKEN 设置)')
    parser.add_argument('--output', default='team_info', help='输出文件名前缀 (默认: team_info)')
    parser.add_argument('--output-dir', help='输出目录路径 (默认: ../data)')
    
    # 数据验证配置
    parser.add_argument('--min-members', type=int, default=1, help='最小团队成员数 (默认: 1)')
    parser.add_argument('--max-members', type=int, default=5, help='最大团队成员数 (默认: 5)')
    parser.add_argument('--no-validate', action='store_true', help='跳过数据验证')
    
    # 输出格式配置
    parser.add_argument('--no-csv', action='store_true', help='不导出 CSV 文件')
    parser.add_argument('--no-json', action='store_true', help='不导出 JSON 文件')
    parser.add_argument('--no-markdown', action='store_true', help='不导出 Markdown 报告')
    parser.add_argument('--no-html', action='store_true', help='不导出 HTML 报告')
    
    args = parser.parse_args()
    
    # 获取 GitHub Token
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ 请提供 GitHub Token (--token 参数或 GITHUB_TOKEN 环境变量)")
        return
    
    # 确定输出目录
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # 默认输出到根目录的 data 目录
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / 'data'
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录: {output_dir.absolute()}")
    
    # 创建收集器
    collector = GitHubTeamInfoCollector(token)
    
    # 收集团队信息
    teams = collector.collect_team_info(args.repo, args.issue)
    
    if not teams:
        print("❌ 未找到任何团队信息")
        return
    
    # 验证数据
    if not args.no_validate:
        issues = collector.validate_teams(teams, args.min_members, args.max_members)
        if any(issues.values()):
            print("\n⚠️ 数据验证发现问题:")
            for category, problems in issues.items():
                if problems:
                    print(f"  {category}: {problems}")
    else:
        print("⚠️ 已跳过数据验证")
    
    # 导出数据
    exported_files = []
    
    # 从仓库名提取文件名前缀
    repo_name = args.repo.replace('/', '_').replace('-', '_')
    
    # 导出团队信息 CSV
    if not args.no_csv:
        csv_filename = output_dir / f"{repo_name}_teams.csv"
        collector.export_to_csv(teams, str(csv_filename))
        exported_files.append(f"团队信息 CSV: {csv_filename}")
        
        # 导出成员信息 CSV
        members_csv_filename = output_dir / f"{repo_name}_members.csv"
        collector.export_members_to_csv(teams, str(members_csv_filename))
        exported_files.append(f"成员信息 CSV: {members_csv_filename}")
    
    # 导出团队信息 JSON
    if not args.no_json:
        json_filename = output_dir / f"{repo_name}_teams.json"
        collector.export_to_json(teams, str(json_filename))
        exported_files.append(f"团队信息 JSON: {json_filename}")
        
        # 导出成员信息 JSON
        members_json_filename = output_dir / f"{repo_name}_members.json"
        collector.export_members_to_json(teams, str(members_json_filename))
        exported_files.append(f"成员信息 JSON: {members_json_filename}")
    
    # 导出 Markdown 报告
    if not args.no_markdown:
        markdown_filename = output_dir / f"{repo_name}_report.md"
        collector.export_to_markdown(teams, str(markdown_filename))
        exported_files.append(f"Markdown 报告: {markdown_filename}")
    
    # 导出 HTML 报告
    if not args.no_html:
        html_filename = output_dir / f"{repo_name}_report.html"
        collector.export_to_html(teams, str(html_filename))
        exported_files.append(f"HTML 报告: {html_filename}")
    
    # 如果没有导出任何文件，显示警告
    if not exported_files:
        print("⚠️ 未导出任何文件 (使用了 --no-csv、--no-json、--no-markdown 和 --no-html 参数)")
    
    print(f"\n🎉 数据收集完成！")
    print(f"📈 统计信息:")
    print(f"  - 总团队数: {len(teams)}")
    print(f"  - 总成员数: {sum(len(team.members) for team in teams)}")
    
    for file_info in exported_files:
        print(f"  - {file_info}")


if __name__ == "__main__":
    main() 