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

ChartJS.register(ArcElement, Tooltip, Legend, Title);

interface PieChartProps {
  command: PieVizCommand;
}

// One Dark theme colors for pie charts
const DEFAULT_COLORS = [
  '#5C6AC4', // Blue
  '#BB86FC', // Purple
  '#4FC1FF', // Cyan
  '#89D185', // Green
  '#DCDCAA', // Yellow
  '#F48771', // Red
  '#75BEFF', // Light Blue
];

export default function PieChart({ command }: PieChartProps) {
  const { data, options } = command;

  const chartData = {
    labels: data.map((d) => d.label),
    datasets: [
      {
        data: data.map((d) => d.value),
        backgroundColor: data.map((d, i) => d.color || DEFAULT_COLORS[i % DEFAULT_COLORS.length]),
        borderColor: '#1E1E1E',
        borderWidth: 2,
        hoverOffset: 4,
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
          color: '#E0E0E0',
          font: {
            family: "'Fira Code', monospace",
            size: 12,
          },
          padding: 16,
          generateLabels: function(chart: any) {
            const data = chart.data;
            return data.labels.map((label: string, i: number) => ({
              text: `${label} (${data.datasets[0].data[i]}%)`,
              fillStyle: data.datasets[0].backgroundColor[i],
              color: '#E0E0E0',
              hidden: false,
              index: i,
            }));
          },
        },
      },
      title: {
        display: !!options?.title,
        text: options?.title,
        color: '#E0E0E0',
        font: {
          family: "'Fira Code', monospace",
          size: 14,
        },
      },
      tooltip: {
        backgroundColor: '#252526',
        titleColor: '#E0E0E0',
        bodyColor: '#B3B3B3',
        borderColor: '#3E3E42',
        borderWidth: 1,
        titleFont: {
          family: "'Fira Code', monospace",
          size: 12,
        },
        bodyFont: {
          family: "'Fira Code', monospace",
          size: 11,
        },
        callbacks: {
          label: function(context: any) {
            return ` ${context.label}: ${context.parsed}%`;
          },
        },
      },
    },
  };

  return (
    <div className="h-72">
      <Pie data={chartData} options={chartOptions} />
    </div>
  );
}
