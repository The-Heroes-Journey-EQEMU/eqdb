import React, { useState, useEffect } from 'react';
import { Item, ItemSearchResponse } from '../../services/itemService';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { 
  Pagination, 
  PaginationContent, 
  PaginationEllipsis, 
  PaginationItem, 
  PaginationLink, 
  PaginationNext, 
  PaginationPrevious 
} from '../ui/pagination';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { 
  HoverCard, 
  HoverCardContent, 
  HoverCardTrigger 
} from '../ui/hover-card';
import { Download } from 'lucide-react';

interface ItemSearchTableProps {
  items: ItemSearchResponse | null;
  isLoading: boolean;
  error: Error | null;
  currentPage?: number;
  itemsPerPage?: number;
  hasWeights?: boolean;
  onPageChange?: (page: number) => void;
  onSortChange?: (sortBy: string) => void;
  onItemClick?: (item: Item) => void;
}

const ItemSearchTable: React.FC<ItemSearchTableProps> = ({ 
  items, 
  isLoading, 
  error,
  currentPage = 1,
  itemsPerPage = 50,
  hasWeights = false,
  onPageChange,
  onSortChange,
  onItemClick
}) => {
  const [sortBy, setSortBy] = useState(hasWeights ? 'weight' : 'id');

  // Update sortBy when hasWeights changes
  useEffect(() => {
    setSortBy(hasWeights ? 'weight' : 'id');
  }, [hasWeights]);

  const handleSortChange = (value: string) => {
    console.log('Sort changed to:', value);
    setSortBy(value);
    onSortChange?.(value);
  };

  const handleItemClick = (item: Item) => {
    onItemClick?.(item);
  };

  const getPaginationInfo = () => {
    const totalItems = items?.total || 0;
    const startItem = (currentPage - 1) * itemsPerPage + 1;
    const endItem = Math.min(currentPage * itemsPerPage, totalItems);
    return { startItem, endItem };
  };

  const renderPagination = () => {
    const totalPages = items?.pages || 1;
    
    if (totalPages <= 1) return null;

    const pages = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) {
          pages.push(i);
        }
        pages.push('ellipsis');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('ellipsis');
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        pages.push(1);
        pages.push('ellipsis');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i);
        }
        pages.push('ellipsis');
        pages.push(totalPages);
      }
    }

    return (
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious 
              href="#" 
              onClick={(e) => {
                e.preventDefault();
                if (currentPage > 1) onPageChange?.(currentPage - 1);
              }}
              className={currentPage <= 1 ? 'pointer-events-none opacity-50' : ''}
            />
          </PaginationItem>
          
          {pages.map((page, index) => (
            <PaginationItem key={index}>
              {page === 'ellipsis' ? (
                <PaginationEllipsis />
              ) : (
                <PaginationLink
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    onPageChange?.(page as number);
                  }}
                  isActive={page === currentPage}
                >
                  {page}
                </PaginationLink>
              )}
            </PaginationItem>
          ))}
          
          <PaginationItem>
            <PaginationNext 
              href="#" 
              onClick={(e) => {
                e.preventDefault();
                if (currentPage < totalPages) onPageChange?.(currentPage + 1);
              }}
              className={currentPage >= totalPages ? 'pointer-events-none opacity-50' : ''}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    );
  };

  if (isLoading) {
    return (
      <Card>
        <CardBody>
          <div className="text-center py-8">
            <LoadingSpinner size="lg" className="mx-auto mb-4" />
            <p className="text-muted-foreground">Searching for items...</p>
          </div>
        </CardBody>
      </Card>
    );
  }

  if (error) {
    return (
      <Card variant="outlined">
        <CardBody>
          <div className="text-center py-4">
            <div className="text-destructive mb-2">
              <svg className="w-8 h-8 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="text-destructive font-medium">Error loading items</p>
            <p className="text-destructive/80 text-sm mt-1">{error.message}</p>
          </div>
        </CardBody>
      </Card>
    );
  }

  if (items && items.results && items.results.length > 0) {
    const { startItem, endItem } = getPaginationInfo();
    
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium">Sort by:</span>
                <Select value={sortBy} onValueChange={handleSortChange}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="id">ID</SelectItem>
                    <SelectItem value="weight">Weight</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <CardTitle>Found {items.total} Results - Showing {startItem}-{endItem}</CardTitle>
            </div>
            
            <div className="flex items-center space-x-4">
              {renderPagination()}
            </div>
            
            <Button variant="ghost" size="sm" className="p-2">
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardBody>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 font-medium text-foreground w-16">
                    Icon
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-foreground">
                    Item Name
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-foreground">
                    Zones/Mobs
                  </th>
                </tr>
              </thead>
              <tbody>
                {items.results.map((item: Item) => (
                  <HoverCard key={item.id}>
                    <HoverCardTrigger asChild>
                      <tr 
                        className="border-b border-border hover:bg-muted/50 transition-colors cursor-pointer"
                        onClick={() => handleItemClick(item)}
                      >
                        <td className="py-3 px-4">
                          <img
                            src={`/item_icons/item_${item.id}.png`}
                            alt={item.name}
                            className="w-8 h-8 object-contain"
                            onError={(e) => {
                              e.currentTarget.src = '/item_icons/item_default.png';
                            }}
                          />
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex flex-col">
                            <span className="font-medium text-foreground">{item.name}</span>
                            <span className="text-xs text-muted-foreground">ID: {item.id}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="text-sm text-muted-foreground">
                            {/* TODO: Replace with actual zones/mobs data when available */}
                            <span className="text-muted-foreground/60 italic">TBD - Zones/Mobs data</span>
                          </div>
                        </td>
                      </tr>
                    </HoverCardTrigger>
                    <HoverCardContent className="w-80">
                      <div className="flex items-start space-x-3">
                        <img
                          src={`/item_icons/item_${item.id}.png`}
                          alt={item.name}
                          className="w-12 h-12 object-contain"
                          onError={(e) => {
                            e.currentTarget.src = '/item_icons/item_default.png';
                          }}
                        />
                        <div className="flex-1">
                          <h4 className="font-medium text-foreground mb-1">{item.name}</h4>
                          <p className="text-sm text-muted-foreground mb-2">ID: {item.id}</p>
                          <p className="text-sm text-muted-foreground mb-3">Type: {item.type}</p>
                          <div className="text-xs text-muted-foreground">
                            <p className="font-medium mb-1">TBD - Item Details View</p>
                            <p>This will show comprehensive item information including:</p>
                            <ul className="list-disc list-inside mt-1 space-y-1">
                              <li>Item stats and effects</li>
                              <li>Class and race requirements</li>
                              <li>Drop locations and rates</li>
                              <li>Quest information</li>
                              <li>Recipe requirements</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </HoverCardContent>
                  </HoverCard>
                ))}
              </tbody>
            </table>
          </div>

          {renderPagination()}
        </CardBody>
      </Card>
    );
  }

  if (items && items.results && items.results.length === 0) {
    return (
      <Card>
        <CardBody>
          <div className="text-center py-8">
            <div className="text-muted-foreground mb-4">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <p className="text-muted-foreground font-medium">No items found</p>
            <p className="text-muted-foreground/80 text-sm mt-1">
              Try adjusting your search criteria
            </p>
          </div>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardBody>
        <div className="text-center py-8">
          <div className="text-muted-foreground mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <p className="text-muted-foreground font-medium">Ready to search</p>
          <p className="text-muted-foreground/80 text-sm mt-1">
            Enter your search criteria above to find items
          </p>
        </div>
      </CardBody>
    </Card>
  );
};

export default ItemSearchTable; 