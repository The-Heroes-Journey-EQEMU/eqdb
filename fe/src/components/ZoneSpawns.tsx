import React, { useEffect, useState } from 'react';
import { zoneService, ZoneSpawn } from '../services/zoneService';

interface ZoneSpawnsProps {
  shortName: string;
}

const ZoneSpawns: React.FC<ZoneSpawnsProps> = ({ shortName }) => {
  const [spawns, setSpawns] = useState<ZoneSpawn[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSpawns = async () => {
      try {
        setLoading(true);
        const spawnData = await zoneService.getZoneSpawns(shortName);
        setSpawns(spawnData);
      } catch (err) {
        setError('Failed to fetch spawn data.');
      } finally {
        setLoading(false);
      }
    };
    fetchSpawns();
  }, [shortName]);

  if (loading) {
    return <div>Loading spawns...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div className="mt-8">
      <h2 className="text-xl font-semibold mb-4">Spawns</h2>
      {spawns.map((spawn, index) => (
        <div key={index} className="mb-4 p-4 border rounded">
          <h3 className="font-bold">{spawn.spawngroup_name}</h3>
          <p>Location: ({spawn.x}, {spawn.y}, {spawn.z})</p>
          <p>Respawn Time: {spawn.respawn} seconds</p>
          <ul className="list-disc ml-5">
            {spawn.npcs.map((npc, npcIndex) => (
              <li key={npcIndex}>
                {npc.npc_name} ({npc.chance}% chance)
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default ZoneSpawns;
