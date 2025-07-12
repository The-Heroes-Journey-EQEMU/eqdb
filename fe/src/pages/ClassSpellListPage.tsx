import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const ClassSpellListPage: React.FC = () => {
  const { className } = useParams<{ className?: string }>();
  const [spellsByLevel, setSpellsByLevel] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [classes, setClasses] = useState<string[]>([]);

  const classIdMap: { [key: string]: number } = {
    "Bard": 8, "Beastlord": 15, "Berserker": 16, "Cleric": 2,
    "Druid": 6, "Enchanter": 14, "Magician": 13, "Monk": 7,
    "Necromancer": 11, "Paladin": 3, "Ranger": 4, "Rogue": 9,
    "Shadow Knight": 5, "Shaman": 10, "Warrior": 1, "Wizard": 12
  };

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
    const fetchSpells = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/v1/spells/list/${className}`);
        const { game_class, ...levels } = response.data;
        setSpellsByLevel(levels);
      } catch (error) {
        console.error('Error fetching spells:', error);
      } finally {
        setLoading(false);
      }
    };

    if (className) {
      fetchSpells();
    } else {
      setSpellsByLevel({});
      setLoading(false);
    }
  }, [className]);

  if (loading) {
    return <div>Loading...</div>;
  }

  const levels = Object.keys(spellsByLevel).map(Number).sort((a, b) => a - b);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-card border border-border rounded-lg p-6 mb-8">
        <div className="bg-background border border-border rounded-lg p-4">
          <div className="grid grid-cols-2 md:grid-cols-8 gap-4">
            {classes.map((cls) => {
              const isActive = className === cls.toLowerCase().replace(/ /g, '-');
              return (
                <Link
                  key={cls}
                  to={`/spells/list/${cls.toLowerCase().replace(/ /g, '-')}`}
                  className={`bg-card hover:bg-muted/50 text-foreground rounded-lg p-4 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 flex flex-col items-center justify-center h-[85px] ${isActive ? 'ring-2 ring-primary' : ''}`}
                >
                  <img src={`/class_icons/${classIdMap[cls]}.gif`} alt={cls} className="h-10 w-10 mb-1 object-contain" />
                  <span className="text-sm font-semibold text-center">{cls}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {className && (
        <>
          <div className="bg-card border border-border rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 text-center text-foreground">Levels</h2>
            <div className="flex flex-wrap justify-center gap-2">
              {levels.map(level => (
                <a key={level} href={`#level-${level}`} className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/80 transition-colors">
                  {level}
                </a>
              ))}
            </div>
          </div>

          {levels.map(level => (
            <div key={level} id={`level-${level}`} className="mb-8">
              <h2 className="text-3xl font-bold mb-4 text-foreground">Level {level}</h2>
              <div className="bg-card border border-border rounded-lg overflow-hidden">
                <table className="min-w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground">Icon</th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground">Name</th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground">Skill</th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground">Target</th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-muted-foreground">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {spellsByLevel[level].map((spell: any) => (
                      <tr key={spell.spell_id} className="hover:bg-muted/50">
                        <td className="py-3 px-4">
                          <div className="w-10 h-10">
                            <img
                              src={`/spell_icons/${spell.icon}.png`}
                              alt={spell.spell_name}
                              className="h-full w-full object-contain"
                            />
                          </div>
                        </td>
                        <td className="py-3 px-4 font-medium text-foreground">{spell.spell_name}</td>
                        <td className="py-3 px-4 text-muted-foreground">{spell.skill}</td>
                        <td className="py-3 px-4 text-muted-foreground">{spell.target}</td>
                        <td className="py-3 px-4 text-sm text-muted-foreground">
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
