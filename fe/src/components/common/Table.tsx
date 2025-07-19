import React from 'react';

export const Table: React.FC<React.HTMLAttributes<HTMLTableElement>> = ({ className = '', ...props }) => (
  <table className={`w-full text-sm text-left text-gray-500 dark:text-gray-400 rounded-[24px] ${className}`} {...props} />
);

export const TableHead: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({ className = '', ...props }) => (
  <thead className={`text-xxs text-gray-500 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-300 rounded-t-[16px] ${className}`} {...props} />
);

export const TableBody: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({ className = '', ...props }) => (
  <tbody className={`bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700 rounded-b-[16px] ${className}`} {...props} />
);

export const TableRow: React.FC<React.HTMLAttributes<HTMLTableRowElement>> = ({ className = '', ...props }) => (
  <tr className={`hover:bg-gray-100 dark:hover:bg-gray-600 rounded-[16px] ${className}`} {...props} />
);

export const TableHeader: React.FC<React.HTMLAttributes<HTMLTableCellElement>> = ({ className = '', ...props }) => (
  <th scope="col" className={`px-[8px] py-[8px] rounded-[16px] ${className}`} {...props} />
);

export const TableCell: React.FC<React.HTMLAttributes<HTMLTableCellElement>> = ({ className = '', ...props }) => (
  <td className={`px-[8px] py-[8px] rounded-[16px] ${className}`} {...props} />
);
