import React, { useState } from 'react';
import { WeightSet } from '../../types/user';
import { useWeightSetStats, useDeleteWeightSet, useDuplicateWeightSet } from '../../hooks/useWeightSets';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';

interface WeightSetCardProps {
  weightSet: WeightSet;
  onEdit?: (weightSet: WeightSet) => void;
  onApply?: (weightSet: WeightSet) => void;
  showActions?: boolean;
  isApplied?: boolean;
  className?: string;
}

export const WeightSetCard: React.FC<WeightSetCardProps> = ({
  weightSet,
  onEdit,
  onApply,
  showActions = true,
  isApplied = false,
  className = ''
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDuplicating, setIsDuplicating] = useState(false);
  
  const stats = useWeightSetStats(weightSet);
  const deleteWeightSet = useDeleteWeightSet();
  const duplicateWeightSet = useDuplicateWeightSet();

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete "${weightSet.name}"?`)) {
      setIsDeleting(true);
      try {
        await deleteWeightSet.mutateAsync(weightSet.id);
      } catch (error) {
        console.error('Failed to delete weight set:', error);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  const handleDuplicate = async () => {
    setIsDuplicating(true);
    try {
      await duplicateWeightSet.mutateAsync(weightSet);
    } catch (error) {
      console.error('Failed to duplicate weight set:', error);
    } finally {
      setIsDuplicating(false);
    }
  };

  const formatStatName = (stat: string): string => {
    const statNames: Record<string, string> = {
      hp: 'Hit Points',
      mana: 'Mana',
      endur: 'Endurance',
      ac: 'Armor Class',
      astr: 'Strength',
      asta: 'Stamina',
      aagi: 'Agility',
      adex: 'Dexterity',
      awis: 'Wisdom',
      aint: 'Intelligence',
      acha: 'Charisma',
      heroic_str: 'Heroic Strength',
      heroic_sta: 'Heroic Stamina',
      heroic_agi: 'Heroic Agility',
      heroic_dex: 'Heroic Dexterity',
      heroic_wis: 'Heroic Wisdom',
      heroic_int: 'Heroic Intelligence',
      heroic_cha: 'Heroic Charisma',
      fr: 'Fire Resist',
      cr: 'Cold Resist',
      pr: 'Poison Resist',
      dr: 'Disease Resist',
      mr: 'Magic Resist',
      damage: 'Damage',
      delay: 'Delay',
      w_eff: 'Weapon Efficiency',
      attack: 'Attack',
      haste: 'Haste',
      accuracy: 'Accuracy',
      avoidance: 'Avoidance'
    };
    
    return statNames[stat] || stat.charAt(0).toUpperCase() + stat.slice(1);
  };

  // Split weights into two columns: < 1.0 and >= 1.0
  const lowWeights = weightSet.weights.filter(w => w.value < 1.0).sort((a, b) => b.value - a.value);
  const highWeights = weightSet.weights.filter(w => w.value >= 1.0).sort((a, b) => b.value - a.value);

  return (
    <Card 
      hover={!isApplied} 
      variant={isApplied ? "elevated" : "default"}
      className={`transition-all duration-200 ${isApplied ? 'ring-2 ring-primary' : ''} ${className}`}
    >
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <CardTitle className={`text-lg ${isApplied ? 'text-primary' : 'text-foreground'}`}>
              {weightSet.name}
              {isApplied && (
                <span className="ml-2 text-sm font-normal text-primary">(Applied)</span>
              )}
            </CardTitle>
            {weightSet.description && (
              <p className="text-sm text-muted-foreground mt-1">{weightSet.description}</p>
            )}
          </div>
          
          {showActions && (
            <div className="flex items-center space-x-2">
              {onApply && !isApplied && (
                <Button 
                  size="sm" 
                  variant="primary"
                  onClick={() => onApply(weightSet)}
                >
                  Apply
                </Button>
              )}
              
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowDetails(!showDetails)}
                className="text-muted-foreground hover:text-foreground"
              >
                {showDetails ? 'Hide' : 'Details'}
              </Button>
            </div>
          )}
        </div>
      </CardHeader>

      <CardBody>
        {/* Weight Set Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-foreground">{stats.totalWeights}</div>
            <div className="text-xs text-muted-foreground">Stats</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.maxWeight}</div>
            <div className="text-xs text-muted-foreground">Max Weight</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.avgWeight}</div>
            <div className="text-xs text-muted-foreground">Avg Weight</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{stats.statCategories.length}</div>
            <div className="text-xs text-muted-foreground">Categories</div>
          </div>
        </div>

        {/* Two-Column Weight Display */}
        <div className="grid grid-cols-2 gap-4">
          {/* Low Weights (< 1.0) */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-muted-foreground border-b border-border pb-1">
              Weights &lt; 1.0
            </h4>
            {lowWeights.length > 0 ? (
              <div className="space-y-1">
                {lowWeights.slice(0, showDetails ? undefined : 3).map((weight) => (
                  <div key={weight.stat} className="flex justify-between items-center text-sm">
                    <span className="text-foreground">{formatStatName(weight.stat)}</span>
                    <span className="font-mono text-muted-foreground">{weight.value.toFixed(2)}</span>
                  </div>
                ))}
                {!showDetails && lowWeights.length > 3 && (
                  <div className="text-xs text-muted-foreground">
                    +{lowWeights.length - 3} more...
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground italic">None</div>
            )}
          </div>

          {/* High Weights (>= 1.0) */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-muted-foreground border-b border-border pb-1">
              Weights ≥ 1.0
            </h4>
            {highWeights.length > 0 ? (
              <div className="space-y-1">
                {highWeights.slice(0, showDetails ? undefined : 3).map((weight) => (
                  <div key={weight.stat} className="flex justify-between items-center text-sm">
                    <span className="text-foreground">{formatStatName(weight.stat)}</span>
                    <span className="font-mono text-muted-foreground">{weight.value.toFixed(2)}</span>
                  </div>
                ))}
                {!showDetails && highWeights.length > 3 && (
                  <div className="text-xs text-muted-foreground">
                    +{highWeights.length - 3} more...
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground italic">None</div>
            )}
          </div>
        </div>

        {/* Detailed View */}
        {showDetails && (
          <div className="mt-4 pt-4 border-t border-border">
            <h4 className="text-sm font-medium text-foreground mb-3">All Weights</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {weightSet.weights
                .sort((a, b) => b.value - a.value)
                .map((weight) => (
                  <div key={weight.stat} className="flex justify-between items-center py-1 px-2 bg-muted rounded text-sm">
                    <span className="text-foreground">{formatStatName(weight.stat)}</span>
                    <span className="font-mono text-muted-foreground font-medium">{weight.value.toFixed(2)}</span>
                  </div>
                ))}
            </div>

            {/* Category Breakdown */}
            {stats.statCategories.length > 0 && (
              <div className="mt-4">
                <h5 className="text-sm font-medium text-foreground mb-2">Categories</h5>
                <div className="flex flex-wrap gap-2">
                  {stats.statCategories.map((category) => (
                    <span 
                      key={category.name}
                      className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded"
                    >
                      {category.name} ({category.count})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        {showActions && (
          <div className="flex justify-between items-center mt-4 pt-4 border-t border-border">
            <div className="text-xs text-muted-foreground">
              Created: {new Date(weightSet.created_at).toLocaleDateString()}
            </div>
            
            <div className="flex space-x-2">
              <Button
                size="sm"
                variant="ghost"
                onClick={handleDuplicate}
                disabled={isDuplicating}
                className="text-muted-foreground hover:text-foreground"
              >
                {isDuplicating ? <LoadingSpinner size="sm" /> : 'Duplicate'}
              </Button>
              
              {onEdit && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => onEdit(weightSet)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  Edit
                </Button>
              )}
              
              <Button
                size="sm"
                variant="ghost"
                onClick={handleDelete}
                disabled={isDeleting}
                className="text-destructive hover:text-destructive hover:bg-destructive/10"
              >
                {isDeleting ? <LoadingSpinner size="sm" /> : 'Delete'}
              </Button>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default WeightSetCard; 