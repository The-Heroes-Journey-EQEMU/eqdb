import React, { useEffect, useState } from 'react';
import { zoneService, ZoneDetails as ZoneDetailsType } from '@/services/zoneService';
import { Table, TableBody, TableCell,TableRow } from '@/components/common/Table';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface ZoneDetailsProps {
  shortName: string;
}

const ZoneDetails: React.FC<ZoneDetailsProps> = ({ shortName }) => {
  const [zoneDetails, setZoneDetails] = useState<ZoneDetailsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchZoneDetails = async () => {
      try {
        setLoading(true);
        const details = await zoneService.getZoneDetails(shortName);
        setZoneDetails(details);
      } catch (err) {
        setError('Failed to fetch zone details.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchZoneDetails();
  }, [shortName]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  if (!zoneDetails) {
    return <div>No details found for this zone.</div>;
  }

  return (
    <Table>
          <TableBody>
            <TableRow>
              <TableCell className="text-xs text-white">Zone ID</TableCell>
              <TableCell>{zoneDetails.zoneidnumber}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-xs text-white">Expansion</TableCell>
              <TableCell>{zoneDetails.expansion}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-xs text-white">Short Name</TableCell>
              <TableCell>{zoneDetails.short_name}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-xs text-white">Bindable</TableCell>
              <TableCell>{zoneDetails.canbind ? 'Yes' : 'No'}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-xs text-white">Levitation</TableCell>
              <TableCell>{zoneDetails.canlevitate ? 'Allowed' : 'Not Allowed'}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-xs text-white">Zone Type</TableCell>
              <TableCell>{zoneDetails.castoutdoor ? 'Outdoor' : 'Indoor'}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-xs text-white">Level Range</TableCell>
              <TableCell>{zoneDetails.zone_level_range}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-xs text-white">Experience Multiplier</TableCell>
              <TableCell>{zoneDetails.zone_exp_multiplier}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-xs text-white">Succor Location</TableCell>
              <TableCell>{zoneDetails.safe_x}, {zoneDetails.safe_y}, {zoneDetails.safe_z}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="text-xs text-white">Newbie Zone</TableCell>
              <TableCell>{zoneDetails.newbie_zone ? 'Yes' : 'No'}</TableCell>
            </TableRow>
            {zoneDetails.waypoint_x && (
              <TableRow>
                <TableCell className="text-xs text-white">Waypoint</TableCell>
                <TableCell>{zoneDetails.waypoint_x}, {zoneDetails.waypoint_y}, {zoneDetails.waypoint_z}</TableCell>
              </TableRow>
            )}
          </TableBody>
    </Table>
  );
};

export default ZoneDetails;
