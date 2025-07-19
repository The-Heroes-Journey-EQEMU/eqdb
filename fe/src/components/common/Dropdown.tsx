import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { NavigationItem } from './Navigation';

interface DropdownProps {
  item: NavigationItem;
  isActive: (href: string) => boolean;
  handleNavigationClick: (item: NavigationItem) => void;
}

const Dropdown: React.FC<DropdownProps> = ({ item, handleNavigationClick }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="nav-item w-full text-left"
      >
        <span>{item.name}</span>
        <span className="ml-auto">{isOpen ? '▲' : '▼'}</span>
      </button>
      {isOpen && (
        <div className="pl-4">
          {item.children?.map((child) => (
            <Link
              key={child.id}
              to={child.href}
              className="nav-item"
              onClick={() => {
                handleNavigationClick(child);
                setIsOpen(false);
              }}
            >
              {child.name}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dropdown;
