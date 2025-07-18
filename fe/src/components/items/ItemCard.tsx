import React from 'react';
import { Link } from 'react-router-dom';
import { ZoneItem } from '@/services/zoneService';

interface ItemCardProps {
  item: ZoneItem;
}

const ItemCard: React.FC<ItemCardProps> = ({ item }) => {
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    e.currentTarget.src = '/item_icons/item_default.png';
  };

  return (
    <Link to={`/items/details/${item.id}`} className="card rounded-[24px] overflow-hidden">
      <div className="p-[8px] bg-gray-800 flex flex-col items-center justify-center min-h-[145px] rounded-b-[16px]">
        <img
          src={`/item_icons/item_${item.icon}.png`}
          alt={item.name}
          onError={handleImageError}
          className="w-12 h-12 object-contain"
        />
        <span className="text-sm text-center mt-2 text-white">{item.name}</span>
      </div>
    </Link>
  );
};

export default ItemCard;
