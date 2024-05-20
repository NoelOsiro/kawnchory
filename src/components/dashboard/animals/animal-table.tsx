'use client';

import * as React from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Checkbox from '@mui/material/Checkbox';
import Divider from '@mui/material/Divider';
import Stack from '@mui/material/Stack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import dayjs from 'dayjs';

import { useSelection } from '@/hooks/use-selection';

function noop(): void {
  // do nothing
}

export interface Animal {
  id: string;
  name: string;
  breed: string;
  gender: string;  // Added gender
  rfid: string;
  microchipId: string;
  tagNumber: string;  // Added tag number
  dob: Date;  // Date of Birth
  createdAt: Date;
  owner: string;  // Added owner information
  currentLocation: string;  // Added current location
  medicalHistory: string[];  // Added medical history
  status: string;  // Added status
}


interface AnimalsTableProps {
  count?: number;
  page?: number;
  rows?: Animal[];
  rowsPerPage?: number;
}

const calculateAge = (dob: Date): number => {
  const birthDate = dayjs(dob);
  const currentDate = dayjs();
  return currentDate.diff(birthDate, 'year');
};

export function AnimalsTable({
  count = 0,
  rows = [],
  page = 0,
  rowsPerPage = 0,
}: AnimalsTableProps): React.JSX.Element {
  const rowIds = React.useMemo(() => {
    return rows.map((animal) => animal.id);
  }, [rows]);

  const { selectAll, deselectAll, selectOne, deselectOne, selected } = useSelection(rowIds);

  const selectedSome = (selected?.size ?? 0) > 0 && (selected?.size ?? 0) < rows.length;
  const selectedAll = rows.length > 0 && selected?.size === rows.length;

  return (
    <Card>
      <Box sx={{ overflowX: 'auto' }}>
        <Table sx={{ minWidth: '800px' }}>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedAll}
                  indeterminate={selectedSome}
                  onChange={(event) => {
                    if (event.target.checked) {
                      selectAll();
                    } else {
                      deselectAll();
                    }
                  }}
                />
              </TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Breed</TableCell>
              <TableCell>Gender</TableCell>
              <TableCell>Tag Number</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Current Location</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Age</TableCell>
              <TableCell>Signed Up</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => {
              const isSelected = selected?.has(row.id);
              const age = calculateAge(row.dob);

              return (
                <TableRow hover key={row.id} selected={isSelected}>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={isSelected}
                      onChange={(event) => {
                        if (event.target.checked) {
                          selectOne(row.id);
                        } else {
                          deselectOne(row.id);
                        }
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Stack sx={{ alignItems: 'center' }} direction="row" spacing={2}>
                      {/* <Avatar src={row.avatar} /> */}
                      <Typography variant="subtitle2">{row.name}</Typography>
                    </Stack>
                  </TableCell>
                  <TableCell>{row.breed}</TableCell>
                  <TableCell>{row.gender}</TableCell>
                  <TableCell>{row.tagNumber}</TableCell>
                  <TableCell>{row.owner}</TableCell>
                  <TableCell>{row.currentLocation}</TableCell>
                  <TableCell>{row.status}</TableCell>
                  <TableCell>{age}</TableCell>
                  <TableCell>{dayjs(row.createdAt).format('MMM D, YYYY')}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Box>
      <Divider />
      <TablePagination
        component="div"
        count={count}
        onPageChange={noop}
        onRowsPerPageChange={noop}
        page={page}
        rowsPerPage={rowsPerPage}
        rowsPerPageOptions={[5, 10, 25]}
      />
    </Card>
  );
}
