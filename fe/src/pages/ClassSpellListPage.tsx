import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ClassListIcons from '@/components/common/ClassListIcons';
import Card from '@/components/common/Card';

const ClassSpellListPage: React.FC = () => {
  const navigate = useNavigate();
  const { classNames: classNamesParam } = useParams<{ classNames?: string }>();
  const [spellsByLevel, setSpellsByLevel] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [classes, setClasses] = useState<string[]>([]);
  const [selectedClasses, setSelectedClasses] = useState<string[]>([]);

  const classIdMap: { [key: string]: number } = {
    "Bard": 8, "Beastlord": 15, "Berserker": 16, "Cleric": 2,
    "Druid": 6, "Enchanter": 14, "Magician": 13, "Monk": 7,
    "Necromancer": 11, "Paladin": 3, "Ranger": 4, "Rogue": 9,
    "Shadow Knight": 5, "Shaman": 10, "Warrior": 1, "Wizard": 12
  };

  useEffect(() => {
    if (classNamesParam) {
      setSelectedClasses(classNamesParam.split(','));
    } else {
      setSelectedClasses([]);
    }
  }, [classNamesParam]);

  const fetchSpells = useCallback(async () => {
    if (selectedClasses.length === 0) {
      setSpellsByLevel({});
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`/api/v1/spells/list/${selectedClasses.join(',')}`);
      const { ...levels } = response.data;
      
      // Aggregate spells by level
      const aggregatedSpells: any = {};
      Object.entries(levels).forEach(([className, classSpells]: [string, any]) => {
        Object.entries(classSpells).forEach(([level, spells]: [string, any]) => {
          if (isNaN(parseInt(level, 10))) {
            return;
          }
          if (!aggregatedSpells[level]) {
            aggregatedSpells[level] = [];
          }
          if (Array.isArray(spells)) {
            const spellsWithClass = spells.map(spell => ({ 
              ...spell, 
              className: className.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            }));
            aggregatedSpells[level].push(...spellsWithClass);
          }
        });
      });

      // Remove duplicates and sort
      Object.keys(aggregatedSpells).forEach(level => {
        const uniqueSpells = Array.from(new Map(aggregatedSpells[level].map((spell: any) => [spell.spell_id, spell])).values());
        aggregatedSpells[level] = uniqueSpells.sort((a: any, b: any) => a.spell_name.localeCompare(b.spell_name));
      });

      setSpellsByLevel(aggregatedSpells);
    } catch (error) {
      console.error('Error fetching spells:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedClasses]);


  useEffect(() => {
    const fetchClasses = async () => {
      try {
        const response = await axios.get('/api/v1/spells/classes');
        setClasses(response.data);
      } catch (error) {
        console.error('Error fetching classes:', error);
      }
    };

    fetchClasses();
  }, []);

  useEffect(() => {
    fetchSpells();
  }, [fetchSpells]);

  const handleClassClick = (cls: string) => {
    const formattedCls = cls.toLowerCase().replace(/ /g, '-');
    const newSelectedClasses = selectedClasses.includes(formattedCls)
      ? selectedClasses.filter(c => c !== formattedCls)
      : [...selectedClasses, formattedCls];

    if (newSelectedClasses.length > 3) {
      // Optional: show some feedback to the user
      return;
    }
    
    navigate(`/spells/list/${newSelectedClasses.join(',')}`);
  };

  const levels = Object.keys(spellsByLevel).map(Number).sort((a, b) => a - b);

  return (
    <div className="container mx-auto px-4 py-8">
      <ClassListIcons
        classes={classes}
        selectedClasses={selectedClasses}
        onClassClick={handleClassClick}
        classIdMap={classIdMap}
      />
      {loading ? (
        <div className="container mx-auto px-4 py-8 text-grey-100" style={{ minHeight: '400px' }}>Loading please wait...</div>
      ) : selectedClasses.length === 0 ? (
        <div className="container mx-auto px-4 py-8 text-grey-100" style={{ minHeight: '400px' }}>Select up to three classes.</div>
      ) : (
        <>
          <Card className="p-6 mb-8">
            <div className="flex flex-wrap justify-left gap-1">
              {levels.map(level => (
                <a key={level} href={`#level-${level}`}  style={{ width: '40px' }} className="text-center py-2 text-s bg-muted text-muted-foreground rounded-md hover:bg-muted/80 transition-colors">
                  {level}
                </a>
              ))}
            </div>
          </Card>

          {levels.map(level => (
            <div key={level} id={`level-${level}`} className="mb-8">
              <h2 className="text-3xl font-bold mb-4 text-foreground">Level {level}</h2>
              <div className="bg-card border border-border rounded-lg overflow-hidden">
                <table className="min-w-full table-fixed">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground" style={{ width: '64px' }}>Icon</th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground" style={{ width: '150px' }}>Class</th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground" style={{ width: '280px' }}>Name</th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground" style={{ width: '192px' }}>Skill</th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground" style={{ width: '192px' }}>Target</th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {spellsByLevel[level].map((spell: any, index: number) => (
                      <tr
                        key={spell.spell_id}
                        className={`cursor-pointer transition-colors duration-200 hover:bg-muted ${
                          index % 2 === 0 ? 'bg-background' : 'bg-muted/20'
                        }`}
                        onClick={() => navigate(`/spell/detail/${spell.spell_id}`)}
                      >
                        <td className="py-3 px-4">
                          <div className="w-10 h-10">
                            <img
                              src={`/spell_icons/${spell.icon}.png`}
                              alt={spell.spell_name}
                              className="h-full w-full object-contain"
                            />
                          </div>
                        </td>
                        <td className="py-3 px-4 text-muted-foreground break-words">{spell.className}</td>
                        <td className="py-3 px-4 font-medium text-foreground break-words">{spell.spell_name}</td>
                        <td className="py-3 px-4 text-muted-foreground break-words">{spell.skill}</td>
                        <td className="py-3 px-4 text-muted-foreground break-words">{spell.target}</td>
                        <td className="py-3 px-4 text-sm text-muted-foreground break-words">
                          {Object.values(spell.slots).map((slot: any, index: number) => (
                            <div key={index} dangerouslySetInnerHTML={{ __html: slot.desc }} />
                          ))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
};

export default ClassSpellListPage;