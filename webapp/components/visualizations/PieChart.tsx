'use client';

import { PieVizCommand } from '@/types/visualizations';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';
import { useEffect, useRef } from 'react';

ChartJS.register(ArcElement, Tooltip, Legend, Title);

interface PieChartProps {
  command: PieVizCommand;
}

export default function PieChart({ command }: PieChartProps) {
  const { data, options } = command;

  const defaultColors = [
    '#00ff00',
    '#00cc00',
    '#009900',
    '#006600',
    '#00ff99',
    '#00ffcc',
    '#00ccff',
    '#0099ff',
  ];

  const chartData = {
    labels: data.map((d) => d.label),
    datasets: [
      {
        data: data.map((d) => d.value),
        backgroundColor: data.map((d, i) => d.color || defaultColors[i % defaultColors.length]),
        borderColor: '#0a0a0a',
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: options?.showLegend !== false,
        position: 'right' as const,
        labels: {
          color: '#00ff00',
        },
      },
      title: {
        display: !!options?.title,
        text: options?.title,
        color: '#00ff00',
      },
    },
  };

  return (
    <div className="w-full h-64 my-4 p-2 border border-terminal-green">
      <Pie data={chartData} options={chartOptions} />
    </div>
  );
}
