'use client';

import { useEffect } from 'react';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';

import { DashboardContent } from 'src/layouts/dashboard';
import { useCustomerStore } from 'src/store/customerStore';
import { _bookings, _bookingNew, _bookingReview, _bookingsOverview } from 'src/_mock';
import {
  BookingIllustration,
  CheckInIllustration,
  CheckoutIllustration,
} from 'src/assets/illustrations';

import { BookingBooked } from '../booking-booked';
import { BookingNewest } from '../booking-newest';
import { BookingDetails } from '../booking-details';
import { BookingAvailable } from '../booking-available';
import { BookingStatistics } from '../booking-statistics';
import { BookingTotalIncomes } from '../booking-total-incomes';
import { BookingWidgetSummary } from '../booking-widget-summary';
import { BookingCheckInWidgets } from '../booking-check-in-widgets';
import { BookingCustomerReviews } from '../booking-customer-reviews';

// ----------------------------------------------------------------------

export function OverviewBookingView() {
  const customers = useCustomerStore((state) => state.customers);
  const fetchCustomers = useCustomerStore((state) => state.fetchCustomers);

  useEffect(() => {
    fetchCustomers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const totalActive = customers.length;
  const totalPPPoE = customers.filter((c) => c.service_type === 'ppoe').length;
  const totalHotspot = customers.filter((c) => c.service_type === 'hotspot').length;

  return (
    <DashboardContent maxWidth="xl">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <BookingWidgetSummary
            title="Total Active Users"
            percent={0}
            total={totalActive}
            icon={<BookingIllustration />}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <BookingWidgetSummary
            title="PPPoE Users"
            percent={0}
            total={totalPPPoE}
            icon={<CheckInIllustration />}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <BookingWidgetSummary
            title="Hotspot Users"
            percent={0}
            total={totalHotspot}
            icon={<CheckoutIllustration />}
          />
        </Grid>

        <Grid container size={12}>
          <Grid size={{ xs: 12, md: 7, lg: 8 }}>
            <Box
              sx={{
                mb: 3,
                p: { md: 1 },
                display: 'flex',
                gap: { xs: 3, md: 1 },
                borderRadius: { md: 2 },
                flexDirection: 'column',
                bgcolor: { md: 'background.neutral' },
              }}
            >
              <Box
                sx={{
                  p: { md: 1 },
                  display: 'grid',
                  gap: { xs: 3, md: 0 },
                  borderRadius: { md: 2 },
                  bgcolor: { md: 'background.paper' },
                  gridTemplateColumns: { xs: 'repeat(1, 1fr)', md: 'repeat(2, 1fr)' },
                }}
              >
                <BookingTotalIncomes
                  title="Total users"
                  total={totalActive}
                  percent={2.6}
                  chart={{
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                    series: [{ data: [10, 41, 80, 100, 60, 120, 69, 91, 160] }],
                  }}
                />

                <BookingBooked
                  title="Status"
                  data={_bookingsOverview}
                  sx={{ boxShadow: { md: 'none' } }}
                />
              </Box>

              <BookingCheckInWidgets
                chart={{
                  series: [
                    { label: 'PPoE Users', percent: 73.9, total: 38566 },
                    { label: 'Hotspot Users', percent: 45.6, total: 18472 },
                  ],
                }}
                sx={{ boxShadow: { md: 'none' } }}
              />
            </Box>

            <BookingStatistics
              title="Statistics"
              chart={{
                series: [
                  {
                    name: 'Weekly',
                    categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
                    data: [
                      { name: 'PPoE', data: [24, 41, 35, 151, 49] },
                      { name: 'Hotspot', data: [20, 56, 77, 88, 99] },
                    ],
                  },
                  {
                    name: 'Monthly',
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                    data: [
                      { name: 'PPoE', data: [83, 112, 119, 88, 103, 112, 114, 108, 93] },
                      { name: 'Hotspot', data: [46, 46, 43, 58, 40, 59, 54, 42, 51] },
                    ],
                  },
                  {
                    name: 'Yearly',
                    categories: ['2018', '2019', '2020', '2021', '2022', '2023'],
                    data: [
                      { name: 'PPoE', data: [76, 42, 29, 41, 27, 96] },
                      { name: 'Hotspot', data: [46, 44, 24, 43, 44, 43] },
                    ],
                  },
                ],
              }}
            />
          </Grid>

          <Grid size={{ xs: 12, md: 5, lg: 4 }}>
            <Box sx={{ gap: 3, display: 'flex', flexDirection: 'column' }}>
              <BookingAvailable
                title="Tours available"
                chart={{
                  series: [
                    { label: 'Sold out', value: 120 },
                    { label: 'Available', value: 66 },
                  ],
                }}
              />

              <BookingCustomerReviews
                title="Customer reviews"
                subheader={`${_bookingReview.length} Reviews`}
                list={_bookingReview}
              />
            </Box>
          </Grid>
        </Grid>

        <Grid size={12}>
          <BookingNewest
            title="Newest booking"
            subheader={`${_bookingNew.length} bookings`}
            list={_bookingNew}
          />
        </Grid>

        <Grid size={12}>
          <BookingDetails
            title="Booking details"
            tableData={_bookings}
            headCells={[
              { id: 'destination', label: 'Destination' },
              { id: 'customer', label: 'Customer' },
              { id: 'checkIn', label: 'Check in' },
              { id: 'checkOut', label: 'Check out' },
              { id: 'status', label: 'Status' },
              { id: '' },
            ]}
          />
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
