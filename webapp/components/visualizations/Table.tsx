'use client';

import { useState } from 'react';
import { TableVizCommand } from '@/types/visualizations';

interface TableProps {
  command: TableVizCommand;
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

  return (
    <div className="my-4 border border-terminal-green overflow-x-auto">
      {options?.caption && (
        <caption className="block text-terminal-green mb-2 text-sm">
          {options.caption}
        </caption>
      )}
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-terminal-green">
            {headers.map((header, i) => (
              <th
                key={i}
                onClick={() => handleSort(i)}
                className={`p-2 text-terminal-green ${
                  options?.sortable ? 'cursor-pointer hover:bg-terminal-dim' : ''
                }`}
              >
                {header}
                {sortColumn === i && (sortDirection === 'asc' ? ' ↑' : ' ↓')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row, i) => (
            <tr key={i} className="border-b border-terminal-dim">
              {row.map((cell, j) => (
                <td key={j} className="p-2 text-terminal-green">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
