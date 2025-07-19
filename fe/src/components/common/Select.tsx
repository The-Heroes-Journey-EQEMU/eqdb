import React from 'react';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
}

const Select: React.FC<SelectProps> = ({ label, children, ...props }) => {
  return (
    <div>
      <label className="block text-sm font-medium text-foreground mb-1">{label}</label>
      <select
        className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-[24px] bg-background px-[8px] py-[8px]"
        {...props}
      >
        {children}
      </select>
    </div>
  );
};

export default Select;
