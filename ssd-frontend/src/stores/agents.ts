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
        // Filter allocations that are NOT released
        const agentAllocations = fetchedAllocations.filter(a => 
            a.agent_id === agent.id && a.status !== 'released'
        );
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

  const deleteAgent = async (id: number) => {
    try {
      await agentsApi.delete(id);
      await fetchAgents();
      return true;
    } catch (error) {
      console.error('Failed to delete agent', error);
      return false;
    }
  };

  return {
    agents,
    loading,
    fetchAgents,
    deleteAgent,
  };
});

