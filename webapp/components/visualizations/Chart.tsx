'use client';

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

// One Dark theme colors for charts
const DEFAULT_COLORS = [
  '#5C6AC4', // Blue
  '#BB86FC', // Purple
  '#4FC1FF', // Cyan
  '#89D185', // Green
  '#DCDCAA', // Yellow
  '#F48771', // Red
];

// Filter out black or very dark colors
function ensureLightColor(color?: string): string {
  if (!color) return DEFAULT_COLORS[0];

  // Check if color is black or very dark
  const darkColorPattern = /#000000|#0[0-9a-f]{5}|black/i;
  if (darkColorPattern.test(color)) {
    return DEFAULT_COLORS[0];
  }

  return color;
}

export default function Chart({ command }: ChartProps) {
  const { data, options, chartType = 'line' } = command;

  // Build chart options with forced light colors
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
        bodyColor: '#E0E0E0',
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
      },
      // Merge user plugins options
      ...options?.plugins,
      // Ensure legend color is never overridden
      legend: {
        ...options?.plugins?.legend,
        labels: {
          ...options?.plugins?.legend?.labels,
          color: '#E0E0E0',
        },
      },
    },
    scales: {
      x: {
        display: true,
        ticks: {
          color: '#E0E0E0',
          font: {
            family: "'Fira Code', monospace",
            size: 11,
          },
        },
        grid: {
          color: '#333333',
          drawBorder: false,
        },
        // Merge user x-axis options
        ...options?.scales?.x,
        ticks: {
          ...options?.scales?.x?.ticks,
          color: '#E0E0E0',
        },
      },
      y: {
        display: true,
        ticks: {
          color: '#E0E0E0',
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
        // Merge user y-axis options
        ...options?.scales?.y,
        ticks: {
          ...options?.scales?.y?.ticks,
          color: '#E0E0E0',
        },
      },
    },
    // Merge any remaining user options
    ...options,
  };

  const chartData = {
    ...data,
    datasets: data.datasets.map((ds, index) => ({
      ...ds,
      borderColor: ensureLightColor(ds.borderColor) || DEFAULT_COLORS[index % DEFAULT_COLORS.length],
      backgroundColor: ensureLightColor(ds.backgroundColor) || DEFAULT_COLORS[index % DEFAULT_COLORS.length] + '20',
      borderWidth: 2,
      tension: 0.4,
      pointRadius: 3,
      pointBackgroundColor: ensureLightColor(ds.borderColor) || DEFAULT_COLORS[index % DEFAULT_COLORS.length],
      pointHoverRadius: 5,
    })),
  };

  const ChartComponent = chartType === 'bar' ? Bar : chartType === 'scatter' ? Scatter : Line;

  return (
    <div className="h-72">
      <ChartComponent data={chartData} options={chartOptions} />
    </div>
  );
}
