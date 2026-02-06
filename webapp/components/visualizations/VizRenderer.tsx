'use client';

import { VizCommand } from '@/types/visualizations';
import Chart from './Chart';
import Table from './Table';
import PieChart from './PieChart';

interface VizRendererProps {
  command: VizCommand;
}

const VIZ_ICONS: Record<string, string> = {
  chart: '📊',
  table: '📋',
  pie: '📊',
};

function getVizTitle(command: VizCommand): string {
  if (command.type === 'pie' && command.options?.title) {
    return command.options.title;
  }
  if (command.type === 'table' && command.options?.caption) {
    return command.options.caption;
  }
  return `${command.type.charAt(0).toUpperCase() + command.type.slice(1)} Visualization`;
}

export default function VizRenderer({ command }: VizRendererProps) {
  const icon = VIZ_ICONS[command.type] || '📊';
  const title = getVizTitle(command);

  // Use light background for pie charts
  const isPieChart = command.type === 'pie';
  const cardBg = isPieChart ? 'bg-gray-100' : 'bg-[#2D2D2D]';
  const contentBg = isPieChart ? 'bg-white' : 'bg-[#252526]';
  const borderColor = isPieChart ? 'border-gray-300' : 'border-[#3E3E42]';
  const titleColor = isPieChart ? 'text-gray-800' : 'text-[#4FC1FF]';

  return (
    <div className={`${cardBg} border ${borderColor} rounded-lg p-3 md:p-4 my-4`}>
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base md:text-lg">{icon}</span>
        <span className={`${titleColor} text-xs md:text-sm font-semibold font-['Fira_Code',monospace]`}>
          {title}
        </span>
      </div>

      {/* Content */}
      <div className={`${contentBg} rounded p-2 md:p-3`}>
        <VizContent command={command} />
      </div>
    </div>
  );
}

function VizContent({ command }: { command: VizCommand }) {
  switch (command.type) {
    case 'chart':
      return <Chart command={command} />;
    case 'table':
      return <Table command={command} />;
    case 'pie':
      return <PieChart command={command} />;
    default:
      return (
        <div className="text-[#F48771] text-sm font-['Fira_Code',monospace]">
          Unknown visualization type: {(command as VizCommand).type}
        </div>
      );
  }
}
