import React from 'react';

interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

const Checkbox: React.FC<CheckboxProps> = ({ label, ...props }) => {
  return (
    <label className="flex items-center space-x-2 cursor-pointer">
      <input
        type="checkbox"
        className="form-checkbox h-5 w-5 text-primary rounded-[24px] border-gray-300 focus:ring-primary p-[8px]"
        {...props}
      />
      <span className="text-sm text-foreground">{label}</span>
    </label>
  );
};

export default Checkbox;
