// src/components/metrics/DeathMetricsDisplay.tsx
'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Info } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface DeathMetrics {
  overall_deaths: {
    total_deaths: {
      value: number;
      description: string;
      odds: [number, number];
    };
    deaths_per_hour: {
      value: number;
      description: string;
      odds: [number, number];
    };
    deaths_per_pull: {
      value: number;
      description: string;
      odds: [number, number];
    };
  };
  death_timing: {
    time_to_death_avg: {
      value: number;
      description: string;
      odds: [number, number];
    };
    early_death_rate: {
      value: number;
      description: string;
      odds: [number, number];
    };
    critical_phase_deaths: {
      value: number;
      description: string;
      odds: [number, number];
    };
  };
  death_causes: {
    mechanic_deaths: {
      value: number;
      description: string;
      odds: [number, number];
    };
    environment_deaths: {
      value: number;
      description: string;
      odds: [number, number];
    };
    chain_deaths: {
      value: number;
      description: string;
      odds: [number, number];
    };
  };
}

interface DeathMetricsDisplayProps {
  metrics: DeathMetrics;
}

const DeathMetricsDisplay: React.FC<DeathMetricsDisplayProps> = ({ metrics }) => {
  const formatOdds = (odds: [number, number]) => {
    const [over, under] = odds;
    return {
      over: over > 0 ? `+${over}` : over,
      under: under > 0 ? `+${under}` : under
    };
  };

  const formatValue = (value: number) => {
    if (value < 1) {
      return `${(value * 100).toFixed(1)}%`;
    }
    return value.toFixed(2);
  };

  const renderMetricCard = (
    title: string,
    value: number,
    odds: [number, number],
    description: string
  ) => (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex justify-between items-start mb-2">
        <span className="text-sm font-medium text-gray-300">{title}</span>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <Info size={16} className="text-gray-400 hover:text-gray-300" />
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-sm">{description}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
      <div className="mb-2">
        <span className="text-xl font-mono text-blue-400">{formatValue(value)}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="text-gray-400">
          Over: <span className={`font-mono ${odds[0] > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatOdds(odds).over}
          </span>
        </div>
        <div className="text-gray-400">
          Under: <span className={`font-mono ${odds[1] > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatOdds(odds).under}
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Overall Deaths */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Death Statistics</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {renderMetricCard(
            "Total Deaths",
            metrics.overall_deaths.total_deaths.value,
            metrics.overall_deaths.total_deaths.odds,
            metrics.overall_deaths.total_deaths.description
          )}
          {renderMetricCard(
            "Deaths per Hour",
            metrics.overall_deaths.deaths_per_hour.value,
            metrics.overall_deaths.deaths_per_hour.odds,
            metrics.overall_deaths.deaths_per_hour.description
          )}
          {renderMetricCard(
            "Deaths per Pull",
            metrics.overall_deaths.deaths_per_pull.value,
            metrics.overall_deaths.deaths_per_pull.odds,
            metrics.overall_deaths.deaths_per_pull.description
          )}
        </CardContent>
      </Card>

      {/* Death Timing */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Death Timing</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {renderMetricCard(
            "Average Survival Time",
            metrics.death_timing.time_to_death_avg.value,
            metrics.death_timing.time_to_death_avg.odds,
            metrics.death_timing.time_to_death_avg.description
          )}
          {renderMetricCard(
            "Early Death Rate",
            metrics.death_timing.early_death_rate.value,
            metrics.death_timing.early_death_rate.odds,
            metrics.death_timing.early_death_rate.description
          )}
          {renderMetricCard(
            "Critical Phase Deaths",
            metrics.death_timing.critical_phase_deaths.value,
            metrics.death_timing.critical_phase_deaths.odds,
            metrics.death_timing.critical_phase_deaths.description
          )}
        </CardContent>
      </Card>

      {/* Death Causes */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Death Causes</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {renderMetricCard(
            "Mechanic Deaths",
            metrics.death_causes.mechanic_deaths.value,
            metrics.death_causes.mechanic_deaths.odds,
            metrics.death_causes.mechanic_deaths.description
          )}
          {renderMetricCard(
            "Environmental Deaths",
            metrics.death_causes.environment_deaths.value,
            metrics.death_causes.environment_deaths.odds,
            metrics.death_causes.environment_deaths.description
          )}
          {renderMetricCard(
            "Chain Deaths",
            metrics.death_causes.chain_deaths.value,
            metrics.death_causes.chain_deaths.odds,
            metrics.death_causes.chain_deaths.description
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DeathMetricsDisplay;
