import React, { useState, useRef, useEffect } from 'react';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';

interface Character {
  id: number;
  name: string;
  classes: string[];
  level: number;
}

interface ClassFilterProps {
  selectedClasses?: string[];
  onClassesChange?: (classes: string[]) => void;
  className?: string;
  compact?: boolean;
  disabled?: boolean;
}

export const ClassFilter: React.FC<ClassFilterProps> = ({
  selectedClasses = [],
  onClassesChange,
  className = '',
  compact = false,
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [charactersExpanded, setCharactersExpanded] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const comboboxRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // TODO: Replace with actual character data from API/hooks
  const characters: Character[] = [
    { id: 1, name: 'Thorgar', classes: ['Warrior', 'Beastlord', 'Ranger'], level: 65 },
    { id: 2, name: 'Mystral', classes: ['Wizard', 'Enchanter'], level: 60 },
    { id: 3, name: 'Healeris', classes: ['Cleric', 'Druid', 'Shaman'], level: 58 },
  ];

  const allClasses = [
    'Bard', 'Beastlord', 'Berserker', 'Cleric', 'Druid', 'Enchanter',
    'Magician', 'Monk', 'Necromancer', 'Paladin', 'Ranger', 'Rogue',
    'Shadow Knight', 'Shaman', 'Warrior', 'Wizard'
  ];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (comboboxRef.current && !comboboxRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleClassToggle = (className: string) => {
    const newClasses = selectedClasses.includes(className)
      ? selectedClasses.filter(c => c !== className)
      : [...selectedClasses, className];
    
    if (onClassesChange) {
      onClassesChange(newClasses);
    }
  };

  const handleCharacterSelect = (character: Character) => {
    // When a character is selected, turn on all their classes and close the selector
    const newClasses = [...new Set([...selectedClasses, ...character.classes])];
    if (onClassesChange) {
      onClassesChange(newClasses);
    }
    // Close the combobox after character selection
    setIsOpen(false);
    // Minimize characters list
    setCharactersExpanded(false);
  };

  const handleClearClasses = () => {
    if (onClassesChange) {
      onClassesChange([]);
    }
  };

  const filteredClasses = allClasses.filter(cls =>
    cls.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredCharacters = characters.filter(char =>
    char.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    char.classes.some(cls => cls.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getDisplayText = () => {
    if (selectedClasses.length === 0) {
      return 'Select classes...';
    } else if (selectedClasses.length === 1) {
      return selectedClasses[0];
    } else {
      return `${selectedClasses.length} classes selected`;
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className={compact ? "text-sm" : "text-base"}>
          Class Filter
        </CardTitle>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          {/* Combobox */}
          <div>
            
            <div className="relative" ref={comboboxRef}>
              {/* Combobox Trigger */}
              <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                disabled={disabled}
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-left focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent flex justify-between items-center"
              >
                <span className="truncate text-sm">
                  {getDisplayText()}
                </span>
                <svg 
                  className={`w-4 h-4 transition-transform text-muted-foreground ${isOpen ? 'rotate-180' : ''}`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Combobox Content */}
              {isOpen && (
                <div className="absolute z-50 w-full mt-1 bg-background border border-border rounded-md shadow-lg max-h-80 overflow-hidden">
                  {/* Search Input */}
                  <div className="p-3 border-b border-border">
                    <input
                      ref={inputRef}
                      type="text"
                      placeholder="Search classes or characters..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-border rounded bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                  </div>

                  <div className="max-h-60 overflow-y-auto">
                    {/* Characters Section */}
                    <div className="border-b border-border">
                      <button
                        type="button"
                        onClick={() => setCharactersExpanded(!charactersExpanded)}
                        className="w-full px-3 py-2 flex items-center justify-between hover:bg-muted text-left"
                      >
                        <span className="font-medium text-foreground text-sm">Characters</span>
                        <svg 
                          className={`w-4 h-4 transition-transform text-muted-foreground ${charactersExpanded ? 'rotate-90' : ''}`} 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>

                      {charactersExpanded && (
                        <div className="bg-muted/30">
                          {filteredCharacters.map((character) => (
                            <button
                              key={character.id}
                              type="button"
                              onClick={() => handleCharacterSelect(character)}
                              className="w-full px-6 py-2 text-left hover:bg-muted/50 flex justify-between items-center"
                            >
                              <div>
                                <div className="text-sm font-medium text-foreground">
                                  {character.name} ({character.level})
                                </div>
                                <div className="text-xs text-muted-foreground">
                                  {character.classes.join(', ')}
                                </div>
                              </div>
                              <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                              </svg>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Classes Section */}
                    <div>
                      <div className="px-3 py-2 bg-muted/20">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-foreground text-sm">Classes</span>
                          {selectedClasses.length > 0 && (
                            <button
                              type="button"
                              onClick={handleClearClasses}
                              className="text-xs text-muted-foreground hover:text-foreground"
                            >
                              Clear all
                            </button>
                          )}
                        </div>
                      </div>
                      
                      <div className="max-h-40 overflow-y-auto">
                        {filteredClasses.map((cls) => {
                          const isSelected = selectedClasses.includes(cls);
                          return (
                            <label
                              key={cls}
                              className={`flex items-center px-3 py-2 cursor-pointer ${
                                isSelected 
                                  ? 'bg-white hover:bg-white/90' 
                                  : 'hover:bg-muted'
                              }`}
                            >
                              <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={() => handleClassToggle(cls)}
                                className="mr-3 w-4 h-4 text-primary bg-background border-border rounded focus:ring-primary focus:ring-2"
                              />
                              <span className={`text-foreground ${compact ? 'text-xs' : 'text-sm'}`}>
                                {cls}
                              </span>
                            </label>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Selected Classes Display */}
          {selectedClasses.length > 0 && (
            <div className={`p-3 bg-muted rounded-lg ${compact ? 'text-xs' : 'text-sm'}`}>
              <div className="flex flex-wrap gap-1 items-center">
                {selectedClasses.map((cls) => (
                  <span
                    key={cls}
                    className="inline-flex items-center px-2 py-1 rounded text-xs bg-white text-gray-900 border border-border shadow-sm"
                  >
                    {cls}
                    <button
                      type="button"
                      onClick={() => handleClassToggle(cls)}
                      className="ml-1 text-gray-500 hover:text-gray-700"
                    >
                      ×
                    </button>
                  </span>
                ))}
                <button
                  type="button"
                  onClick={handleClearClasses}
                  className="text-xs text-muted-foreground hover:text-foreground ml-auto"
                >
                  Clear
                </button>
              </div>
              {!compact && (
                <div className="mt-2 pt-2 border-t border-border">
                  <p className="text-xs text-muted-foreground">
                    Items will be filtered to show only those usable by the selected classes.
                  </p>
                </div>
              )}
            </div>
          )}



          {/* Help Text */}
          {!compact && (
            <div className="mt-4 p-3 bg-muted rounded-lg">
              <div className="text-sm text-muted-foreground">
                <div className="font-medium mb-1 text-foreground">Class Filtering</div>
                <div className="text-xs">
                  Select individual classes or choose a character to automatically select all their classes. 
                  Items will be filtered to show only those usable by the selected classes.
                </div>
              </div>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
};

// Keep backwards compatibility
export const CharacterSelector = ClassFilter;
export default ClassFilter; 