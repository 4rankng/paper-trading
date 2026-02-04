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
    <div className="my-4 border border-[#333333] rounded-lg overflow-hidden bg-[#1E1E1E]">
      {options?.caption && (
        <div className="bg-[#252526] px-4 py-2 text-sm text-[#E0E0E0] font-medium border-b border-[#333333]">
          {options.caption}
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-[#252526] border-b border-[#333333]">
              {headers.map((header, i) => (
                <th
                  key={i}
                  onClick={() => handleSort(i)}
                  className={`p-3 text-xs font-semibold text-[#E0E0E0] uppercase tracking-wide font-mono ${
                    options?.sortable
                      ? 'cursor-pointer hover:bg-[#2D2D2D] transition-colors'
                      : ''
                  }`}
                >
                  {header}
                  {sortColumn === i && (
                    <span className="ml-2 text-[#5C6AC4]">
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
                className="border-b border-[#333333] hover:bg-[#252526] transition-colors"
              >
                {row.map((cell, j) => (
                  <td key={j} className="p-3 text-sm text-[#B3B3B3] font-mono">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
