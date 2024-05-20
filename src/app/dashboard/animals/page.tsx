import * as React from 'react';
import type { Metadata } from 'next';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { Download as DownloadIcon } from '@phosphor-icons/react/dist/ssr/Download';
import { Plus as PlusIcon } from '@phosphor-icons/react/dist/ssr/Plus';
import { Upload as UploadIcon } from '@phosphor-icons/react/dist/ssr/Upload';

import { config } from '@/config';
import { AnimalsFilters } from '@/components/dashboard/animals/animal-filters';
import { AnimalsTable } from '@/components/dashboard/animals/animal-table';
import type { Animal } from '@/components/dashboard/animals/animal-table';

export const metadata = { title: `Customers | Dashboard | ${config.site.name}` } satisfies Metadata;

const animals = [
  {
    id: '1',
    name: 'Bella',
    breed: 'Holstein',
    gender: 'Female',
    rfid: 'RFID001',
    microchipId: 'MIC001',
    tagNumber: 'TAG001',
    dob: new Date('2018-05-21'),
    createdAt: new Date('2018-05-21T10:30:00Z'),
    owner: 'John Doe',
    currentLocation: 'Pasture A',
    medicalHistory: ['Vaccinated for BVD', 'Treated for mastitis'],
    status: 'Active',
  },
  {
    id: '2',
    name: 'Max',
    breed: 'Angus',
    gender: 'Male',
    rfid: 'RFID002',
    microchipId: 'MIC002',
    tagNumber: 'TAG002',
    dob: new Date('2019-03-14'),
    createdAt: new Date('2019-03-14T08:45:00Z'),
    owner: 'Jane Smith',
    currentLocation: 'Barn B',
    medicalHistory: ['Dewormed', 'Vaccinated for brucellosis'],
    status: 'Active',
  },
  {
    id: '3',
    name: 'Lucy',
    breed: 'Jersey',
    gender: 'Female',
    rfid: 'RFID003',
    microchipId: 'MIC003',
    tagNumber: 'TAG003',
    dob: new Date('2017-11-22'),
    createdAt: new Date('2017-11-22T14:00:00Z'),
    owner: 'Sam Wilson',
    currentLocation: 'Pasture C',
    medicalHistory: ['Vaccinated for leptospirosis', 'Treated for lameness'],
    status: 'Active',
  },
  {
    id: '4',
    name: 'Charlie',
    breed: 'Hereford',
    gender: 'Male',
    rfid: 'RFID004',
    microchipId: 'MIC004',
    tagNumber: 'TAG004',
    dob: new Date('2020-01-15'),
    createdAt: new Date('2020-01-15T12:15:00Z'),
    owner: 'Laura Brown',
    currentLocation: 'Pasture D',
    medicalHistory: ['Castrated', 'Vaccinated for IBR'],
    status: 'Active',
  },
  {
    id: '5',
    name: 'Molly',
    breed: 'Simmental',
    gender: 'Female',
    rfid: 'RFID005',
    microchipId: 'MIC005',
    tagNumber: 'TAG005',
    dob: new Date('2016-07-30'),
    createdAt: new Date('2016-07-30T09:00:00Z'),
    owner: 'Bill Green',
    currentLocation: 'Pasture E',
    medicalHistory: ['Vaccinated for BRSV', 'Treated for pinkeye'],
    status: 'Active',
  },
  {
    id: '6',
    name: 'Oscar',
    breed: 'Charolais',
    gender: 'Male',
    rfid: 'RFID006',
    microchipId: 'MIC006',
    tagNumber: 'TAG006',
    dob: new Date('2019-09-10'),
    createdAt: new Date('2019-09-10T07:45:00Z'),
    owner: 'Nina White',
    currentLocation: 'Barn A',
    medicalHistory: ['Vaccinated for clostridial diseases', 'Treated for respiratory infection'],
    status: 'Active',
  },
  {
    id: '7',
    name: 'Daisy',
    breed: 'Guernsey',
    gender: 'Female',
    rfid: 'RFID007',
    microchipId: 'MIC007',
    tagNumber: 'TAG007',
    dob: new Date('2018-04-05'),
    createdAt: new Date('2018-04-05T11:30:00Z'),
    owner: 'Oliver Black',
    currentLocation: 'Pasture F',
    medicalHistory: ['Vaccinated for Johne’s disease', 'Treated for udder infection'],
    status: 'Active',
  },
  {
    id: '8',
    name: 'Henry',
    breed: 'Limousin',
    gender: 'Male',
    rfid: 'RFID008',
    microchipId: 'MIC008',
    tagNumber: 'TAG008',
    dob: new Date('2021-06-17'),
    createdAt: new Date('2021-06-17T10:00:00Z'),
    owner: 'Emily Gray',
    currentLocation: 'Pasture G',
    medicalHistory: ['Vaccinated for blackleg', 'Treated for gastrointestinal issues'],
    status: 'Active',
  },
  {
    id: '9',
    name: 'Lily',
    breed: 'Brahman',
    gender: 'Female',
    rfid: 'RFID009',
    microchipId: 'MIC009',
    tagNumber: 'TAG009',
    dob: new Date('2020-12-25'),
    createdAt: new Date('2020-12-25T15:00:00Z'),
    owner: 'George Brown',
    currentLocation: 'Pasture H',
    medicalHistory: ['Vaccinated for BVD', 'Treated for hoof rot'],
    status: 'Active',
  },
  {
    id: '10',
    name: 'Jack',
    breed: 'Brangus',
    gender: 'Male',
    rfid: 'RFID010',
    microchipId: 'MIC010',
    tagNumber: 'TAG010',
    dob: new Date('2017-02-28'),
    createdAt: new Date('2017-02-28T08:00:00Z'),
    owner: 'Susan Blue',
    currentLocation: 'Barn C',
    medicalHistory: ['Vaccinated for PI3', 'Treated for respiratory issues'],
    status: 'Active',
  },
] satisfies Animal[];

export default function Page(): React.JSX.Element {
  const page = 0;
  const rowsPerPage = 5;

  const paginatedAnimals = applyPagination(animals, page, rowsPerPage);

  return (
    <Stack spacing={3}>
      <Stack direction="row" spacing={3}>
        <Stack spacing={1} sx={{ flex: '1 1 auto' }}>
          <Typography variant="h4">Farm Records</Typography>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
            <Button color="inherit" startIcon={<UploadIcon fontSize="var(--icon-fontSize-md)" />}>
              Import
            </Button>
            <Button color="inherit" startIcon={<DownloadIcon fontSize="var(--icon-fontSize-md)" />}>
              Export
            </Button>
          </Stack>
        </Stack>
        <div>
          <Button startIcon={<PlusIcon fontSize="var(--icon-fontSize-md)" />} variant="contained">
            Add
          </Button>
        </div>
      </Stack>
      <AnimalsFilters />
      <AnimalsTable
        count={paginatedAnimals.length}
        page={page}
        rows={paginatedAnimals}
        rowsPerPage={rowsPerPage}
      />
    </Stack>
  );
}

function applyPagination(rows: Animal[], page: number, rowsPerPage: number): Animal[] {
  return rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
}
