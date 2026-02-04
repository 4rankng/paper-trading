'use client';

import { useState, useEffect, useRef } from 'react';

interface TerminalInputProps {
  onSubmit: (command: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export default function TerminalInput({ onSubmit, isLoading, disabled }: TerminalInputProps) {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading && !disabled) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, [isLoading, disabled]);

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <span className="text-terminal-green">$</span>
      <input
        ref={inputRef}
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={isLoading || disabled}
        className="flex-1 bg-transparent text-terminal-green outline-none font-mono"
        autoComplete="off"
        autoFocus
      />
    </form>
  );
}
