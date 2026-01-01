import type { Agent, Allocation } from '../types';

export const mockAgents: Agent[] = [
  { id: '1', name: 'Agent-001', status: 'online', last_seen_at: '2023-10-27 10:00:00', ip: '192.168.1.101', active_allocations: 1 },
  { id: '2', name: 'Agent-002', status: 'offline', last_seen_at: '2023-10-26 15:30:00', ip: '192.168.1.102', active_allocations: 0 },
  { id: '3', name: 'Agent-GPU-01', status: 'online', last_seen_at: '2023-10-27 10:05:00', ip: '192.168.1.201', active_allocations: 2 },
];

export const mockAllocations: Record<string, Allocation[]> = {
  '1': [
    { id: 'alloc-1', status: 'active', remote_port: 8080, access_url: 'http://localhost:8080', created_at: '2023-10-27 09:00:00' }
  ],
  '3': [
    { id: 'alloc-2', status: 'active', remote_port: 8081, access_url: 'http://localhost:8081', created_at: '2023-10-27 09:30:00' },
    { id: 'alloc-3', status: 'starting', remote_port: 8082, access_url: '', created_at: '2023-10-27 10:00:00' }
  ]
};

export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
