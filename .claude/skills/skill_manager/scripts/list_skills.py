#!/usr/bin/env python3
"""
List all available skills in .claude/skills and their descriptions.
"""
import os
import sys
from pathlib import Path

def parse_frontmatter(file_path):
    """Simple parser for YAML frontmatter."""
    metadata = {}
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        if not content.startswith('---'):
            return metadata
            
        parts = content.split('---', 2)
        if len(parts) < 3:
            return metadata
            
        frontmatter = parts[1]
        for line in frontmatter.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
                
        return metadata
    except Exception:
        return metadata

def main():
    skills_dir = Path(__file__).resolve().parent.parent.parent
    if not skills_dir.exists():
        print(f"Error: Skills directory not found at {skills_dir}")
        sys.exit(1)

    print(f"{ 'SKILL NAME':<25} | {'DESCRIPTION'}")
    print('-' * 80)

    for item in sorted(skills_dir.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            skill_md = item / 'SKILL.md'
            if skill_md.exists():
                metadata = parse_frontmatter(skill_md)
                name = metadata.get('name', item.name)
                description = metadata.get('description', 'No description provided.')
                
                # Truncate description if too long
                if len(description) > 50:
                    description = description[:47] + "..."
                    
                print(f"{name:<25} | {description}")
            else:
                 print(f"{item.name:<25} | (No SKILL.md found)")

if __name__ == '__main__':
    main()
