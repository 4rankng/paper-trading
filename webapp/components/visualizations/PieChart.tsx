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

// Modern color palette for pie charts
const DEFAULT_COLORS = [
  '#5C6AC4', // Blue
  '#BB86FC', // Purple
  '#4FC1FF', // Cyan
  '#89D185', // Green
  '#DCDCAA', // Yellow
  '#F48771', // Red
  '#75BEFF', // Light Blue
  '#FF6B9D', // Pink
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
          padding: 16,
        },
      },
      title: {
        display: !!options?.title,
        text: options?.title,
        color: '#E0E0E0',
      },
      tooltip: {
        backgroundColor: '#252526',
        titleColor: '#E0E0E0',
        bodyColor: '#B3B3B3',
        borderColor: '#333333',
        borderWidth: 1,
      },
    },
  };

  return (
    <div className="w-full h-72 my-4 p-4 bg-[#1E1E1E] border border-[#333333] rounded-lg">
      <Pie data={chartData} options={chartOptions} />
    </div>
  );
}
