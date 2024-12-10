// src/types/api.ts
export interface Character {
  name: string;
  server: string;
  region: string;
  version: string;
  class: string;
}

export interface Report {
  title: string;
  date: string;
  zone: string;
  total_fights: number;
  kills: number;
}

export interface Metrics {
  overview: {
    total_reports: number;
    total_fights: number;
    total_kills: number;
    kill_rate: number;
  };
  reports: Report[];
  status?: string;
}

export interface SearchData {
  character: Character;
  timestamp: string;
  metrics: Metrics;
  error?: string;
}
