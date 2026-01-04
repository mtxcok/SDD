<template>
  <a-layout class="layout-container">
    <a-layout-header class="header">
      <div class="logo">资源管理器</div>
      <div class="header-right">
        <a-button type="link" @click="logout" class="logout-btn">退出登录</a-button>
      </div>
    </a-layout-header>
    <a-layout-content class="content">
      <div class="content-wrapper">
        <div class="page-header">
          <h2>节点管理</h2>
          <a-button type="primary" @click="refreshAgents">刷新列表</a-button>
        </div>
        
        <a-card :bordered="false" class="table-card">
          <a-table :dataSource="agentsStore.agents" :columns="columns" :loading="agentsStore.loading" rowKey="id">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-badge :status="record.status === 'online' ? 'success' : 'default'" :text="record.status.toUpperCase()" />
              </template>
              <template v-if="column.key === 'cpu'">
                {{ record.cpu != null ? record.cpu.toFixed(1) + '%' : '-' }}
              </template>
              <template v-if="column.key === 'mem'">
                {{ record.mem != null ? record.mem.toFixed(1) + '%' : '-' }}
              </template>
              <template v-if="column.key === 'active_allocations'">
                {{ record.active_allocations?.length || 0 }}
              </template>
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-popconfirm
                    title="确定要启动新的 code-server 会话吗？"
                    ok-text="是"
                    cancel-text="否"
                    @confirm="startSession(record.id)"
                  >
                    <a-button type="primary" size="small">启动会话</a-button>
                  </a-popconfirm>
                  <a-popconfirm
                    title="确定要删除此节点吗？"
                    ok-text="是"
                    cancel-text="否"
                    @confirm="deleteAgent(record.id)"
                  >
                    <a-button danger size="small">删除</a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
            
            <!-- Expanded Row for Allocations -->
            <template #expandedRowRender="{ record }">
              <div class="expanded-row" v-if="record.active_allocations && record.active_allocations.length > 0">
                  <h4>{{ record.name }} 的活跃会话</h4>
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
                              <span v-else class="text-muted">等待 URL...</span>
                          </template>
                          <template v-if="column.key === 'action'">
                              <a-space>
                                  <a-button size="small" v-if="allocation.access_url" @click="copyLink(allocation.access_url)">复制</a-button>
                                  <a-popconfirm
                                    title="停止此会话？"
                                    ok-text="是"
                                    cancel-text="否"
                                    @confirm="stopSession(allocation.id)"
                                  >
                                    <a-button danger size="small">停止</a-button>
                                  </a-popconfirm>
                              </a-space>
                          </template>
                      </template>
                  </a-table>
              </div>
              <div v-else class="expanded-row">
                  <p>无活跃会话。</p>
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
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: 'IP 地址', dataIndex: 'ip', key: 'ip' },
  { title: 'CPU', key: 'cpu' },
  { title: '内存', key: 'mem' },
  { title: '最后在线', dataIndex: 'last_seen_at', key: 'last_seen_at' },
  { title: '活跃会话', key: 'active_allocations' },
  { title: '操作', key: 'action' },
];

const allocationColumns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: '状态', dataIndex: 'status', key: 'status' },
    { title: '端口', dataIndex: 'remote_port', key: 'remote_port' },
    { title: '访问链接', key: 'access_url' },
    { title: '操作', key: 'action', width: '150px' },
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
  message.loading({ content: '正在启动会话...', key: 'startSession' });
  const success = await allocationsStore.createAllocation(agentId);
  if (success) {
    message.success({ content: '会话已启动！', key: 'startSession' });
  } else {
    message.error({ content: '启动会话失败', key: 'startSession' });
  }
};

const deleteAgent = async (agentId: number) => {
  const success = await agentsStore.deleteAgent(agentId);
  if (success) {
    message.success('节点已删除');
  } else {
    message.error('删除节点失败');
  }
};

const stopSession = async (allocationId: number) => {
    const success = await allocationsStore.releaseAllocation(allocationId);
    if (success) {
        message.success('正在停止会话...');
    } else {
        message.error('停止会话失败');
    }
}

const copyLink = (url: string) => {
    navigator.clipboard.writeText(url).then(() => {
        message.success('链接已复制到剪贴板');
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
