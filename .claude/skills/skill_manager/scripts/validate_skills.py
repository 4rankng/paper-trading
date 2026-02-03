#!/usr/bin/env python3
"""
Validate the structure of skills in .claude/skills.
"""
import sys
from pathlib import Path

def parse_frontmatter(file_path):
    """Simple parser for YAML frontmatter."""
    metadata = {}
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        if not content.startswith('---'):
            return None
            
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
            
        frontmatter = parts[1]
        for line in frontmatter.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
                
        return metadata
    except Exception:
        return None

def main():
    skills_dir = Path(__file__).resolve().parent.parent.parent
    if not skills_dir.exists():
        print(f"Error: Skills directory not found at {skills_dir}")
        sys.exit(1)

    print(f"Validating skills in {skills_dir}...\n")
    
    errors = 0
    warnings = 0

    for item in sorted(skills_dir.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            print(f"Checking {item.name}...")
            
            # Check SKILL.md
            skill_md = item / 'SKILL.md'
            if not skill_md.exists():
                print(f"  [ERROR] Missing SKILL.md")
                errors += 1
            else:
                metadata = parse_frontmatter(skill_md)
                if metadata is None:
                    print(f"  [ERROR] SKILL.md has invalid frontmatter")
                    errors += 1
                else:
                    if 'name' not in metadata:
                        print(f"  [ERROR] SKILL.md missing 'name' in frontmatter")
                        errors += 1
                    if 'description' not in metadata:
                        print(f"  [WARNING] SKILL.md missing 'description'")
                        warnings += 1

            # Check scripts directory
            scripts_dir = item / 'scripts'
            if not scripts_dir.exists():
                print(f"  [INFO] No scripts directory (might be intentonal)")
            
            print("")

    print("-" * 40)
    print(f"Validation complete: {errors} errors, {warnings} warnings.")
    
    if errors > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
