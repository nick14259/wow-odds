// src/components/metrics/PerformanceDisplay.tsx
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

interface PerformanceMetrics {
  fight_execution: {
    mechanic_success: {
      success_rate: number;
      total_mechanics: number;
      successful: number;
      odds: [number, number];
    };
    cooldown_usage: {
      efficiency: number;
      total_possible: number;
      total_used: number;
      odds: [number, number];
    };
  };
  role_performance: {
    dps_uptime?: {
      value: number;
      odds: [number, number];
    };
    healing_efficiency?: {
      value: number;
      odds: [number, number];
    };
    tank_survival?: {
      value: number;
      odds: [number, number];
    };
  };
}

interface PerformanceDisplayProps {
  metrics: PerformanceMetrics;
  playerClass: string;
  playerSpec: string;
}

const PerformanceDisplay: React.FC<PerformanceDisplayProps> = ({ metrics, playerClass, playerSpec }) => {
  const formatOdds = (odds: [number, number]) => {
    const [over, under] = odds;
    return {
      over: over > 0 ? `+${over}` : over,
      under: under > 0 ? `+${under}` : under
    };
  };

  const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`;

  const renderMetricCard = (
    title: string,
    value: number,
    odds: [number, number],
    description: string,
    additionalInfo?: string
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
        <span className="text-xl font-mono text-blue-400">{formatPercentage(value)}</span>
        {additionalInfo && (
          <span className="text-sm text-gray-400 ml-2">({additionalInfo})</span>
        )}
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
      {/* Fight Execution */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Fight Execution</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {renderMetricCard(
            "Mechanic Success Rate",
            metrics.fight_execution.mechanic_success.success_rate,
            metrics.fight_execution.mechanic_success.odds,
            "Success rate at handling fight mechanics",
            `${metrics.fight_execution.mechanic_success.successful}/${metrics.fight_execution.mechanic_success.total_mechanics}`
          )}
          {renderMetricCard(
            "Cooldown Usage",
            metrics.fight_execution.cooldown_usage.efficiency,
            metrics.fight_execution.cooldown_usage.odds,
            "Efficiency of major cooldown usage",
            `${metrics.fight_execution.cooldown_usage.total_used}/${metrics.fight_execution.cooldown_usage.total_possible}`
          )}
        </CardContent>
      </Card>

      {/* Role Performance */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Role Performance</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {metrics.role_performance.dps_uptime && (
            renderMetricCard(
              "DPS Uptime",
              metrics.role_performance.dps_uptime.value,
              metrics.role_performance.dps_uptime.odds,
              "Percentage of time actively dealing damage"
            )
          )}
          {metrics.role_performance.healing_efficiency && (
            renderMetricCard(
              "Healing Efficiency",
              metrics.role_performance.healing_efficiency.value,
              metrics.role_performance.healing_efficiency.odds,
              "Effective healing vs overhealing ratio"
            )
          )}
          {metrics.role_performance.tank_survival && (
            renderMetricCard(
              "Tank Survival",
              metrics.role_performance.tank_survival.value,
              metrics.role_performance.tank_survival.odds,
              "Success rate at surviving tankable damage"
            )
          )}
        </CardContent>
      </Card>

      {/* Class/Spec Info */}
      <div className="text-sm text-gray-400">
        Showing metrics for {playerSpec} {playerClass}
      </div>
    </div>
  );
};

export default PerformanceDisplay;
