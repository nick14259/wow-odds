// src/components/metrics/AvoidableDamageDisplay.tsx
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

interface DamageMetrics {
  standing_in_bad: {
    total_damage: {
      value: number;
      per_minute: number;
      description: string;
      odds: [number, number];
    };
    damage_breakdown: {
      [key: string]: {
        total: number;
        percentage: number;
        odds: [number, number];
      };
    };
  };
  mechanic_execution: {
    mechanic_failure_rate: {
      value: number;
      description: string;
      odds: [number, number];
    };
    repeated_failures: {
      [key: string]: {
        count: number;
        odds: [number, number];
      };
    };
  };
  overall_avoidance: {
    avoidance_rate: {
      value: number;
      description: string;
      odds: [number, number];
    };
    improvement_trend: {
      trend: 'improving' | 'declining' | 'stable';
      confidence: number;
      early_vs_late: string;
    };
  };
}

interface AvoidableDamageDisplayProps {
  metrics: DamageMetrics;
}

const AvoidableDamageDisplay: React.FC<AvoidableDamageDisplayProps> = ({ metrics }) => {
  const formatOdds = (odds: [number, number]) => {
    const [over, under] = odds;
    return {
      over: over > 0 ? `+${over}` : over,
      under: under > 0 ? `+${under}` : under
    };
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toFixed(0);
  };

  const renderDamageMetric = (
    title: string,
    value: number,
    odds: [number, number],
    description: string,
    suffix: string = ""
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
        <span className="text-xl font-mono text-blue-400">
          {formatNumber(value)}{suffix}
        </span>
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

  const renderTrendIndicator = (trend: DamageMetrics['overall_avoidance']['improvement_trend']) => {
    const colors = {
      improving: 'text-green-400',
      declining: 'text-red-400',
      stable: 'text-yellow-400'
    };

    return (
      <div className="flex items-center gap-2">
        <span className={`text-sm ${colors[trend.trend]}`}>
          {trend.trend.charAt(0).toUpperCase() + trend.trend.slice(1)}
        </span>
        <span className="text-gray-400 text-sm">
          ({trend.early_vs_late})
        </span>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Damage Overview */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Avoidable Damage Overview</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {renderDamageMetric(
            "Total Damage Taken",
            metrics.standing_in_bad.total_damage.value,
            metrics.standing_in_bad.total_damage.odds,
            metrics.standing_in_bad.total_damage.description
          )}
          {renderDamageMetric(
            "Damage per Minute",
            metrics.standing_in_bad.total_damage.per_minute,
            metrics.standing_in_bad.total_damage.odds,
            "Average avoidable damage taken per minute",
            "/min"
          )}
        </CardContent>
      </Card>

      {/* Damage Breakdown */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Damage Type Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(metrics.standing_in_bad.damage_breakdown).map(([type, data]) => (
            <div key={type} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm font-medium text-gray-300 mb-2">{type}</div>
              <div className="text-xl font-mono text-blue-400 mb-2">
                {formatNumber(data.total)}
                <span className="text-sm text-gray-400 ml-1">
                  ({data.percentage.toFixed(1)}%)
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="text-gray-400">
                  Over: <span className={`font-mono ${data.odds[0] > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatOdds(data.odds).over}
                  </span>
                </div>
                <div className="text-gray-400">
                  Under: <span className={`font-mono ${data.odds[1] > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatOdds(data.odds).under}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Mechanic Execution */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Mechanic Execution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {renderDamageMetric(
              "Overall Avoidance",
              metrics.overall_avoidance.avoidance_rate.value,
              metrics.overall_avoidance.avoidance_rate.odds,
              metrics.overall_avoidance.avoidance_rate.description,
              "%"
            )}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm font-medium text-gray-300 mb-2">Improvement Trend</div>
              {renderTrendIndicator(metrics.overall_avoidance.improvement_trend)}
            </div>
          </div>
          
          {/* Repeated Failures */}
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-300 mb-2">Repeated Mechanic Failures</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(metrics.mechanic_execution.repeated_failures).map(([mechanic, data]) => (
                <div key={mechanic} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <div className="text-sm font-medium text-gray-300 mb-2">{mechanic}</div>
                  <div className="text-xl font-mono text-blue-400 mb-2">
                    {data.count} times
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="text-gray-400">
                      Over: <span className={`font-mono ${data.odds[0] > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatOdds(data.odds).over}
                      </span>
                    </div>
                    <div className="text-gray-400">
                      Under: <span className={`font-mono ${data.odds[1] > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatOdds(data.odds).under}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AvoidableDamageDisplay;
