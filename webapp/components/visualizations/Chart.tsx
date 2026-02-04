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

export default function Chart({ command }: ChartProps) {
  const { data, options, chartType = 'line' } = command;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        labels: {
          color: '#00ff00',
        },
      },
      ...options?.plugins,
    },
    scales: {
      x: {
        display: true,
        ticks: { color: '#00ff00' },
        grid: { color: '#003300' },
        ...options?.scales?.x,
      },
      y: {
        display: true,
        ticks: { color: '#00ff00' },
        grid: { color: '#003300' },
        beginAtZero: true,
        ...options?.scales?.y,
      },
    },
    ...options,
  };

  const chartData = {
    ...data,
    datasets: data.datasets.map((ds) => ({
      ...ds,
      borderColor: ds.borderColor || '#00ff00',
      backgroundColor: ds.backgroundColor || 'rgba(0, 255, 0, 0.2)',
    })),
  };

  const ChartComponent = chartType === 'bar' ? Bar : chartType === 'scatter' ? Scatter : Line;

  return (
    <div className="w-full h-64 my-4 p-2 border border-terminal-green">
      <ChartComponent data={chartData} options={chartOptions} />
    </div>
  );
}
