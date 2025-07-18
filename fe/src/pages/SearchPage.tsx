import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import ItemSearchPage from './ItemSearchPage';

type Tab = 'Items' | 'Weapons' | 'Armor';

const SearchPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState<Tab>('Items');

  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab && ['Items', 'Weapons', 'Armor'].includes(tab)) {
      setActiveTab(tab as Tab);
    }
  }, [searchParams]);

  const renderContent = () => {
    switch (activeTab) {
      case 'Items':
        return <ItemSearchPage searchType="item" />;
      case 'Weapons':
        return <ItemSearchPage searchType="weapon" />;
      case 'Armor':
        return <ItemSearchPage searchType="armor" />;
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Search</h1>
        <p className="text-muted-foreground">Search for items, weapons, and armor.</p>
      </div>
      <div className="flex border-b border-border">
        {(['Items', 'Weapons', 'Armor'] as Tab[]).map((tab) => (
          <button
            key={tab}
            className={`px-4 py-2 -mb-px text-sm font-medium ${
              activeTab === tab
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>
      <div className="pt-8">{renderContent()}</div>
    </div>
  );
};

export default SearchPage;
