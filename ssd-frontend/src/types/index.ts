export interface User {
  username: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export enum AgentStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
}

export enum AllocationStatus {
  REQUESTED = 'requested',
  STARTING = 'starting',
  ACTIVE = 'active',
  RELEASING = 'releasing',
  RELEASED = 'released',
  FAILED = 'failed',
}

export interface Agent {
  id: number;
  name: string;
  status: AgentStatus;
  last_seen_at: string | null;
  ip: string | null;
  // Frontend specific property to hold allocations
  active_allocations?: Allocation[];
}

export interface Allocation {
  id: number;
  agent_id: number;
  service: string;
  remote_port: number;
  status: AllocationStatus;
  access_url: string | null;
  created_at: string;
}

export interface AllocationCreate {
  agent_id: number;
  service: string;
}
