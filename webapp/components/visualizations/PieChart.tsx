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

  // Detect if values are percentages (sum close to 100) or actual values (dollar amounts)
  const totalValue = data.reduce((sum, d) => sum + d.value, 0);
  const isPercentage = totalValue > 90 && totalValue < 110;

  // Convert to percentages if values are actual dollar amounts
  const normalizedData = isPercentage
    ? data
    : data.map((d) => ({
        ...d,
        value: totalValue > 0 ? (d.value / totalValue) * 100 : 0,
      }));

  const chartData = {
    labels: normalizedData.map((d) => d.label),
    datasets: [
      {
        data: normalizedData.map((d) => d.value),
        backgroundColor: normalizedData.map((d, i) => d.color || DEFAULT_COLORS[i % DEFAULT_COLORS.length]),
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
          color: '#1a1a1a',
          font: {
            family: 'monospace',
            size: 12,
          },
          padding: 16,
          generateLabels: function(chart: any) {
            const chartData = chart.data;
            return chartData.labels.map((label: string, i: number) => {
              const percentage = chartData.datasets[0].data[i];
              const labelText = `${label} (${percentage.toFixed(1)}%)`;

              return {
                text: labelText,
                fillStyle: chartData.datasets[0].backgroundColor[i],
                color: '#1a1a1a',
                hidden: false,
                index: i,
              };
            });
          },
        },
      },
      title: {
        display: !!options?.title,
        text: options?.title,
        color: '#1a1a1a',
        font: {
          family: 'monospace',
          size: 14,
        },
      },
      tooltip: {
        backgroundColor: '#ffffff',
        titleColor: '#1a1a1a',
        bodyColor: '#4a4a4a',
        borderColor: '#e0e0e0',
        borderWidth: 1,
        titleFont: {
          family: 'monospace',
          size: 12,
        },
        bodyFont: {
          family: 'monospace',
          size: 11,
        },
        callbacks: {
          label: function(context: any) {
            const percentage = context.parsed;
            const originalValue = data[context.dataIndex].value;

            if (isPercentage) {
              return ` ${context.label}: ${percentage.toFixed(1)}%`;
            } else {
              const formattedValue = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0,
              }).format(originalValue);

              return ` ${context.label}: ${percentage.toFixed(1)}% (${formattedValue})`;
            }
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
