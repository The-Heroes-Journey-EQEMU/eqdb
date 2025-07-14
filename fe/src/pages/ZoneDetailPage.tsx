import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { zoneService, Zone, ConnectedZone, ZoneNPC, ZoneItem, ZoneDetails as ZoneDetailsType } from '@/services/zoneService';
import Card from '@/components/common/Card';
import ZoneMap from '@/components/zones/ZoneMap';
import ZoneDetails from '@/components/zones/ZoneDetails';
import { Table, TableBody, TableCell, TableRow, TableHead, TableHeader } from '@/components/common/Table';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ItemCard from '@/components/items/ItemCard';
import ZoneSpawns from '@/components/ZoneSpawns';

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

const NPCsTab: React.FC<{ npcs: ZoneNPC[]; loading: boolean; onLoad: () => void }> = ({ npcs, loading, onLoad }) => {
  const [filter, setFilter] = useState('');

  useEffect(() => {
    if (npcs.length === 0 && !loading) {
      onLoad();
    }
  }, [npcs.length, loading, onLoad]);

  const filteredNpcs = npcs.filter(npc =>
    npc.name.toLowerCase().includes(filter.toLowerCase())
  );

  if (loading) {
    return <LoadingSpinner />;
  }

  if (npcs.length === 0) {
    return <div className="text-gray-500">No NPCs found in this zone.</div>;
  }

  return (
    <div>
      <div className="mb-4">
        <input
          type="text"
          placeholder="Filter by NPC name..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <Table>
        <TableHead>
          <TableRow>
            <TableHeader>Name</TableHeader>
            <TableHeader>Level</TableHeader>
            <TableHeader>HP</TableHeader>
            <TableHeader>Race</TableHeader>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredNpcs.map((npc) => (
          <TableRow key={npc.id}>
            <TableCell className="font-medium text-blue-400">{npc.name.replace(/_/g, ' ')}</TableCell>
            <TableCell>{npc.level}</TableCell>
            <TableCell>{npc.hp ? npc.hp.toLocaleString() : 'N/A'}</TableCell>
            <TableCell>{npc.race}</TableCell>
          </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

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
  const [zoneNPCs, setZoneNPCs] = useState<ZoneNPC[]>([]);
  const [zoneItems, setZoneItems] = useState<ZoneItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [npcsLoading, setNpcsLoading] = useState(false);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('Connected Zones');

  const fetchNPCs = async () => {
    if (!zone || zoneNPCs.length > 0 || npcsLoading) return;
    
    try {
      setNpcsLoading(true);
      const npcs = await zoneService.getZoneNPCs(zone.short_name);
      setZoneNPCs(npcs);
    } catch (err) {
      console.error('Failed to fetch zone NPCs:', err);
    } finally {
      setNpcsLoading(false);
    }
  };

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
                    <button onClick={() => setActiveTab('Connected Zones')} className={`py-2 px-12 ${activeTab === 'Connected Zones' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>Connected Zones</button>
                    <button onClick={() => setActiveTab('Items')} className={`py-2 px-12 ${activeTab === 'Items' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>Items</button>
                    <button onClick={() => setActiveTab('NPCs')} className={`py-2 px-12 ${activeTab === 'NPCs' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>NPCs</button>
                    <button onClick={() => setActiveTab('Spawns')} className={`py-2 px-12 ${activeTab === 'Spawns' ? 'text-blue-200 border-b-2 border-blue-200' : 'text-gray-200'}`}>Spawns</button>
                  </div>
                  {/* Tab Content */}
                  <div className="pt-4 min-h-[12rem]">
                    {activeTab === 'Connected Zones' && <ConnectedZonesTab zones={connectedZones} />}
                    {activeTab === 'Items' && <ItemsTab items={zoneItems} loading={itemsLoading} onLoad={fetchItems} />}
                    {activeTab === 'NPCs' && <NPCsTab npcs={zoneNPCs} loading={npcsLoading} onLoad={fetchNPCs} />}
                    {activeTab === 'Spawns' && <ZoneSpawns shortName={zone.short_name} />}
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
