import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { zoneService, ZoneSpawn } from '../services/zoneService';
import { Table, TableBody, TableCell, TableRow, TableHead, TableHeader } from '@/components/common/Table';
import { BiTargetLock, BiSolidZoomIn } from "react-icons/bi";

interface FormattedSpawn {
  npc_id: number;
  name: string;
  race: string;
  level: number;
  hp: number;
  spawntime: string;
  spawnchance: string;
  spawns: { id: number; x: number; y: number; z: number }[];
}

interface ZoneSpawnsProps {
  shortName: string;
}

const formatSpawnData = (spawns: ZoneSpawn[]): FormattedSpawn[] => {
  const groupedSpawns: { [key: string]: { npc_id: number; name: string; race: string; level: number; hp: number; spawntime: number; spawnchance: number; spawns: { id: number; x: number; y: number; z: number }[] } } = {};

  spawns.forEach(spawn => {
    spawn.npcs.forEach(npc => {
      const key = `${npc.npc_id}_${spawn.respawn}_${npc.chance}`;
      if (!groupedSpawns[key]) {
        groupedSpawns[key] = {
          npc_id: npc.npc_id,
          name: npc.npc_name,
          race: npc.npc_race,
          level: npc.npc_level,
          hp: npc.npc_hp,
          spawntime: spawn.respawn,
          spawnchance: npc.chance,
          spawns: [],
        };
      }
      groupedSpawns[key].spawns.push({ id: npc.spawn2_id, x: Math.round(spawn.x), y: Math.round(spawn.y), z: Math.round(spawn.z) });
    });
  });

  const formatted = Object.values(groupedSpawns)
    .map(data => {
      return {
        npc_id: data.npc_id,
        name: data.name.replace(/_/g, ' '),
        race: data.race,
        level: data.level,
        hp: data.hp,
        spawntime: `${Math.round(data.spawntime / 60)} minutes`,
        spawnchance: `${data.spawnchance}%`,
        spawns: data.spawns,
      };
    })
    .filter(spawn => spawn.name !== 'Echo of the Past' && !spawn.name.startsWith('#'));

  return formatted.sort((a, b) => b.level - a.level);
};

const ZoneSpawns: React.FC<ZoneSpawnsProps> = ({ shortName }) => {
  const [formattedSpawns, setFormattedSpawns] = useState<FormattedSpawn[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSpawns = async () => {
      try {
        setLoading(true);
        const spawnData = await zoneService.getZoneSpawns(shortName);
        setFormattedSpawns(formatSpawnData(spawnData));
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
      <Table>
        <TableHead>
          <TableRow>
            <TableHeader className="w-1/12">Menu</TableHeader>
            <TableHeader className="w-1/6">NPC Name</TableHeader>
            <TableHeader  className="w-1/8">Race</TableHeader>
            <TableHeader>Level</TableHeader>
            <TableHeader>HP</TableHeader>
            <TableHeader>Respawn Time</TableHeader>
            <TableHeader>Spawn Chance</TableHeader>
            <TableHeader>Locations</TableHeader>
          </TableRow>
        </TableHead>
        <TableBody>
          {formattedSpawns.map((spawn, index) => (
            <TableRow key={index}>
              <TableCell>
                <div className="flex space-x-2">
                  <a href="#" onClick={() => alert(`Targeting ${spawn.name}`)} className="text-blue-100 hover:underline">
                    <BiTargetLock className="text-lg" />
                  </a>
                  <Link to={`/npc/${spawn.npc_id}`} className="text-blue-100 hover:underline">
                    <BiSolidZoomIn className="text-lg" />
                  </Link>
                </div>
              </TableCell>
              <TableCell>
                <Link to={`/npc/${spawn.npc_id}`} className="text-blue-100 hover:underline">
                  {spawn.name}
                </Link>
              </TableCell>
              <TableCell>{spawn.race}</TableCell>
              <TableCell>{spawn.level}</TableCell>
              <TableCell>{spawn.hp}</TableCell>
              <TableCell>{spawn.spawntime}</TableCell>
              <TableCell>{spawn.spawnchance}</TableCell>
              <TableCell>
                {spawn.spawns.map((s, i) => (
                  <Link key={i} to={`/zones/detail/${shortName}/spawn/${s.id}`} className="text-blue-100 hover:underline">
                    ({s.x}, {s.y}, {s.z})
                  </Link>
                )).reduce((prev, curr) => <>{prev}, {curr}</>)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default ZoneSpawns;
