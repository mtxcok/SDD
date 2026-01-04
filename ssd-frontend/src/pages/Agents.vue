<template>
  <a-layout class="layout-container">
    <a-layout-header class="header">
      <div class="logo">Resource Manager</div>
      <div class="header-right">
        <a-button type="link" @click="logout" class="logout-btn">Logout</a-button>
      </div>
    </a-layout-header>
    <a-layout-content class="content">
      <div class="content-wrapper">
        <div class="page-header">
          <h2>Agent Management</h2>
          <a-button type="primary" @click="refreshAgents">Refresh List</a-button>
        </div>
        
        <a-card :bordered="false" class="table-card">
          <a-table :dataSource="agentsStore.agents" :columns="columns" :loading="agentsStore.loading" rowKey="id">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-badge :status="record.status === 'online' ? 'success' : 'default'" :text="record.status.toUpperCase()" />
              </template>
              <template v-if="column.key === 'active_allocations'">
                {{ record.active_allocations?.length || 0 }}
              </template>
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-popconfirm
                    title="Are you sure start a new code-server session?"
                    ok-text="Yes"
                    cancel-text="No"
                    @confirm="startSession(record.id)"
                  >
                    <a-button type="primary" size="small">Start Session</a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
            
            <!-- Expanded Row for Allocations -->
            <template #expandedRowRender="{ record }">
              <div class="expanded-row" v-if="record.active_allocations && record.active_allocations.length > 0">
                  <h4>Active Sessions for {{ record.name }}</h4>
                  <a-table 
                      :dataSource="record.active_allocations" 
                      :columns="allocationColumns" 
                      rowKey="id" 
                      pagination="false"
                      size="small"
                      :bordered="true"
                  >
                      <template #bodyCell="{ column, record: allocation }">
                          <template v-if="column.key === 'status'">
                             <a-tag :color="getAllocationStatusColor(allocation.status)">
                                {{ allocation.status.toUpperCase() }}
                             </a-tag>
                          </template>
                          <template v-if="column.key === 'access_url'">
                              <a :href="allocation.access_url" target="_blank" v-if="allocation.access_url">{{ allocation.access_url }}</a>
                              <span v-else-if="allocation.status === 'active' && allocation.remote_port">
                                  <a :href="`http://127.0.0.1:${allocation.remote_port}`" target="_blank">http://127.0.0.1:{{ allocation.remote_port }}</a>
                              </span>
                              <span v-else class="text-muted">Waiting for URL...</span>
                          </template>
                          <template v-if="column.key === 'action'">
                              <a-space>
                                  <a-button size="small" v-if="allocation.access_url" @click="copyLink(allocation.access_url)">Copy</a-button>
                                  <a-popconfirm
                                    title="Stop this session?"
                                    ok-text="Yes"
                                    cancel-text="No"
                                    @confirm="stopSession(allocation.id)"
                                  >
                                    <a-button danger size="small">Stop</a-button>
                                  </a-popconfirm>
                              </a-space>
                          </template>
                      </template>
                  </a-table>
              </div>
              <div v-else class="expanded-row">
                  <p>No active sessions.</p>
              </div>
            </template>
          </a-table>
        </a-card>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script lang="ts" setup>
import { onMounted } from 'vue';
import { useAgentsStore } from '../stores/agents';
import { useAllocationsStore } from '../stores/allocations';
import { useAuthStore } from '../stores/auth';
import { message } from 'ant-design-vue';
import { usePolling } from '../composables/usePolling';
import type { Agent, Allocation } from '../types';

const agentsStore = useAgentsStore();
const allocationsStore = useAllocationsStore();
const authStore = useAuthStore();

const columns = [
  { title: 'Name', dataIndex: 'name', key: 'name' },
  { title: 'Status', dataIndex: 'status', key: 'status' },
  { title: 'IP Address', dataIndex: 'ip', key: 'ip' },
  { title: 'Last Seen', dataIndex: 'last_seen_at', key: 'last_seen_at' },
  { title: 'Active Sessions', key: 'active_allocations' },
  { title: 'Action', key: 'action' },
];

const allocationColumns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
    { title: 'Port', dataIndex: 'remote_port', key: 'remote_port' },
    { title: 'Access Link', key: 'access_url' },
    { title: 'Action', key: 'action', width: '150px' },
];

const refreshAgents = () => {
  agentsStore.fetchAgents();
};

// Poll every 10 seconds
usePolling(refreshAgents, 10000);

onMounted(() => {
    refreshAgents();
});

const logout = () => {
    authStore.logout();
}

const startSession = async (agentId: number) => {
  message.loading({ content: 'Starting session...', key: 'startSession' });
  const success = await allocationsStore.createAllocation(agentId);
  if (success) {
    message.success({ content: 'Session started!', key: 'startSession' });
  } else {
    message.error({ content: 'Failed to start session', key: 'startSession' });
  }
};

const stopSession = async (allocationId: number) => {
    const success = await allocationsStore.releaseAllocation(allocationId);
    if (success) {
        message.success('Session stopping...');
    } else {
        message.error('Failed to stop session');
    }
}

const copyLink = (url: string) => {
    navigator.clipboard.writeText(url).then(() => {
        message.success('Link copied to clipboard');
    });
}

const getAllocationStatusColor = (status: string) => {
    switch (status) {
        case 'active': return 'green';
        case 'starting': return 'blue';
        case 'releasing': return 'orange';
        case 'released': return 'red';
        default: return 'default';
    }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #f7faff 0%, #eef1f7 35%, #ffffff 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  background: #001529;
  color: white;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: white;
}

.logout-btn {
  color: rgba(255, 255, 255, 0.65);
}

.logout-btn:hover {
  color: white;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  background: transparent;
  overflow: auto;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.table-card {
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02);
}

.expanded-row {
    padding: 16px;
    background: #fafafa;
    border-radius: 4px;
}

.text-muted {
    color: #999;
}
</style>
