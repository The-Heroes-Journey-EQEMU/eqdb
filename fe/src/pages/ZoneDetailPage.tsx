import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { zoneService, Zone, ConnectedZone } from '@/services/zoneService';
import Card from '@/components/common/Card';
import ZoneMap from '@/components/zones/ZoneMap';
import ZoneDetails from '@/components/zones/ZoneDetails';

const ConnectedZonesTab: React.FC<{ zones: ConnectedZone[] }> = ({ zones }) => (
  <div>
    <ul>
      {zones.map((cz, index) => (
        <li key={`${cz.target_zone_id}-${index}`}>
          <Link to={`/zones/detail/${cz.short_name}`} className="text-blue-400 hover:underline">
            {cz.long_name}
          </Link>
        </li>
      ))}
    </ul>
  </div>
);

export const ZoneDetailPage: React.FC = () => {
  const { identifier } = useParams<{ identifier: string }>();
  const [zone, setZone] = useState<Zone | null>(null);
  const [connectedZones, setConnectedZones] = useState<ConnectedZone[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('Connected Zones');

  useEffect(() => {
    const fetchZoneData = async () => {
      if (!identifier) return;
      try {
        setLoading(true);
        const zoneData = await zoneService.getZoneByIdentifier(identifier);
        setZone(zoneData);

        const detailsData = await zoneService.getZoneDetails(zoneData.short_name);
        const connectedData = await zoneService.getConnectedZones(detailsData.short_name);
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
              <ZoneDetails shortName={zone.short_name} />
            </div>
          </div>

          {/* Bottom Section: Tabs */}
          <div className="flex flex-col md:flex-row gap-4 mt-4">
            <div style={{ flex: '4 1 1000px' }}>
              <Card>
                <div className="p-4" style={{ minHeight: 300 }}>
                  {/* Tab Headers */}
                  <div className="flex border-b">
                    <button onClick={() => setActiveTab('Connected Zones')} className={`py-2 px-12 ${activeTab === 'Connected Zones' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>Connected Zones</button>
                    <button onClick={() => setActiveTab('Items')} className={`py-2 px-12 ${activeTab === 'Items' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>Items</button>
                    <button onClick={() => setActiveTab('NPCs')} className={`py-2 px-12 ${activeTab === 'NPCs' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>NPCs</button>
                    <button onClick={() => setActiveTab('Spawns')} className={`py-2 px-12 ${activeTab === 'Spawns' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>Spawns</button>
                  </div>
                  {/* Tab Content */}
                  <div className="pt-4 min-h-[12rem]">
                    {activeTab === 'Connected Zones' && <ConnectedZonesTab zones={connectedZones} />}
                    {activeTab === 'Items' && <p>Items Content</p>}
                    {activeTab === 'NPCs' && <p>NPCs Content</p>}
                    {activeTab === 'Spawns' && <p>Spawns Content</p>}
                  </div>
                </div>
              </Card>
            </div>
            <div style={{ flex: '3 1 0' }}>
              <Card>
                <div className="p-4" style={{ minHeight: 300 }}>
                  <h2 className="text-xl font-bold mb-2">Additional Info</h2>
                  {/* Add additional info here */}
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
