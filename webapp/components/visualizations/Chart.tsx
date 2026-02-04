'use client';

import { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Scatter } from 'react-chartjs-2';
import { ChartVizCommand } from '@/types/visualizations';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ChartProps {
  command: ChartVizCommand;
}

// Modern color palette for charts
const DEFAULT_COLORS = [
  '#5C6AC4', // Blue
  '#BB86FC', // Purple
  '#4FC1FF', // Cyan
  '#89D185', // Green
  '#DCDCAA', // Yellow
  '#F48771', // Red
];

export default function Chart({ command }: ChartProps) {
  const { data, options, chartType = 'line' } = command;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        labels: {
          color: '#E0E0E0',
          font: {
            family: "'Fira Code', monospace",
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: '#252526',
        titleColor: '#E0E0E0',
        bodyColor: '#B3B3B3',
        borderColor: '#333333',
        borderWidth: 1,
      },
      ...options?.plugins,
    },
    scales: {
      x: {
        display: true,
        ticks: {
          color: '#858585',
          font: {
            family: "'Fira Code', monospace",
            size: 11,
          },
        },
        grid: {
          color: '#333333',
          drawBorder: false,
        },
        ...options?.scales?.x,
      },
      y: {
        display: true,
        ticks: {
          color: '#858585',
          font: {
            family: "'Fira Code', monospace",
            size: 11,
          },
        },
        grid: {
          color: '#333333',
          drawBorder: false,
        },
        beginAtZero: true,
        ...options?.scales?.y,
      },
    },
    ...options,
  };

  const chartData = {
    ...data,
    datasets: data.datasets.map((ds, index) => ({
      ...ds,
      borderColor: ds.borderColor || DEFAULT_COLORS[index % DEFAULT_COLORS.length],
      backgroundColor: ds.backgroundColor || DEFAULT_COLORS[index % DEFAULT_COLORS.length] + '40',
      borderWidth: 2,
      tension: 0.3,
      pointRadius: 3,
      pointHoverRadius: 5,
    })),
  };

  const ChartComponent = chartType === 'bar' ? Bar : chartType === 'scatter' ? Scatter : Line;

  return (
    <div className="w-full h-64 my-4">
      <ChartComponent data={chartData} options={chartOptions} />
    </div>
  );
}
