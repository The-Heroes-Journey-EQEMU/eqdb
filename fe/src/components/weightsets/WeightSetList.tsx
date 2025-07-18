import React, { useState } from 'react';
import { useWeightSets } from '../../hooks/useWeightSets';
import Card, { CardBody } from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { SkeletonList } from '../common/Skeleton';
import { WeightSet } from '../../types/user';
import WeightSetCard from './WeightSetCard';

export const WeightSetList: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { data: weightSets, isLoading, error } = useWeightSets();

  if (isLoading) {
    return (
      <Card>
        <CardBody>
          <div className="text-center py-8">
            <LoadingSpinner size="lg" className="mx-auto mb-4" />
            <p className="text-muted-foreground">Loading weight sets...</p>
          </div>
          <SkeletonList count={3} />
        </CardBody>
      </Card>
    );
  }

  if (error) {
    return (
      <Card variant="outlined">
        <CardBody>
          <div className="text-center py-8">
            <div className="text-destructive mb-4">
              <svg className="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="text-destructive font-medium">Error loading weight sets</p>
            <p className="text-destructive/80 text-sm mt-1">
              {error instanceof Error ? error.message : 'An unknown error occurred'}
            </p>
          </div>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Weight Sets</h1>
          <p className="text-muted-foreground">
            Manage your stat weight configurations for item optimization
          </p>
        </div>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          leftIcon={
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          }
        >
          Create Weight Set
        </Button>
      </div>

      {/* Weight Sets Grid */}
      {weightSets && weightSets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {weightSets.map((weightSet: WeightSet) => (
            <WeightSetCard
              key={weightSet.id}
              weightSet={weightSet}
              onEdit={() => console.log('Edit weight set:', weightSet.id)}
              showActions={true}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardBody>
            <div className="text-center py-12">
              <div className="text-muted-foreground mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-foreground mb-2">No weight sets yet</h3>
              <p className="text-muted-foreground mb-4">
                Create your first weight set to start optimizing your gear choices
              </p>
              <Button
                onClick={() => setIsCreateModalOpen(true)}
                leftIcon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                }
              >
                Create Your First Weight Set
              </Button>
            </div>
          </CardBody>
        </Card>
      )}

      {/* TODO: Add Create/Edit Modal when needed */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardBody>
              <div className="text-center py-4">
                <p className="text-foreground mb-4">Create Weight Set Modal</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Weight set creation modal will be implemented when needed.
                </p>
                <Button onClick={() => setIsCreateModalOpen(false)}>
                  Close
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>
      )}
    </div>
  );
}; 

export default WeightSetList; 