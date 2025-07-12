import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const SpellListPage: React.FC = () => {
  const [classes, setClasses] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClasses = async () => {
      try {
        const response = await axios.get('/api/v1/spells/classes');
        setClasses(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching spell classes:', error);
        setLoading(false);
      }
    };

    fetchClasses();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  const classIdMap: { [key: string]: number } = {
    "Bard": 8, "Beastlord": 15, "Berserker": 16, "Cleric": 2,
    "Druid": 6, "Enchanter": 14, "Magician": 13, "Monk": 7,
    "Necromancer": 11, "Paladin": 3, "Ranger": 4, "Rogue": 9,
    "Shadow Knight": 5, "Shaman": 10, "Warrior": 1, "Wizard": 12
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4 text-center">Spell List by Class</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto">
        {classes.map(className => (
          <Link
            key={className}
            to={`/spells/list/${className.toLowerCase().replace(' ', '-')}`}
            className="p-4 bg-gray-800 text-white rounded-lg text-center hover:bg-gray-700 flex flex-col items-center"
          >
            <img src={`/class_icons/${classIdMap[className]}.gif`} alt={className} className="h-16 w-16 mb-2" />
            <span className="text-lg font-semibold">{className}</span>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default SpellListPage;
