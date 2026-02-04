import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { join } from 'path';

export const runtime = 'nodejs';

// Map skill names to their Python entry points
// Each skill maps to its scripts directory for flexible invocation
const SKILL_SCRIPTS: Record<string, string> = {
  // Portfolio & Trading
  'portfolio_manager': '.claude/skills/portfolio_manager/scripts',
  'watchlist_manager': '.claude/skills/watchlist_manager/scripts',
  'trading_plan': '.claude/skills/trading-plan/scripts',

  // Data & Analytics
  'news_fetcher': '.claude/skills/news_fetcher/scripts',
  'analytics_generator': '.claude/skills/analytics_generator/scripts',
  'macro_fetcher': '.claude/skills/macro_fetcher/scripts',

  // Analysis Tools
  'trading_debate': '.claude/skills/trading-debate/scripts',
  'signal_formatter': '.claude/skills/signal-formatter/scripts',

  // Utilities
  'read_csv': '.claude/skills/read-csv/scripts',
  'read_pdf': '.claude/skills/read-pdf/scripts',
  'skill_manager': '.claude/skills/skill_manager/scripts',

  // Messaging (optional)
  'zalo_messenger': '.claude/skills/zalo_messenger/scripts',

  // Documentation
  'documentation_templates': '.claude/skills/documentation-templates/scripts',
};

// Skill description for LLM
const SKILL_DESCRIPTIONS: Record<string, string> = {
  portfolio_manager: 'Manage portfolio holdings, execute trades, track history. Scripts: get_portfolio.py, update_portfolio_and_log.py, get_trade_log.py, thesis_monitor.py, visualize.py',
  watchlist_manager: 'Manage watchlist.json. Scripts: add.py, list.py, remove.py, search.py, update.py',
  trading_plan: 'Generate trading plans with entry/exit/stop levels. Script: trading_plan.py',
  news_fetcher: 'Fetch news from yfinance, manage articles. Scripts: fetch_news.py, list_news.py, add_news.py, search_news.py, update_article.py, delete_article.py',
  analytics_generator: 'Generate price data, technical/fundamental/thesis files. Scripts: fetch_prices.py, update_technical.py, update_fundamental.py, update_thesis.py, visualize.py',
  macro_fetcher: 'Macro economic analysis. Scripts: create_macro_thesis.py, add_central_bank_update.py, add_geopolitical_event.py, add_commodity_update.py, list_macro.py',
  trading_debate: 'Multi-agent adversarial analysis. Scripts: start_debate.py, debate_orchestrator.py, persona_tracker.py, challenge_scorer.py',
  signal_formatter: 'Format trading signals. Script: format_signal.py',
  read_csv: 'Read CSV files. Script: read_csv.py',
  read_pdf: 'Read PDF files. Script: read_pdf.py',
  skill_manager: 'Manage skills. Scripts: list_skills.py, validate_skill.py',
  zalo_messenger: 'Zalo messaging. Scripts: send_message.py, list_friends.py, status.py, listen.py',
  documentation_templates: 'Generate docs. Script: generate_docs.py',
};

async function invokePythonSkill(
  skillName: string,
  scriptName: string,
  args: string[]
): Promise<{ success: boolean; output?: string; error?: string }> {
  return new Promise((resolve) => {
    const projectRoot = join(process.cwd(), '..');
    const skillDir = SKILL_SCRIPTS[skillName];

    if (!skillDir) {
      return resolve({
        success: false,
        error: `Unknown skill: ${skillName}. Available: ${Object.keys(SKILL_SCRIPTS).join(', ')}`,
      });
    }

    const scriptPath = join(projectRoot, skillDir, scriptName);

    // Build command arguments
    const commandArgs = [...args];

    console.log(`[Skill API] Invoking: python3 ${scriptPath}`, commandArgs);

    const python = spawn('python3', [scriptPath, ...commandArgs], {
      cwd: projectRoot,
      env: {
        ...process.env,
        PYTHONPATH: join(projectRoot, '.claude', 'shared'),
      },
    });

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, output: stdout.trim() });
      } else {
        resolve({
          success: false,
          error: stderr || `Script exited with code ${code}`,
        });
      }
    });

    python.on('error', (error) => {
      resolve({
        success: false,
        error: `Failed to spawn Python: ${error.message}`,
      });
    });

    // Timeout after 60 seconds for long-running tasks
    setTimeout(() => {
      python.kill();
      resolve({
        success: false,
        error: 'Skill execution timed out (60s)',
      });
    }, 60000);
  });
}

export async function POST(request: NextRequest) {
  try {
    const { skill, script, args = [], session_id } = await request.json();

    if (!skill) {
      return NextResponse.json(
        { error: 'Skill name is required' },
        { status: 400 }
      );
    }

    if (!script) {
      return NextResponse.json(
        { error: 'Script name is required. Use GET /api/skill?name=portfolio_manager to see available scripts.' },
        { status: 400 }
      );
    }

    if (!Array.isArray(args)) {
      return NextResponse.json(
        { error: 'Args must be an array' },
        { status: 400 }
      );
    }

    // Convert args to strings for Python
    const stringArgs = args.map(String);

    const result = await invokePythonSkill(skill, script, stringArgs);

    if (!result.success) {
      return NextResponse.json(
        { error: result.error },
        { status: 500 }
      );
    }

    return NextResponse.json({
      skill,
      script,
      args: stringArgs,
      session_id,
      output: result.output,
    });
  } catch (error: any) {
    console.error('[Skill API] Error:', error);
    return NextResponse.json(
      {
        error: 'Skill execution failed',
        message: error?.message || 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// GET endpoint to list available skills or scripts for a specific skill
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const skillName = searchParams.get('name');

  // List all skills
  if (!skillName) {
    return NextResponse.json({
      skills: Object.keys(SKILL_SCRIPTS).map(name => ({
        name,
        description: SKILL_DESCRIPTIONS[name] || '',
      })),
    });
  }

  // List scripts for a specific skill
  const skillDir = SKILL_SCRIPTS[skillName];
  if (!skillDir) {
    return NextResponse.json(
      { error: `Unknown skill: ${skillName}` },
      { status: 404 }
    );
  }

  const projectRoot = join(process.cwd(), '..');
  const fullPath = join(projectRoot, skillDir);

  try {
    const fs = await import('fs/promises');
    const files = await fs.readdir(fullPath);
    const scripts = files.filter(f => f.endsWith('.py'));

    return NextResponse.json({
      skill: skillName,
      description: SKILL_DESCRIPTIONS[skillName] || '',
      scripts,
    });
  } catch (error) {
    return NextResponse.json(
      { error: `Failed to list scripts for ${skillName}` },
      { status: 500 }
    );
  }
}
