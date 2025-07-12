import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { NavigationItem } from './Navigation';

interface DropdownProps {
  item: NavigationItem;
  isActive: (href: string) => boolean;
  handleNavigationClick: (item: NavigationItem) => void;
  isMobile: boolean;
}

const Dropdown: React.FC<DropdownProps> = ({ item, isActive, handleNavigationClick, isMobile }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          nav-item
          ${isActive(item.href) ? 'active' : ''}
          ${isMobile ? 'w-full text-left' : ''}
        `}
      >
        <span className={`text-${isMobile ? 'lg' : 'base'}`}>{item.icon}</span>
        <span>{item.name}</span>
        <span className="ml-1">▼</span>
      </button>
      {isOpen && (
        <div
          className={`
            absolute ${isMobile ? 'left-full top-0 ml-1' : 'top-full left-0 mt-1'} 
            bg-card border border-border rounded-md shadow-lg z-50
          `}
        >
          {item.children?.map((child) => (
            <Link
              key={child.id}
              to={child.href}
              className={`
                block px-4 py-2 text-sm text-foreground hover:bg-muted
                ${isActive(child.href) ? 'font-bold' : ''}
              `}
              onClick={() => {
                handleNavigationClick(child);
                setIsOpen(false);
              }}
            >
              <span className={`text-${isMobile ? 'lg' : 'base'} mr-2`}>{child.icon}</span>
              {child.name}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dropdown;
