import React, { useState, useEffect } from 'react';
import { useItems, useItemTypes, useItemSlots } from '../hooks/useApi';
import { useAuth } from '../contexts/AuthContext';
import Card, { CardHeader, CardBody } from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Checkbox from '../components/common/Checkbox';
import Select from '../components/common/Select';
import ItemSearchTable from '../components/items/ItemSearchTable';
import { WeightSetSelector } from '../components/weightsets';
import { WeightSet } from '../types/user';
import CalculatedWeights from '../components/weightsets/CalculatedWeights';
import { ClassFilter } from '../components/characters';

interface ItemSearchPageProps {
  searchType?: 'item' | 'weapon' | 'armor';
}

const ItemSearchPage: React.FC<ItemSearchPageProps> = ({ searchType = 'item' }) => {
  const { data: itemTypes } = useItemTypes();
  const { data: itemSlots } = useItemSlots();
  const { isAuthenticated } = useAuth();

  const [searchParams, setSearchParams] = useState({
    name: '',
    tradeskill_only: false,
    equippable_only: false,
    exclude_glamours: false,
    only_augments: false,
    item_type: '',
    item_slot: '',
    id: undefined as number | undefined,
    stat_weights: undefined as Array<{ stat: string; value: number }> | undefined,
    show_weight_detail: false,
  });

  const [debouncedSearchParams, setDebouncedSearchParams] = useState(searchParams);

  const [selectedWeightSets, setSelectedWeightSets] = useState<WeightSet[]>([]);
  const [selectedClasses, setSelectedClasses] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<'filters' | 'weights'>('filters');

  // Only search if we have actual search parameters
  const hasSearchParams = Object.values(debouncedSearchParams).some(value => 
    value !== '' && value !== false && value !== undefined && value !== null
  );

  const { data: items, isLoading, error } = useItems(debouncedSearchParams, {
    enabled: hasSearchParams
  });

  // Debounce search parameters
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchParams(searchParams);
    }, 250);

    return () => clearTimeout(timer);
  }, [searchParams]);

  // Debug logging
  useEffect(() => {
    console.log('Search params:', searchParams);
    console.log('Debounced params:', debouncedSearchParams);
    console.log('Has search params:', hasSearchParams);
    console.log('Items:', items);
    console.log('Loading:', isLoading);
    console.log('Error:', error);
  }, [searchParams, debouncedSearchParams, hasSearchParams, items, isLoading, error]);

  useEffect(() => {
    setSearchParams(prev => ({ ...prev, item_type: searchType === 'item' ? '' : searchType }));
  }, [searchType]);

  // Switch to filters tab if user logs out while on weights tab
  useEffect(() => {
    if (!isAuthenticated && activeTab === 'weights') {
      setActiveTab('filters');
    }
  }, [isAuthenticated, activeTab]);



  const handleInputChange = (field: string, value: string | number | boolean | undefined) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleApplyWeights = (weights: Array<{ stat: string; value: number }>) => {
    setSearchParams(prev => ({
      ...prev,
      stat_weights: weights,
      show_weight_detail: true,
    }));
  };

  const handleClearWeights = () => {
    setSearchParams(prev => ({
      ...prev,
      stat_weights: undefined,
      show_weight_detail: false,
    }));
    setSelectedWeightSets([]);
  };

  const handleWeightSetSelectionChange = (newSelectedWeightSets: WeightSet[]) => {
    setSelectedWeightSets(newSelectedWeightSets);
  };

  const handleClassesChange = (classes: string[]) => {
    setSelectedClasses(classes);
    // TODO: Apply class filters to search params
    // This would modify searchParams based on the selected classes
  };

  const handleClearSearch = () => {
    setSearchParams({
      name: '',
      tradeskill_only: false,
      equippable_only: false,
      exclude_glamours: false,
      only_augments: false,
      item_type: '',
      item_slot: '',
      id: undefined,
      stat_weights: undefined,
      show_weight_detail: false,
    });
    setSelectedWeightSets([]);
    setSelectedClasses([]);
  };

  const renderItemTypeOptions = () => {
    if (!itemTypes) return null;

    if (searchType === 'item') {
      return itemTypes.items_tab?.map((type) => (
        <option key={type} value={type}>{type}</option>
      )) || null;
    }

    if (searchType === 'weapon' && itemTypes.weapons_tab) {
      return (
        <>
          <optgroup label="Weapons">
            {itemTypes.weapons_tab.Weapons && Object.entries(itemTypes.weapons_tab.Weapons).map(([name, id]) => (
              <option key={String(id)} value={String(id)}>{name}</option>
            ))}
          </optgroup>
          <optgroup label="Held Items">
            {itemTypes.weapons_tab['Held Items'] && Object.entries(itemTypes.weapons_tab['Held Items']).map(([name, id]) => (
              <option key={String(id)} value={String(id)}>{name}</option>
            ))}
          </optgroup>
        </>
      );
    }

    if (searchType === 'armor' && itemTypes.armor_tab) {
      return (
        <optgroup label="Armor">
          {itemTypes.armor_tab.Armor && Object.entries(itemTypes.armor_tab.Armor).map(([name, id]) => (
            <option key={String(id)} value={String(id)}>{name}</option>
          ))}
        </optgroup>
      );
    }

    return null;
  };

  const renderItemSlotOptions = () => {
    if (!itemSlots) return null;
    return (
      <>
        <optgroup label="General">
          {itemSlots.General && Object.entries(itemSlots.General).map(([name, id]) => (
            <option key={String(id)} value={String(id)}>{name}</option>
          ))}
        </optgroup>
        <optgroup label="Armor">
          {itemSlots.Armor && Object.entries(itemSlots.Armor).map(([name, id]) => (
            <option key={String(id)} value={String(id)}>{name}</option>
          ))}
        </optgroup>
      </>
    );
  };

  return (
    <div>
      {/* Main Layout with Left Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-8 gap-6">
        {/* Left Sidebar - Calculated Weights (always visible when authenticated) */}
        <div className="lg:col-span-1">
          {isAuthenticated && (
            <div className="space-y-4">
              <CalculatedWeights 
                selectedWeightSets={selectedWeightSets}
                compact={true}
              />
              
              {/* Class filter only on search filters tab */}
              {activeTab === 'filters' && (
                <ClassFilter
                  selectedClasses={selectedClasses}
                  onClassesChange={handleClassesChange}
                  compact={true}
                />
              )}
            </div>
          )}
        </div>

        {/* Main Content Area */}
        <div className={`${isAuthenticated ? 'lg:col-span-7' : 'lg:col-span-8'}`}>
          {/* Tabbed Interface */}
          <Card>
            <CardHeader>
              <div className="flex border-b border-border">
                <button
                  type="button"
                  className={`px-4 py-2 -mb-px text-sm font-medium ${
                    activeTab === 'filters'
                      ? 'border-b-2 border-primary text-primary'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                  onClick={() => setActiveTab('filters')}
                >
                  Search Filters
                </button>
                {isAuthenticated && (
                  <button
                    type="button"
                    className={`px-4 py-2 -mb-px text-sm font-medium ${
                      activeTab === 'weights'
                        ? 'border-b-2 border-primary text-primary'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                    onClick={() => setActiveTab('weights')}
                  >
                    Weight Sets
                  </button>
                )}
              </div>
            </CardHeader>
            <CardBody>
              {/* Search Filters Tab */}
              {activeTab === 'filters' && (
                <div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Row 1: Name */}
                  <div className="md:col-span-2 lg:col-span-3">
                    <Input
                      label="Item Name (partial allowed)"
                      placeholder="Search by item name..."
                      value={searchParams.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                    />
                  </div>

                  {/* Row 2: Checkboxes */}
                  <div className="md:col-span-2 lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4 items-center">
                    <Checkbox
                      label="Tradeskill Only"
                      checked={searchParams.tradeskill_only}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('tradeskill_only', e.target.checked)}
                    />
                    <Checkbox
                      label="Equippable Items Only"
                      checked={searchParams.equippable_only}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('equippable_only', e.target.checked)}
                    />
                    <Checkbox
                      label="Exclude Glamours"
                      checked={searchParams.exclude_glamours}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('exclude_glamours', e.target.checked)}
                    />
                    <Checkbox
                      label="Only Augments"
                      checked={searchParams.only_augments}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('only_augments', e.target.checked)}
                    />
                  </div>

                  {/* Row 3: Type and Slot */}
                  <div className="md:col-span-2 lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Select
                      label="Item Type"
                      value={searchParams.item_type}
                      onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleInputChange('item_type', e.target.value)}
                      disabled={searchType === 'weapon' || searchType === 'armor'}
                    >
                      <option value="">All Types</option>
                      {renderItemTypeOptions()}
                    </Select>
                    <Select
                      label="Item Slot"
                      value={searchParams.item_slot}
                      onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleInputChange('item_slot', e.target.value)}
                    >
                      <option value="">All Slots</option>
                      {renderItemSlotOptions()}
                    </Select>
                  </div>
                </div>

                <div className="flex items-center space-x-4 mt-6">
                  <Button variant="outline" onClick={handleClearSearch}>
                    Clear
                  </Button>
                </div>
              </div>
              )}

              {/* Weight Sets Tab */}
              {activeTab === 'weights' && isAuthenticated && (
                <div className="py-4">
                  <WeightSetSelector
                    onApplyWeights={handleApplyWeights}
                    onClearWeights={handleClearWeights}
                    selectedWeightSets={selectedWeightSets}
                    onSelectionChange={handleWeightSetSelectionChange}
                    disabled={isLoading}
                    showPreview={false}
                    layout="grid"
                    multiSelect={true}
                  />
                </div>
              )}

              {/* Show message for non-authenticated users on weights tab */}
              {activeTab === 'weights' && !isAuthenticated && (
                <div className="text-center py-8">
                  <div className="text-muted-foreground mb-4">
                    <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-foreground mb-2">Authentication Required</h3>
                  <p className="text-muted-foreground">
                    Please log in to access weight sets functionality
                  </p>
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-4 mt-8">
        <ItemSearchTable 
          items={items || null} 
          isLoading={isLoading} 
          error={error}
        />
      </div>
    </div>
  );
};

export default ItemSearchPage;
