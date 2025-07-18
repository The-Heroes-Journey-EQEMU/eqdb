import React, { useState } from 'react';
import { WeightSet } from '../../types/user';
import { useWeightSets } from '../../hooks/useWeightSets';
import { useAuth } from '../../contexts/AuthContext';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import WeightSetCard from './WeightSetCard';

interface WeightSetSelectorProps {
  onApplyWeights?: (weights: Array<{ stat: string; value: number }>) => void;
  onClearWeights?: () => void;
  onSelectionChange?: (selectedWeightSets: WeightSet[]) => void;
  selectedWeightSets?: WeightSet[];
  disabled?: boolean;
  showPreview?: boolean;
  className?: string;
  layout?: 'default' | 'grid';
  multiSelect?: boolean;
}

export const WeightSetSelector: React.FC<WeightSetSelectorProps> = ({
  onApplyWeights,
  onClearWeights,
  onSelectionChange,
  selectedWeightSets = [],
  disabled = false,
  showPreview = true,
  className = '',
  layout = 'default',
  multiSelect = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const { isAuthenticated } = useAuth();
  const { data: weightSets, isLoading, error } = useWeightSets();

  // Helper function to format stat names
  const formatStatName = (stat: string): string => {
    const statNames: Record<string, string> = {
      hp: 'HP',
      mana: 'Mana',
      endur: 'Endurance',
      ac: 'AC',
      astr: 'STR',
      asta: 'STA',
      aagi: 'AGI',
      adex: 'DEX',
      awis: 'WIS',
      aint: 'INT',
      acha: 'CHA',
      heroic_str: 'H-STR',
      heroic_sta: 'H-STA',
      heroic_agi: 'H-AGI',
      heroic_dex: 'H-DEX',
      heroic_wis: 'H-WIS',
      heroic_int: 'H-INT',
      heroic_cha: 'H-CHA',
      fr: 'FR',
      cr: 'CR',
      pr: 'PR',
      dr: 'DR',
      mr: 'MR',
      damage: 'DMG',
      delay: 'Delay',
      w_eff: 'W-Eff',
      attack: 'ATK',
      haste: 'Haste',
      accuracy: 'ACC',
      avoidance: 'Avoid'
    };
    
    return statNames[stat] || stat.toUpperCase();
  };



  const handleToggleWeightSet = (weightSet: WeightSet) => {
    const isSelected = selectedWeightSets.some(ws => ws.id === weightSet.id);
    let newSelection: WeightSet[];

    if (multiSelect) {
      if (isSelected) {
        // Remove from selection
        newSelection = selectedWeightSets.filter(ws => ws.id !== weightSet.id);
      } else {
        // Add to selection
        newSelection = [...selectedWeightSets, weightSet];
      }
    } else {
      // Single select mode
      if (isSelected) {
        // Deselect if already selected
        newSelection = [];
      } else {
        // Select only this one
        newSelection = [weightSet];
      }
    }

    // Notify parent of selection change
    if (onSelectionChange) {
      onSelectionChange(newSelection);
    }

    // Calculate and apply combined weights
    if (newSelection.length > 0) {
      const combinedWeights = calculateCombinedWeightsForSets(newSelection);
      if (onApplyWeights) {
        onApplyWeights(combinedWeights);
      }
    } else {
      if (onClearWeights) {
        onClearWeights();
      }
    }
  };

  const calculateCombinedWeightsForSets = (sets: WeightSet[]): Array<{ stat: string; value: number }> => {
    const combinedMap = new Map<string, number>();
    
    sets.forEach(weightSet => {
      weightSet.weights.forEach(weight => {
        const currentValue = combinedMap.get(weight.stat) || 1.0; // Start with 1.0 for multiplication
        combinedMap.set(weight.stat, currentValue * weight.value);
      });
    });
    
    // Only include stats that have a multiplier effect (not equal to 1.0)
    return Array.from(combinedMap.entries())
      .filter(([_, value]) => value !== 1.0)
      .map(([stat, value]) => ({ stat, value }));
  };

  const handleClearAllWeights = () => {
    if (onSelectionChange) {
      onSelectionChange([]);
    }
    if (onClearWeights) {
      onClearWeights();
    }
  };

  // Component for grid-style weight set cards
  const WeightSetGridCard: React.FC<{ weightSet: WeightSet; isSelected: boolean }> = ({ 
    weightSet, 
    isSelected 
  }) => {
    const topStats = weightSet.weights
      .sort((a, b) => b.value - a.value)
      .slice(0, 8); // Show top 8 stats

    return (
      <div 
        className={`relative p-4 border rounded-lg cursor-pointer transition-all duration-200 hover:shadow-md ${
          isSelected 
            ? 'border-primary bg-primary/5 ring-2 ring-primary' 
            : 'border-border hover:border-border-hover'
        }`}
        onClick={() => handleToggleWeightSet(weightSet)}
      >
        {/* Header */}
        <div className="mb-3">
          <h4 className={`font-semibold text-sm truncate ${
            isSelected ? 'text-primary' : 'text-foreground'
          }`}>
            {weightSet.name}
          </h4>
          <p className="text-xs text-muted-foreground">
            {weightSet.weights.length} stats
          </p>
        </div>

        {/* Stats List (Vertical) */}
        <div className="space-y-1 text-xs">
          {topStats.map((weight) => (
            <div key={weight.stat} className="flex justify-between">
              <span className="text-muted-foreground truncate">
                {formatStatName(weight.stat)}:
              </span>
              <span className={`font-mono font-medium ${
                weight.value < 1.0 
                  ? 'text-red-600' 
                  : 'text-green-600'
              }`}>
                {weight.value.toFixed(1)}
              </span>
            </div>
          ))}
          {weightSet.weights.length > 8 && (
            <div className="text-center text-xs text-muted-foreground mt-1">
              +{weightSet.weights.length - 8} more...
            </div>
          )}
        </div>

        {/* Selected indicator */}
        {isSelected && (
          <div className="absolute top-2 right-2">
            <div className="w-2 h-2 bg-primary rounded-full"></div>
          </div>
        )}
      </div>
    );
  };

  // Don't render if user is not authenticated
  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <Card className={className}>
        <CardBody>
          <div className="flex items-center justify-center py-4">
            <LoadingSpinner size="sm" className="mr-2" />
            <span className="text-sm text-muted-foreground">Loading weight sets...</span>
          </div>
        </CardBody>
      </Card>
    );
  }

  if (error) {
    return (
      <Card variant="outlined" className={className}>
        <CardBody>
          <div className="text-center py-4">
            <p className="text-sm text-destructive">Failed to load weight sets</p>
            <p className="text-xs text-muted-foreground mt-1">{error.message}</p>
          </div>
        </CardBody>
      </Card>
    );
  }

  if (!weightSets || weightSets.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-base">Weight Sets</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="text-center py-4">
            <p className="text-sm text-muted-foreground mb-2">No weight sets found</p>
            <Button size="sm" variant="outline" onClick={() => setIsExpanded(!isExpanded)}>
              Create Weight Set
            </Button>
          </div>
        </CardBody>
      </Card>
    );
  }

  // Grid layout for filter tab
  if (layout === 'grid') {
    return (
      <div className={className}>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-foreground">Weight Sets</h3>
            {selectedWeightSets.length > 0 && (
              <p className="text-sm text-muted-foreground">
                {selectedWeightSets.length} weight set{selectedWeightSets.length !== 1 ? 's' : ''} selected
                {multiSelect && <span className="ml-2 text-xs">(Click to toggle on/off)</span>}
              </p>
            )}
          </div>
          {selectedWeightSets.length > 0 && (
            <Button
              size="sm"
              variant="ghost"
              onClick={handleClearAllWeights}
              disabled={disabled}
              className="text-muted-foreground hover:text-foreground"
            >
              Clear All
            </Button>
          )}
        </div>

        {/* Grid of Weight Sets */}
        {weightSets && weightSets.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {weightSets.map((weightSet) => (
              <WeightSetGridCard
                key={weightSet.id}
                weightSet={weightSet}
                isSelected={selectedWeightSets.some(ws => ws.id === weightSet.id)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 border border-dashed border-border rounded-lg">
            <div className="text-muted-foreground mb-2">
              <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-sm text-muted-foreground">No weight sets available</p>
            <p className="text-xs text-muted-foreground mt-1">Create weight sets to prioritize item stats</p>
          </div>
        )}

        {/* Help Text for multi-select */}
        {multiSelect && weightSets.length > 0 && (
          <div className="mt-4 p-3 bg-muted rounded-lg">
            <div className="text-sm text-muted-foreground">
              <div className="font-medium mb-1">Multi-Select Mode</div>
              <div className="text-xs">
                Click weight sets to toggle them on/off. Selected weight sets will be multiplied together to calculate final stat multipliers.
                {selectedWeightSets.length > 0 && (
                  <span className="block mt-1">
                    Currently selected: {selectedWeightSets.map(ws => ws.name).join(', ')}
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Default card layout (for backward compatibility)
  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">
            Weight Sets
            {selectedWeightSets.length > 0 && (
              <span className="ml-2 text-sm font-normal text-muted-foreground">
                ({selectedWeightSets.length} selected)
              </span>
            )}
          </CardTitle>
          <div className="flex items-center space-x-2">
            {selectedWeightSets.length > 0 && (
              <Button
                size="sm"
                variant="ghost"
                onClick={handleClearAllWeights}
                disabled={disabled}
                className="text-muted-foreground hover:text-foreground"
              >
                Clear
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setIsExpanded(!isExpanded)}
              disabled={disabled}
              className="text-muted-foreground hover:text-foreground"
            >
              {isExpanded ? 'Hide' : 'Select'}
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardBody>
        {/* Selected Weight Sets Preview */}
        {selectedWeightSets.length > 0 && showPreview && !isExpanded && (
          <div className="mb-4 space-y-2">
            {selectedWeightSets.map((weightSet) => (
              <WeightSetCard
                key={weightSet.id}
                weightSet={weightSet}
                showActions={false}
                isApplied={true}
                className="border-primary"
              />
            ))}
          </div>
        )}

        {/* Quick Apply Buttons */}
        {!isExpanded && weightSets.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm text-muted-foreground mb-2">Quick Apply:</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {weightSets.slice(0, 4).map((weightSet) => (
                <Button
                  key={weightSet.id}
                  size="sm"
                  variant={selectedWeightSets.some(ws => ws.id === weightSet.id) ? "primary" : "outline"}
                  onClick={() => handleToggleWeightSet(weightSet)}
                  disabled={disabled}
                  className="justify-start text-left"
                >
                  <div className="flex-1 truncate">
                    <div className="font-medium">{weightSet.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {weightSet.weights.length} stats
                    </div>
                  </div>
                </Button>
              ))}
            </div>
            {weightSets.length > 4 && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsExpanded(true)}
                disabled={disabled}
                className="w-full text-muted-foreground hover:text-foreground"
              >
                View all {weightSets.length} weight sets...
              </Button>
            )}
          </div>
        )}

        {/* Expanded Weight Set List */}
        {isExpanded && (
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground">
              {multiSelect ? 'Select multiple weight sets to combine:' : 'Select a weight set to apply:'}
            </div>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {weightSets.map((weightSet) => (
                <WeightSetCard
                  key={weightSet.id}
                  weightSet={weightSet}
                  onApply={() => handleToggleWeightSet(weightSet)}
                  showActions={false}
                  isApplied={selectedWeightSets.some(ws => ws.id === weightSet.id)}
                  className="cursor-pointer"
                />
              ))}
            </div>
            
            <div className="flex justify-between items-center pt-2 border-t border-border">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsExpanded(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                Collapse
              </Button>
              
              <div className="text-xs text-muted-foreground">
                {weightSets.length} weight set{weightSets.length !== 1 ? 's' : ''} available
              </div>
            </div>
          </div>
        )}

        {/* Help Text */}
        {selectedWeightSets.length === 0 && !isExpanded && (
          <div className="mt-4 p-3 bg-muted rounded-lg">
            <div className="text-sm text-muted-foreground">
              <div className="font-medium mb-1">Weight Sets</div>
              <div className="text-xs">
                Apply saved stat weights to prioritize items based on your preferences. 
                Weight sets calculate scores for each item to help you find the best gear.
                {multiSelect && ' You can select multiple weight sets to multiply their effects together.'}
              </div>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default WeightSetSelector; 