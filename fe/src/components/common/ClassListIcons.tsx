import React from 'react';
import Card from '@/components/common/Card';

interface ClassListIconsProps {
  classes: string[];
  selectedClasses: string[];
  onClassClick: (className: string) => void;
  classIdMap: { [key: string]: number };
}

const ClassListIcons: React.FC<ClassListIconsProps> = ({
  classes,
  selectedClasses,
  onClassClick,
  classIdMap,
}) => {
  return (
    <Card className="bg-card border border-border p-6 mb-8">
      <div className="bg-background border border-border p-4">
        <div className="grid grid-cols-2 md:grid-cols-8 gap-4">
          {classes.map((cls) => {
            const formattedCls = cls.toLowerCase().replace(/ /g, '-');
            const isActive = selectedClasses.includes(formattedCls);
            return (
              <div
                key={cls}
                onClick={() => onClassClick(cls)}
                className={`cursor-pointer bg-card hover:bg-muted/50 text-foreground rounded-lg p-4 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 flex flex-col items-center justify-center h-[85px] ${
                  isActive ? 'ring-2 ring-primary' : ''
                }`}
              >
                <img
                  src={`/class_icons/${classIdMap[cls]}.gif`}
                  alt={cls}
                  className="h-10 w-10 mb-1 object-contain"
                />
                <span className="text-sm font-semibold text-center">{cls}</span>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};

export default ClassListIcons;
