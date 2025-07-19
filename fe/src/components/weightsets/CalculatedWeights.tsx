import React from 'react';
import { WeightSet } from '../../types/user';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';

interface CalculatedWeightsProps {
  selectedWeightSets: WeightSet[];
  className?: string;
  compact?: boolean;
}

export const CalculatedWeights: React.FC<CalculatedWeightsProps> = ({
  selectedWeightSets,
  className = '',
  compact = false
}) => {
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

  // Calculate combined weights from all selected weight sets
  const calculateCombinedWeights = (): Array<{ stat: string; value: number }> => {
    const combinedMap = new Map<string, number>();
    
    selectedWeightSets.forEach(weightSet => {
      weightSet.weights.forEach(weight => {
        const currentValue = combinedMap.get(weight.stat) || 1.0; // Start with 1.0 for multiplication
        combinedMap.set(weight.stat, currentValue * weight.value);
      });
    });
    
    // Only include stats that have a multiplier effect (not equal to 1.0)
    return Array.from(combinedMap.entries())
      .filter(([_, value]) => value !== 1.0)
      .map(([stat, value]) => ({ stat, value }))
      .sort((a, b) => b.value - a.value);
  };

  const combinedWeights = calculateCombinedWeights();

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className={compact ? "text-sm" : "text-base"}>
          Weights
        </CardTitle>
        <p className="text-xs text-muted-foreground">
          {selectedWeightSets.length === 0 
            ? 'No weight sets selected'
            : selectedWeightSets.length === 1 
              ? `From: ${selectedWeightSets[0].name}`
              : `From ${selectedWeightSets.length} weight sets`
          }
        </p>
      </CardHeader>
      <CardBody>
        {selectedWeightSets.length === 0 ? null : (
          <>
            {/* Selected Weight Sets Summary - Only show in non-compact mode */}
            {!compact && selectedWeightSets.length > 1 && (
              <div className="mb-4 p-3 bg-muted rounded-lg">
                <h4 className="text-sm font-medium text-foreground mb-2">
                  Active Weight Sets:
                </h4>
                <div className="space-y-1">
                  {selectedWeightSets.map((weightSet) => (
                    <div key={weightSet.id} className="flex justify-between text-xs">
                      <span className="text-muted-foreground truncate">
                        {weightSet.name}
                      </span>
                      <span className="text-muted-foreground">
                        {weightSet.weights.length} stats
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Combined Weights Display */}
            <div className="space-y-1">
              <h4 className={`font-medium text-foreground mb-3 ${compact ? 'text-xs' : 'text-sm'}`}>
                {compact ? 'Stat Multipliers:' : 'Combined Stat Multipliers:'}
              </h4>
              <div className={`overflow-y-auto space-y-1 ${compact ? 'max-h-48' : 'max-h-64'}`}>
                {combinedWeights.slice(0, compact ? 10 : undefined).map((weight) => (
                  <div key={weight.stat} className="flex justify-between items-center py-1">
                    <span className={`text-foreground truncate ${compact ? 'text-xs' : 'text-sm'}`}>
                      {formatStatName(weight.stat)}
                    </span>
                    <span className={`font-mono font-medium ${compact ? 'text-xs' : 'text-sm'} ${
                      weight.value < 1.0 
                        ? 'text-red-600' 
                        : 'text-green-600'
                    }`}>
                      {weight.value.toFixed(2)}
                    </span>
                  </div>
                ))}
                {compact && combinedWeights.length > 10 && (
                  <div className="text-center py-1">
                    <p className="text-xs text-muted-foreground">
                      +{combinedWeights.length - 10} more...
                    </p>
                  </div>
                )}
              </div>
              
              {combinedWeights.length === 0 && (
                <div className={`text-center ${compact ? 'py-2' : 'py-4'}`}>
                  <p className={`text-muted-foreground ${compact ? 'text-xs' : 'text-sm'}`}>
                    No weights to display
                  </p>
                </div>
              )}
            </div>

            {/* Stats Summary - Only show in non-compact mode */}
            {!compact && combinedWeights.length > 0 && (
              <div className="mt-4 pt-3 border-t border-border">
                <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
                  <div>
                    <span className="font-medium">Total Stats:</span> {combinedWeights.length}
                  </div>
                  <div>
                    <span className="font-medium">Avg Weight:</span> {
                      (combinedWeights.reduce((sum, w) => sum + w.value, 0) / combinedWeights.length).toFixed(2)
                    }
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </CardBody>
    </Card>
  );
};

export default CalculatedWeights; 