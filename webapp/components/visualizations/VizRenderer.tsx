'use client';

import { VizCommand } from '@/types/visualizations';
import Chart from './Chart';
import Table from './Table';
import PieChart from './PieChart';

interface VizRendererProps {
  command: VizCommand;
}

export default function VizRenderer({ command }: VizRendererProps) {
  switch (command.type) {
    case 'chart':
      return <Chart command={command} />;
    case 'table':
      return <Table command={command} />;
    case 'pie':
      return <PieChart command={command} />;
    default:
      return (
        <div className="text-terminal-green p-2 border border-terminal-green my-4">
          Unknown visualization type: {(command as VizCommand).type}
        </div>
      );
  }
}
