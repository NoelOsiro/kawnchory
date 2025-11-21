'use client';

import type { TableHeadCellProps } from 'src/components/table';
import type { ICustomerItem, ICustomerTableFilters } from 'src/types/customer';

import { varAlpha } from 'minimal-shared/utils';
import { useMemo, useEffect, useCallback } from 'react';
import { useBoolean, useSetState } from 'minimal-shared/hooks';

// Material-UI components
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Card from '@mui/material/Card';
import Tabs from '@mui/material/Tabs';
import Table from '@mui/material/Table';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import TableBody from '@mui/material/TableBody';
import IconButton from '@mui/material/IconButton';

// Routing
import { paths } from 'src/routes/paths';
import { RouterLink } from 'src/routes/components';

// Mock data and store
import { _roles, USER_STATUS_OPTIONS } from 'src/_mock';
import { _customerList } from 'src/_mock/_customerList';
import { DashboardContent } from 'src/layouts/dashboard';
import { useCustomerStore } from 'src/store/customerStore';

import { Label } from 'src/components/label';
import { toast } from 'src/components/snackbar';
import { Iconify } from 'src/components/iconify';
import { Scrollbar } from 'src/components/scrollbar';
// UI Components
import { ConfirmDialog } from 'src/components/custom-dialog';
import { CustomBreadcrumbs } from 'src/components/custom-breadcrumbs';
// Table components
import {
  useTable,
  emptyRows,
  rowInPage,
  TableNoData,
  getComparator,
  TableEmptyRows,
  TableHeadCustom,
  TableSelectedAction,
  TablePaginationCustom,
} from 'src/components/table';

import { CustomerTableRow } from '../customer-table-row';
// Local components
import { CustomerTableToolbar } from '../customer-table-toolbar';
import { CustomerTableFiltersResult } from '../customer-table-filters-result';

// ----------------------------------------------------------------------

const STATUS_OPTIONS = [{ value: 'all', label: 'All' }, ...USER_STATUS_OPTIONS];

const TABLE_HEAD: TableHeadCellProps[] = [
  { id: 'name', label: 'Name', width: 220 },
  { id: 'phone', label: 'Phone', width: 180 },
  { id: 'service_type', label: 'Service Type', width: 180 },
  { id: 'email', label: 'Email', width: 180 },
  { id: 'status', label: 'Status', width: 100 },
  { id: 'location', label: 'Location', width: 180 },
  { id: '', width: 88 },
];

// ----------------------------------------------------------------------


export function SegmentListView() {
  const table = useTable();
  const confirmDialog = useBoolean();
  const filters = useSetState<ICustomerTableFilters>({
    name: '',
    role: [],
    status: 'all',
  });
  const { state: currentFilters, setState: updateFilters } = filters;

  const customers = useCustomerStore((state) => state.customers);
  const fetchCustomers = useCustomerStore((state) => state.fetchCustomers);
  const loading = useCustomerStore((state) => state.loading);
  const error = useCustomerStore((state) => state.error);
  const deleteCustomer = useCustomerStore((state) => state.deleteCustomer);

  // Fetch customers on mount
  useEffect(() => {
    fetchCustomers();
  }, [fetchCustomers]);

  // Show error toast when there's an error
  useEffect(() => {
    if (error) {
      toast.error(error.message || 'An error occurred while fetching customers');
    }
  }, [error]);

  // Use store data or fallback to mock
  const tableData = useMemo(() => (customers.length > 0 ? customers : _customerList), [customers]);

  const dataFiltered = applyFilter({
    inputData: tableData,
    comparator: getComparator(table.order, table.orderBy),
    filters: currentFilters,
  });

  const dataInPage = rowInPage(dataFiltered, table.page, table.rowsPerPage);

  const canReset =
    !!currentFilters.name || currentFilters.role.length > 0 || currentFilters.status !== 'all';

  const notFound = (!dataFiltered.length && canReset) || !dataFiltered.length;

  // Delete a single row using store
  const handleDeleteRow = useCallback(
    async (id: string) => {
      const customerToDelete = tableData.find((row) => row.id === id);
      if (!customerToDelete) return;
      try {
        await deleteCustomer(customerToDelete);
        toast.success('Delete success!');
        table.onUpdatePageDeleteRow(dataInPage.length);
      } catch {
        toast.error('Delete failed!');
      }
    },
    [tableData, deleteCustomer, table, dataInPage.length]
  );

  // Delete selected rows using store
  const handleDeleteRows = useCallback(async () => {
    const customersToDelete = tableData.filter((row) => table.selected.includes(row.id));
    if (customersToDelete.length === 0) return;
    try {
      await Promise.all(customersToDelete.map((customer) => deleteCustomer(customer)));
      toast.success('Delete success!');
      table.onUpdatePageDeleteRows(dataInPage.length, dataFiltered.length);
    } catch {
      toast.error('Delete failed!');
    }
  }, [tableData, table, dataInPage.length, dataFiltered.length, deleteCustomer]);

  const handleFilterStatus = useCallback(
    (event: React.SyntheticEvent, newValue: string) => {
      table.onResetPage();
      updateFilters({ status: newValue });
    },
    [updateFilters, table]
  );

  const renderConfirmDialog = () => (
    <ConfirmDialog
      open={confirmDialog.value}
      onClose={confirmDialog.onFalse}
      title="Delete"
      content={
        <>
          Are you sure want to delete <strong> {table.selected.length} </strong> items?
        </>
      }
      action={
        <Button
          variant="contained"
          color="error"
          onClick={() => {
            handleDeleteRows();
            confirmDialog.onFalse();
          }}
        >
          Delete
        </Button>
      }
    />
  );

  // Add handleResetPage to reset filters and table page
  const handleResetPage = useCallback(() => {
    updateFilters({
      name: '',
      role: [],
      status: 'all',
    });
    table.onResetPage();
  }, [updateFilters, table]);

  const memoizedFilters = useMemo(() => ({
    state: currentFilters,
    setState: updateFilters,
    resetState: handleResetPage,
    setField: (field: keyof ICustomerTableFilters, value: any) => {
      updateFilters({ [field]: value });
    }
  }), [currentFilters, updateFilters, handleResetPage]);

  const filtersResultProps = useMemo(() => ({
    state: currentFilters,
    setState: (updateState: any) => {
      updateFilters(updateState);
    },
    resetState: handleResetPage,
    setField: (field: keyof ICustomerTableFilters, value: any) => {
      updateFilters({ [field]: value });
    },
  }), [currentFilters, updateFilters, handleResetPage]);


  

  return (
    <>
      <DashboardContent>
        <CustomBreadcrumbs
          heading="List"
          links={[
            { name: 'Dashboard', href: paths.dashboard.root },
            { name: 'Customers', href: paths.dashboard.customer.root },
            { name: 'List' },
          ]}
          action={
            <Button
              component={RouterLink}
              href={paths.dashboard.customer.new}
              variant="contained"
              startIcon={<Iconify icon="mingcute:add-line" />}
            >
              New customer
            </Button>
          }
          sx={{ mb: { xs: 3, md: 5 } }}
        />

        <Card>
          <Tabs
            value={currentFilters.status}
            onChange={handleFilterStatus}
            sx={[
              (theme) => ({
                px: 2.5,
                boxShadow: `inset 0 -2px 0 0 ${varAlpha(theme.vars.palette.grey['500Channel'], 0.08)}`,
              }),
            ]}
          >
            {STATUS_OPTIONS.map((tab) => (
              <Tab
                key={tab.value}
                iconPosition="end"
                value={tab.value}
                label={tab.label}
                icon={
                  <Label
                    variant={
                      ((tab.value === 'all' || tab.value === currentFilters.status) && 'filled') ||
                      'soft'
                    }
                    color={
                      (tab.value === 'active' && 'success') ||
                      (tab.value === 'pending' && 'warning') ||
                      (tab.value === 'banned' && 'error') ||
                      'default'
                    }
                  >
                    {['active', 'pending', 'banned', 'rejected'].includes(tab.value)
                      ? tableData.filter((user) => user.status === tab.value).length
                      : tableData.length}
                  </Label>
                }
              />
            ))}
          </Tabs>

          {/** Memoize filters object to prevent infinite update loop */}
          <CustomerTableToolbar
            filters={memoizedFilters}
            onResetPage={table.onResetPage}
            options={{
              roles: _roles,
            }}
          />

          {canReset && (
            <CustomerTableFiltersResult
              filters={filtersResultProps}
              totalResults={dataFiltered.length}
              onResetPage={handleResetPage}
              sx={{ p: 2.5, pt: 0 }}
            />
          )}

          <Box sx={{ position: 'relative' }}>
            {loading ? (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Iconify icon="eos-icons:loading" width={40} sx={{ color: 'primary.main' }} />
                <Box sx={{ mt: 2 }}>Loading customers...</Box>
              </Box>
            ) : error ? (
              <Box sx={{ p: 4, textAlign: 'center', color: 'error.main' }}>
                <Iconify icon="mdi:alert-circle-outline" width={40} />
                <Box sx={{ mt: 2 }}>Error loading customers. Please try again later.</Box>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={fetchCustomers}
                  sx={{ mt: 2 }}
                  startIcon={<Iconify icon="mdi:refresh" />}
                >
                  Retry
                </Button>
              </Box>
            ) : (
              <>
                <TableSelectedAction
                  dense={table.dense}
                  numSelected={table.selected.length}
                  rowCount={dataFiltered.length}
                  onSelectAllRows={(checked) =>
                    table.onSelectAllRows(
                      checked,
                      dataFiltered.map((row) => row.id)
                    )
                  }
                  action={
                    <Tooltip title="Delete">
                      <IconButton color="primary" onClick={confirmDialog.onTrue}>
                        <Iconify icon="solar:trash-bin-trash-bold" />
                      </IconButton>
                    </Tooltip>
                  }
                />

                <Scrollbar>
                  <Table size={table.dense ? 'small' : 'medium'} sx={{ minWidth: 960 }}>
                    <TableHeadCustom
                      order={table.order}
                      orderBy={table.orderBy}
                      headCells={TABLE_HEAD}
                      rowCount={dataFiltered.length}
                      numSelected={table.selected.length}
                      onSort={table.onSort}
                      onSelectAllRows={(checked) =>
                        table.onSelectAllRows(
                          checked,
                          dataFiltered.map((row) => row.id)
                        )
                      }
                    />

                    <TableBody>
                      {dataFiltered
                        .slice(
                          table.page * table.rowsPerPage,
                          table.page * table.rowsPerPage + table.rowsPerPage
                        )
                        .map((row) => (
                          <CustomerTableRow
                            key={row.id}
                            row={row}
                            selected={table.selected.includes(row.id)}
                            onSelectRow={() => table.onSelectRow(row.id)}
                            onDeleteRow={() => handleDeleteRow(row.id)}
                            editHref={paths.dashboard.customer.edit2(row.id)}
                          />
                        ))}

                      <TableEmptyRows
                        height={table.dense ? 56 : 56 + 20}
                        emptyRows={emptyRows(table.page, table.rowsPerPage, dataFiltered.length)}
                      />

                      <TableNoData notFound={notFound} />
                    </TableBody>
                  </Table>
                </Scrollbar>
              </>
            )}
          </Box>

          <TablePaginationCustom
            page={table.page}
            dense={table.dense}
            count={dataFiltered.length}
            rowsPerPage={table.rowsPerPage}
            onPageChange={table.onChangePage}
            onChangeDense={table.onChangeDense}
            onRowsPerPageChange={table.onChangeRowsPerPage}
          />
        </Card>
      </DashboardContent>

      {renderConfirmDialog()}
    </>
  );
}

// ----------------------------------------------------------------------

type ApplyFilterProps = {
  inputData: ICustomerItem[];
  filters: ICustomerTableFilters;
  comparator: (a: any, b: any) => number;
};

function applyFilter({ inputData, comparator, filters }: ApplyFilterProps) {
  const { name, status, role } = filters;

  const stabilizedThis = inputData.map((el, index) => [el, index] as const);

  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });

  inputData = stabilizedThis.map((el) => el[0]);

  if (name) {
    inputData = inputData.filter((user) => user.name.toLowerCase().includes(name.toLowerCase()));
  }

  if (status !== 'all') {
    inputData = inputData.filter((user) => user.status === status);
  }

  if (role.length) {
    inputData = inputData.filter((user) => role.includes(user.role));
  }

  return inputData;
}
