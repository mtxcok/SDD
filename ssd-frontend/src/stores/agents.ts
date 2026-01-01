import { defineStore } from 'pinia';
import { ref } from 'vue';
import { agentsApi, allocationsApi, type Agent, type Allocation } from '../api';

export const useAgentsStore = defineStore('agents', () => {
  const agents = ref<Agent[]>([]);
  const loading = ref(false);

  const fetchAgents = async () => {
    loading.value = true;
    try {
      const [agentsResponse, allocationsResponse] = await Promise.all([
        agentsApi.list(),
        allocationsApi.list()
      ]);
      
      const fetchedAgents = agentsResponse.data;
      const fetchedAllocations = allocationsResponse.data;

      // Map allocations to agents
      agents.value = fetchedAgents.map(agent => {
        const agentAllocations = fetchedAllocations.filter(a => a.agent_id === agent.id);
        return {
          ...agent,
          active_allocations: agentAllocations
        };
      });

    } catch (error) {
      console.error('Failed to fetch agents or allocations', error);
    } finally {
      loading.value = false;
    }
  };

  return {
    agents,
    loading,
    fetchAgents,
  };
});

