import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { zoneService, Zone, ConnectedZone, ZoneItem, ZoneDetails as ZoneDetailsType } from '@/services/zoneService';
import Card from '@/components/common/Card';
import ZoneMap from '@/components/zones/ZoneMap';
import ZoneDetails from '@/components/zones/ZoneDetails';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ItemCard from '@/components/items/ItemCard';
import ZoneSpawns from '@/components/ZoneSpawns';

const ItemsTab: React.FC<{ items: ZoneItem[]; loading: boolean; onLoad: () => void }> = ({ items, loading, onLoad }) => {
  useEffect(() => {
    if (items.length === 0 && !loading) {
      onLoad();
    }
  }, [items.length, loading, onLoad]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (items.length === 0) {
    return <div className="text-gray-500">No items found in this zone.</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-8 gap-4">
      {items.map((item) => (
        <ItemCard key={item.id} item={item} />
      ))}
    </div>
  );
};

export const ZoneDetailPage: React.FC = () => {
  const { shortName: identifier } = useParams<{ shortName: string }>();
  const [zone, setZone] = useState<Zone | null>(null);
  const [zoneDetails, setZoneDetails] = useState<ZoneDetailsType | null>(null);
  const [connectedZones, setConnectedZones] = useState<ConnectedZone[]>([]);
  const [zoneItems, setZoneItems] = useState<ZoneItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('Items');


  const fetchItems = async () => {
    if (!zone || zoneItems.length > 0 || itemsLoading) return;
    
    try {
      setItemsLoading(true);
      const items = await zoneService.getZoneItems(zone.short_name);
      setZoneItems(items);
    } catch (err) {
      console.error('Failed to fetch zone items:', err);
    } finally {
      setItemsLoading(false);
    }
  };

  useEffect(() => {
    const fetchZoneData = async () => {
      if (!identifier) return;
      try {
        setLoading(true);
        const zoneData = await zoneService.getZoneByIdentifier(identifier);
        setZone(zoneData);

        const [detailsData, connectedData] = await Promise.all([
          zoneService.getZoneDetails(zoneData.short_name),
          zoneService.getConnectedZones(zoneData.short_name)
        ]);
        setZoneDetails(detailsData);
        setConnectedZones(connectedData);

        setError(null);
      } catch (err) {
        setError('Failed to fetch zone data.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchZoneData();
  }, [identifier]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-center mb-4">{zone ? zone.long_name : 'Zone Details'}</h1>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {zone && (
        <div>
          <div className="flex flex-col md:flex-row gap-4">
            {/* Left Column: Map */}
            <div style={{ flex: '4 1 1000px' }}>
              <Card>
                <div className="p-0 bg-gray-200" style={{ minHeight: 500, position: 'relative', width: '100%', paddingBottom: '50%' }}>
                  <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
                    {zone.mapping && zone.mapping.length > 0 ? (
                      <ZoneMap zone={zone} />
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">No map data available for this zone.</p>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            </div>

            {/* Right Column: Zone Info */}
            <div style={{ flex: '3 1 0' }} className="p-0">
              {zoneDetails && <ZoneDetails shortName={zone.short_name} />}
            </div>
          </div>

          {/* Bottom Section: Tabs */}
          <div className="flex flex-col md:flex-row gap-4 mt-4">
            <div style={{ flex: '4 1 1000px' }}>
              <Card>
                <div className="p-4" style={{ minHeight: 300 }}>
                  {/* Tab Headers */}
                  <div className="flex border-b">
                    <button onClick={() => setActiveTab('Items')} className={`py-2 px-12 ${activeTab === 'Items' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>Items</button>
                    <button onClick={() => setActiveTab('Spawns')} className={`py-2 px-12 ${activeTab === 'Spawns' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>NPCs / Spawns</button>
                  </div>
                  {/* Tab Content */}
                  <div className="pt-4 min-h-[12rem]">
                    {activeTab === 'Items' && <ItemsTab items={zoneItems} loading={itemsLoading} onLoad={fetchItems} />}
                    {activeTab === 'Spawns' && <ZoneSpawns shortName={zone.short_name} />}
                  </div>
                </div>
              </Card>
            </div>
            <div style={{ flex: '3 1 0' }}>
              <Card>
                <div className="p-4" style={{ minHeight: 300 }}>
                  <h3 className="text-lg font-semibold mt-4 mb-2">Connected Zones</h3>
                  {connectedZones.length > 0 ? (
                    <ul>
                      {connectedZones.map((cz, index) => (
                        <li key={`${cz.target_zone_id}-${index}`}>
                          <Link to={`/zones/detail/${cz.short_name}`} className="text-blue-400 hover:underline">
                            {cz.long_name}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500">No connected zones found.</p>
                  )}
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
