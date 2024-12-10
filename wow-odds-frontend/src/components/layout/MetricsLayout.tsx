// src/components/layout/MetricsLayout.tsx
'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { LoadingSpinner, ErrorDisplay } from '@/components/shared';

interface Metrics {
  overview: {
    total_reports: number;
    total_fights: number;
    total_kills: number;
    kill_rate: number;
  };
  reports: Array<{
    title: string;
    date: string;
    zone: string;
    total_fights: number;
    kills: number;
  }>;
}

interface MetricsLayoutProps {
  data: {
    character: {
      name: string;
      server: string;
      region: string;
      version: string;
      class: string;
    };
    timestamp: string;
    metrics: Metrics;
  };
  isLoading: boolean;
  error?: string;
}

const MetricsLayout: React.FC<MetricsLayoutProps> = ({ data, isLoading, error }) => {
  console.log('MetricsLayout: Received props:', { data, isLoading, error });

  if (isLoading) {
    console.log('MetricsLayout: Showing loading state');
    return <LoadingSpinner />;
  }

  if (error) {
    console.log('MetricsLayout: Showing error state:', error);
    return <ErrorDisplay message={error} />;
  }

  if (!data) {
    console.log('MetricsLayout: No data received');
    return null;
  }

  console.log('MetricsLayout: Rendering data:', data);
  const { character, metrics } = data;

  return (
    <div className="space-y-6">
      {/* Character Info */}
      <Card className="bg-gray-800 border-gray-700 p-6">
        <h2 className="text-2xl font-bold text-white">
          {character.name} - {character.server}
        </h2>
        <p className="text-gray-400 mt-2">
          {character.class} ({character.version}) - {metrics.overview.total_reports} reports found
        </p>
      </Card>

      {/* Performance Overview */}
      <Card className="bg-gray-800 border-gray-700">
        <div className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Performance Overview</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-400">Total Fights</p>
              <p className="text-2xl font-bold text-white">{metrics.overview.total_fights}</p>
            </div>
            <div className="text-center p-4 bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-400">Total Kills</p>
              <p className="text-2xl font-bold text-white">{metrics.overview.total_kills}</p>
            </div>
            <div className="text-center p-4 bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-400">Kill Rate</p>
              <p className="text-2xl font-bold text-white">
                {metrics.overview.kill_rate.toFixed(1)}%
              </p>
            </div>
            <div className="text-center p-4 bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-400">Total Reports</p>
              <p className="text-2xl font-bold text-white">{metrics.overview.total_reports}</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Recent Reports */}
      {metrics.reports && metrics.reports.length > 0 && (
        <Card className="bg-gray-800 border-gray-700">
          <div className="p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Recent Reports</h3>
            <div className="space-y-4">
              {metrics.reports.map((report, index) => (
                <div 
                  key={`${report.title}-${index}`} 
                  className="border-b border-gray-700 pb-4 last:border-0 hover:bg-gray-700/20 transition-colors rounded-lg p-4"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-white font-medium">{report.title}</p>
                      <p className="text-sm text-gray-400">
                        {new Date(report.date).toLocaleDateString(undefined, {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-300">{report.zone}</p>
                      <p className="text-sm text-gray-400">
                        Success Rate: {((report.kills / report.total_fights) * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-400">
                        Kills: {report.kills}/{report.total_fights}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default MetricsLayout;
