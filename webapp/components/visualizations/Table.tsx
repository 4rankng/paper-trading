'use client';

import { useState } from 'react';
import { TableVizCommand } from '@/types/visualizations';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface TableProps {
  command: TableVizCommand;
}

// Helper component to render markdown in table cells
function MarkdownCell({ content }: { content: string }) {
  return (
    <ReactMarkdown
      className="prose prose-invert prose-sm max-w-none"
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <span>{children}</span>,
        strong: ({ children }) => <span className="font-bold text-white">{children}</span>,
        em: ({ children }) => <span className="italic">{children}</span>,
        code: ({ children }) => (
          <code className="bg-[#2D2D2D] text-[#4FC1FF] px-1 py-0.5 rounded text-xs">{children}</code>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

export default function Table({ command }: TableProps) {
  const { headers, rows, options } = command;
  const [sortColumn, setSortColumn] = useState<number | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Normalize rows to array of arrays
  const normalizedRows = rows.map((row) => {
    if (Array.isArray(row)) return row;
    return headers.map((header) => row[header]?.toString() || '');
  });

  const handleSort = (columnIndex: number) => {
    if (!options?.sortable) return;

    if (sortColumn === columnIndex) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnIndex);
      setSortDirection('asc');
    }
  };

  let sortedRows = [...normalizedRows];
  if (sortColumn !== null && options?.sortable) {
    sortedRows.sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];

      const aNum = parseFloat(aVal);
      const bNum = parseFloat(bVal);

      if (!isNaN(aNum) && !isNaN(bNum)) {
        return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
      }

      return sortDirection === 'asc'
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal);
    });
  }

  const getCellClass = (value: string) => {
    // Check for positive/negative indicators
    if (value.startsWith('+') || value.toLowerCase().includes('positive') || value.toLowerCase() === 'strong' || value.toLowerCase() === 'growing') {
      return 'text-[#89D185]';
    }
    if (value.startsWith('-') || value.toLowerCase().includes('negative') || value.toLowerCase() === 'below' || value.toLowerCase() === 'weak') {
      return 'text-[#F48771]';
    }
    return 'text-[#E0E0E0]';
  };

  const getHeaderClass = () => {
    return 'text-[#4FC1FF]';
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left font-['Fira_Code',monospace]">
        <thead>
          <tr>
            {headers.map((header, i) => (
              <th
                key={i}
                onClick={() => handleSort(i)}
                className={`px-3 py-2.5 text-xs font-semibold uppercase tracking-wider border-b-2 border-[#3E3E42] ${
                  options?.sortable
                    ? 'cursor-pointer hover:text-[#75BEFF] transition-colors'
                    : ''
                } ${getHeaderClass()}`}
              >
                <MarkdownCell content={header} />
                {sortColumn === i && (
                  <span className="ml-2">
                    {sortDirection === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row, i) => (
            <tr
              key={i}
              className="border-b border-[#333333] hover:bg-[#2D2D2D] transition-colors"
            >
              {row.map((cell, j) => (
                <td
                  key={j}
                  className={`px-3 py-2.5 text-sm ${getCellClass(cell.toString())}`}
                >
                  <MarkdownCell content={cell.toString()} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
