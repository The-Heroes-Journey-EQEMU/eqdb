import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services/userService';
import { WeightSet, CreateWeightSetRequest, UpdateWeightSetRequest } from '../types/user';
import { useAuth } from '../contexts/AuthContext';
import { useMemo } from 'react';

/**
 * Hook to fetch all weight sets for the current user
 */
export const useWeightSets = () => {
  const { user, isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['user', 'weight-sets'],
    queryFn: () => userService.getWeightSets(),
    enabled: isAuthenticated && !!user,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000,   // 10 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on authentication errors
      if (error?.response?.status === 401) {
        return false;
      }
      return failureCount < 3;
    }
  });
};

/**
 * Hook to fetch a specific weight set by ID
 */
export const useWeightSet = (id: number, enabled = true) => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['user', 'weight-sets', id],
    queryFn: () => userService.getWeightSet(id),
    enabled: enabled && isAuthenticated && !!id,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000
  });
};

/**
 * Hook to create a new weight set
 */
export const useCreateWeightSet = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateWeightSetRequest) => userService.createWeightSet(data),
    onSuccess: (newWeightSet) => {
      // Update the weight sets list cache
      queryClient.setQueryData(['user', 'weight-sets'], (oldData: WeightSet[] = []) => {
        return [...oldData, newWeightSet];
      });
      
      // Also cache the individual weight set
      queryClient.setQueryData(['user', 'weight-sets', newWeightSet.id], newWeightSet);
      
      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ 
        queryKey: ['user', 'weight-sets'],
        exact: false 
      });
    },
    onError: (error: any) => {
      console.error('Failed to create weight set:', error);
    }
  });
};

/**
 * Hook to update an existing weight set
 */
export const useUpdateWeightSet = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateWeightSetRequest }) => 
      userService.updateWeightSet(id, data),
    onSuccess: (updatedWeightSet, { id }) => {
      // Update the individual weight set cache
      queryClient.setQueryData(['user', 'weight-sets', id], updatedWeightSet);
      
      // Update the weight sets list cache
      queryClient.setQueryData(['user', 'weight-sets'], (oldData: WeightSet[] = []) => {
        return oldData.map(ws => ws.id === id ? updatedWeightSet : ws);
      });
      
      // Invalidate to ensure consistency
      queryClient.invalidateQueries({ 
        queryKey: ['user', 'weight-sets'],
        exact: false 
      });
    },
    onError: (error: any) => {
      console.error('Failed to update weight set:', error);
    }
  });
};

/**
 * Hook to delete a weight set
 */
export const useDeleteWeightSet = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => userService.deleteWeightSet(id),
    onSuccess: (_, deletedId) => {
      // Remove from weight sets list cache
      queryClient.setQueryData(['user', 'weight-sets'], (oldData: WeightSet[] = []) => {
        return oldData.filter(ws => ws.id !== deletedId);
      });
      
      // Remove the individual weight set cache
      queryClient.removeQueries({ 
        queryKey: ['user', 'weight-sets', deletedId] 
      });
      
      // Invalidate to ensure consistency
      queryClient.invalidateQueries({ 
        queryKey: ['user', 'weight-sets'],
        exact: false 
      });
    },
    onError: (error: any) => {
      console.error('Failed to delete weight set:', error);
    }
  });
};

/**
 * Hook to duplicate a weight set
 */
export const useDuplicateWeightSet = () => {
  const createWeightSet = useCreateWeightSet();
  
  return useMutation({
    mutationFn: async (originalWeightSet: WeightSet) => {
      const duplicateData: CreateWeightSetRequest = {
        name: `${originalWeightSet.name} (Copy)`,
        description: originalWeightSet.description,
        weights: [...originalWeightSet.weights]
      };
      
      return createWeightSet.mutateAsync(duplicateData);
    },
    onError: (error: any) => {
      console.error('Failed to duplicate weight set:', error);
    }
  });
};

/**
 * Utility hook to convert weight set to search parameters
 */
export const useWeightSetToSearchParams = () => {
  return {
    convertToSearchParams: (weightSet: WeightSet | null) => {
      if (!weightSet || !weightSet.weights.length) {
        return {
          stat_weights: undefined,
          show_weight_detail: false
        };
      }
      
      return {
        stat_weights: weightSet.weights,
        show_weight_detail: true
      };
    }
  };
};

/**
 * Hook to validate weight set data
 */
export const useWeightSetValidation = () => {
  return {
    validateWeightSet: (data: Partial<CreateWeightSetRequest>) => {
      const errors: Record<string, string> = {};
      
      if (!data.name?.trim()) {
        errors.name = 'Weight set name is required';
      } else if (data.name.trim().length < 2) {
        errors.name = 'Weight set name must be at least 2 characters';
      } else if (data.name.trim().length > 50) {
        errors.name = 'Weight set name must be less than 50 characters';
      }
      
      if (!data.weights || data.weights.length === 0) {
        errors.weights = 'At least one stat weight is required';
      } else {
        // Check for duplicate stats
        const statCounts: Record<string, number> = {};
        data.weights.forEach(weight => {
          if (weight.stat) {
            statCounts[weight.stat] = (statCounts[weight.stat] || 0) + 1;
          }
        });
        
        const duplicates = Object.entries(statCounts)
          .filter(([_, count]) => count > 1)
          .map(([stat, _]) => stat);
        
        if (duplicates.length > 0) {
          errors.weights = `Duplicate stats found: ${duplicates.join(', ')}`;
        }
        
        // Check for invalid weights
        const invalidWeights = data.weights.filter(weight => 
          !weight.stat || 
          typeof weight.value !== 'number' || 
          isNaN(weight.value) ||
          weight.value < 0
        );
        
        if (invalidWeights.length > 0) {
          errors.weights = 'All weights must have valid stat names and positive numeric values';
        }
      }
      
      return {
        isValid: Object.keys(errors).length === 0,
        errors
      };
    }
  };
};

/**
 * Hook to get weight set statistics
 */
export const useWeightSetStats = (weightSet: WeightSet | null) => {
  return useMemo(() => {
    if (!weightSet) {
      return {
        totalWeights: 0,
        maxWeight: 0,
        minWeight: 0,
        avgWeight: 0,
        statCategories: []
      };
    }
    
    const weights = weightSet.weights.map(w => w.value);
    const totalWeights = weights.length;
    const maxWeight = Math.max(...weights);
    const minWeight = Math.min(...weights);
    const avgWeight = weights.reduce((sum, w) => sum + w, 0) / totalWeights;
    
    // Group stats by category (simplified categorization)
    const statCategories = weightSet.weights.reduce((acc, weight) => {
      let category = 'Other';
      
      if (['hp', 'mana', 'endur', 'ac'].includes(weight.stat)) {
        category = 'Basic Attributes';
      } else if (weight.stat.startsWith('heroic_')) {
        category = 'Heroic Stats';
      } else if (['astr', 'asta', 'aagi', 'adex', 'awis', 'aint', 'acha'].includes(weight.stat)) {
        category = 'Base Stats';
      } else if (['fr', 'cr', 'pr', 'dr', 'mr'].includes(weight.stat)) {
        category = 'Resists';
      } else if (['damage', 'delay', 'w_eff'].includes(weight.stat)) {
        category = 'Weapon Stats';
      }
      
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return {
      totalWeights,
      maxWeight,
      minWeight,
      avgWeight: Number(avgWeight.toFixed(2)),
      statCategories: Object.entries(statCategories).map(([name, count]) => ({
        name,
        count
      }))
    };
  }, [weightSet]);
};

// Re-export types for convenience
export type { WeightSet, CreateWeightSetRequest, UpdateWeightSetRequest }; 