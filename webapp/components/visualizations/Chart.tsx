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
function ensureLightColor(color?: string | string[]): string {
  if (!color) return DEFAULT_COLORS[0];

  // If array, return first element or default
  if (Array.isArray(color)) {
    return ensureLightColor(color[0]);
  }

  // Check if color is black or very dark
  const darkColorPattern = /#000000|#0[0-9a-f]{5}|black/i;
  if (darkColorPattern.test(color)) {
    return DEFAULT_COLORS[0];
  }

  return color;
}

export default function Chart({ command }: ChartProps) {
  const { data, options, chartType = 'line' } = command;

  // Validate data structure
  if (!data || !data.datasets || !Array.isArray(data.datasets)) {
    return (
      <div className="text-[#F48771] text-sm font-['Fira_Code',monospace]">
        Invalid chart data: missing or malformed datasets
      </div>
    );
  }

  // Build chart options with forced light colors
  const userPlugins = (options?.plugins as any) || {};
  const userScales = (options?.scales as any) || {};

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
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
        padding: 10,
        displayColors: true,
        ...userPlugins.tooltip,
      },
      // Ensure legend color is never overridden
      legend: {
        display: true,
        position: 'top' as const,
        align: 'start' as const,
        ...userPlugins.legend,
        labels: {
          color: '#E0E0E0',
          font: {
            family: "'Fira Code', monospace",
            size: 11,
          },
          boxWidth: 12,
          padding: 8,
          ...userPlugins.legend?.labels,
        },
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: '#333333',
          drawBorder: false,
          ...userScales.x?.grid,
        },
        ticks: {
          color: '#E0E0E0',
          font: {
            family: "'Fira Code', monospace",
            size: 11,
          },
          ...userScales.x?.ticks,
        },
      },
      y: {
        display: true,
        beginAtZero: true,
        grid: {
          color: '#333333',
          drawBorder: false,
          ...userScales.y?.grid,
        },
        ticks: {
          color: '#E0E0E0',
          font: {
            family: "'Fira Code', monospace",
            size: 11,
          },
          ...userScales.y?.ticks,
        },
      },
    },
  };

  const chartData = {
    ...data,
    datasets: data.datasets.map((ds, index) => ({
      ...ds,
      borderColor: ensureLightColor(ds.borderColor) || DEFAULT_COLORS[index % DEFAULT_COLORS.length],
      backgroundColor: Array.isArray(ds.backgroundColor)
        ? ds.backgroundColor.map(c => ensureLightColor(c) || DEFAULT_COLORS[index % DEFAULT_COLORS.length])
        : ensureLightColor(ds.backgroundColor) || DEFAULT_COLORS[index % DEFAULT_COLORS.length] + '20',
      borderWidth: 2,
      tension: 0.4,
      pointRadius: 3,
      pointBackgroundColor: ensureLightColor(ds.borderColor) || DEFAULT_COLORS[index % DEFAULT_COLORS.length],
      pointHoverRadius: 5,
    })),
  };

  const ChartComponent = chartType === 'bar' ? Bar : chartType === 'scatter' ? Scatter : Line;

  return (
    <div className="h-64 md:h-72 w-full">
      <ChartComponent data={chartData} options={chartOptions} />
    </div>
  );
}
