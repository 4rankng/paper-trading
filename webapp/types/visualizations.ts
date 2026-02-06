export type VizType = 'chart' | 'table' | 'pie';

export interface BaseVizCommand {
  type: VizType;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string | string[];
    borderWidth?: number;
  }[];
}

export interface ChartOptions {
  responsive?: boolean;
  maintainAspectRatio?: boolean;
  plugins?: {
    title?: {
      display: boolean;
      text: string;
    };
    legend?: {
      display: boolean;
    };
  };
  scales?: {
    x?: {
      display: boolean;
    };
    y?: {
      display: boolean;
      beginAtZero?: boolean;
    };
  };
}

export interface ChartVizCommand extends BaseVizCommand {
  type: 'chart';
  data: ChartData;
  options?: ChartOptions;
  chartType?: 'line' | 'bar' | 'scatter';
}

export interface TableRow {
  [key: string]: string | number | boolean;
}

export interface TableVizCommand extends BaseVizCommand {
  type: 'table';
  headers: string[];
  rows: TableRow[] | string[][];
  options?: {
    sortable?: boolean;
    caption?: string;
  };
}

export interface PieData {
  label: string;
  value: number;
  color?: string;
}

export interface PieVizCommand extends BaseVizCommand {
  type: 'pie';
  data: PieData[];
  options?: {
    title?: string;
    showLegend?: boolean;
  };
}

export type VizCommand = ChartVizCommand | TableVizCommand | PieVizCommand;

export interface ParsedViz {
  command: VizCommand;
  startIndex: number;
  endIndex: number;
  /** True if the visualization was auto-fixed from malformed syntax */
  autoFixed?: boolean;
  /** Description of what was fixed (for debugging/logging) */
  fixDescription?: string;
}
