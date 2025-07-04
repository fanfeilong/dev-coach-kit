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
        """导出为 CSV 格式"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入表头
            writer.writerow([
                '团队名称', '成员1姓名', '成员1GitHub', '成员1链接',
                '成员2姓名', '成员2GitHub', '成员2链接',
                '成员3姓名', '成员3GitHub', '成员3链接',
                '团队GitHub账户', '团队仓库地址', '提交时间', '评论作者'
            ])
            
            # 写入数据
            for team in teams:
                row = [team.team_name]
                
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
        
        print(f"💾 CSV 文件已保存: {filename}")
    
    def export_to_json(self, teams: List[TeamInfo], filename: str):
        """导出为 JSON 格式"""
        data = {
            'export_time': datetime.now().isoformat(),
            'total_teams': len(teams),
            'teams': [asdict(team) for team in teams]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 JSON 文件已保存: {filename}")
    
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
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    exported_files = []
    
    # 导出 CSV
    if not args.no_csv:
        csv_filename = output_dir / f"{args.output}_{timestamp}.csv"
        collector.export_to_csv(teams, str(csv_filename))
        exported_files.append(f"CSV 文件: {csv_filename}")
    
    # 导出 JSON
    if not args.no_json:
        json_filename = output_dir / f"{args.output}_{timestamp}.json"
        collector.export_to_json(teams, str(json_filename))
        exported_files.append(f"JSON 文件: {json_filename}")
    
    # 如果没有导出任何文件，显示警告
    if not exported_files:
        print("⚠️ 未导出任何文件 (使用了 --no-csv 和 --no-json 参数)")
    
    print(f"\n🎉 数据收集完成！")
    print(f"📈 统计信息:")
    print(f"  - 总团队数: {len(teams)}")
    print(f"  - 总成员数: {sum(len(team.members) for team in teams)}")
    
    for file_info in exported_files:
        print(f"  - {file_info}")


if __name__ == "__main__":
    main() 