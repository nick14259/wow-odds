// src/components/PlayerMetricsDisplay.tsx
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

interface OddsDisplay {
  over: number;
  under: number;
}

interface MetricsProps {
  data: {
    character: {
      name: string;
      server: string;
      region: string;
      class: string;
      spec: string;
      version: string;
    };
    metrics: {
      death_analysis: any;
      avoidable_damage: any;
      performance: any;
    };
  };
}

const PlayerMetricsDisplay: React.FC<MetricsProps> = ({ data }) => {
  const formatOdds = (odds: [number, number]) => {
    const [over, under] = odds;
    return {
      over: over > 0 ? `+${over}` : over,
      under: under > 0 ? `+${under}` : under
    };
  };

  const renderOddsSection = (title: string, odds: [number, number], description: string) => (
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
      {/* Character Info */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white mb-2">
          {data.character.name} - {data.character.server}
        </h2>
        <p className="text-sm text-gray-400">
          {data.character.class} - {data.character.spec}
        </p>
      </div>

      {/* Death Metrics */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Death Analysis</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.metrics.death_analysis.overall_deaths && renderOddsSection(
            "Total Deaths",
            data.metrics.death_analysis.overall_deaths.odds,
            "Total number of deaths across all attempts"
          )}
          {data.metrics.death_analysis.death_timing && renderOddsSection(
            "Early Deaths",
            data.metrics.death_analysis.death_timing.early_death_rate.odds,
            "Deaths occurring in the first 30 seconds"
          )}
        </CardContent>
      </Card>

      {/* Avoidable Damage */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Avoidable Damage</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.metrics.avoidable_damage.mechanic_execution && renderOddsSection(
            "Mechanic Failures",
            data.metrics.avoidable_damage.mechanic_execution.mechanic_failure_rate.odds,
            "Rate of failing avoidable mechanics"
          )}
          {data.metrics.avoidable_damage.overall_avoidance && renderOddsSection(
            "Damage Avoidance",
            data.metrics.avoidable_damage.overall_avoidance.avoidance_rate.odds,
            "Success rate at avoiding damage"
          )}
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Performance Metrics</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.metrics.performance.fight_execution && renderOddsSection(
            "Mechanic Success",
            data.metrics.performance.fight_execution.mechanic_success.odds,
            "Success rate at handling fight mechanics"
          )}
          {data.metrics.performance.cooldown_usage && renderOddsSection(
            "Cooldown Efficiency",
            data.metrics.performance.fight_execution.cooldown_usage.odds,
            "Efficiency of major cooldown usage"
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PlayerMetricsDisplay;
