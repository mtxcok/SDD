import { defineStore } from 'pinia';
import { ref } from 'vue';
import { allocationsApi, type Allocation } from '../api';
import { useAgentsStore } from './agents';

export const useAllocationsStore = defineStore('allocations', () => {
  const loading = ref(false);
  const agentsStore = useAgentsStore();

  const createAllocation = async (agentId: number) => {
    loading.value = true;
    try {
      await allocationsApi.create({ agent_id: agentId, service: 'code_server' });
      // Refresh agents to get updated allocations
      await agentsStore.fetchAgents();
      return true;
    } catch (error) {
      console.error('Failed to create allocation', error);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const releaseAllocation = async (id: number) => {
    loading.value = true;
    try {
      await allocationsApi.release(id);
      // Refresh agents to get updated allocations
      await agentsStore.fetchAgents();
      return true;
    } catch (error) {
      console.error('Failed to release allocation', error);
      return false;
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    createAllocation,
    releaseAllocation,
  };
});

