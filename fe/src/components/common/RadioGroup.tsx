import React from 'react';

interface RadioGroupProps {
  label: string;
  options: string[];
  value: string;
  onChange: (value: string) => void;
}

const RadioGroup: React.FC<RadioGroupProps> = ({ label, options, value, onChange }) => {
  return (
    <div>
      <label className="block text-sm font-medium text-foreground mb-1">{label}</label>
      <div className="flex items-center space-x-4">
        {options.map((option) => (
          <label key={option} className="flex items-center space-x-2 cursor-pointer">
            <input
              type="radio"
              name={label}
              value={option}
              checked={value === option}
              onChange={(e) => onChange(e.target.value)}
              className="form-radio h-4 w-4 text-primary border-gray-300 focus:ring-primary rounded-[24px] p-[8px]"
            />
            <span className="text-sm text-foreground">{option}</span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default RadioGroup;
