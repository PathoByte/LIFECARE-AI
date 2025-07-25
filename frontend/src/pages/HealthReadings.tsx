import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  Pagination,
  Alert,
} from '@mui/material';
import {
  Search,
  MonitorHeart,
  Bloodtype,
  ThermostatAuto,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { healthAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';
import LoadingSpinner from '../components/common/LoadingSpinner';

interface HealthReading {
  id: number;
  timestamp: string;
  heart_rate: number;
  blood_oxygen: number;
  temperature?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  activity_level?: string;
  anomaly_score: number;
  is_anomaly: boolean;
}

const HealthReadings: React.FC = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const itemsPerPage = 10;

  const { data: readings, isLoading, error } = useQuery<HealthReading[]>({
    queryKey: ['healthReadings', user?.username, page],
    queryFn: () => healthAPI.getReadings(user!.username, itemsPerPage, (page - 1) * itemsPerPage),
    enabled: !!user,
  });

  const filteredReadings = readings?.filter(reading => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      reading.heart_rate.toString().includes(searchLower) ||
      reading.blood_oxygen.toString().includes(searchLower) ||
      (reading.activity_level && reading.activity_level.toLowerCase().includes(searchLower))
    );
  }) || [];

  const formatDateTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getAnomalyChip = (isAnomaly: boolean, score: number) => {
    if (isAnomaly) {
      return (
        <Chip
          icon={<Warning />}
          label={`Anomaly (${score.toFixed(2)})`}
          color="error"
          size="small"
        />
      );
    }
    return (
      <Chip
        icon={<CheckCircle />}
        label="Normal"
        color="success"
        size="small"
      />
    );
  };

  const getActivityLevelColor = (level?: string) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'info';
      case 'moderate': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading health readings..." />;
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load health readings. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Health Readings
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Recent Measurements
            </Typography>
            <TextField
              size="small"
              placeholder="Search readings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ width: 300 }}
            />
          </Box>

          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date & Time</TableCell>
                  <TableCell align="center">
                    <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                      <MonitorHeart color="error" />
                      Heart Rate
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                      <Bloodtype color="primary" />
                      Blood Oxygen
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                      <ThermostatAuto color="warning" />
                      Temperature
                    </Box>
                  </TableCell>
                  <TableCell align="center">Activity Level</TableCell>
                  <TableCell align="center">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredReadings.map((reading, index) => (
                  <motion.tr
                    key={reading.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    component={TableRow}
                    hover
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {formatDateTime(reading.timestamp)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Typography
                        variant="body1"
                        fontWeight="bold"
                        color={reading.heart_rate > 100 || reading.heart_rate < 60 ? 'error' : 'text.primary'}
                      >
                        {reading.heart_rate} BPM
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Typography
                        variant="body1"
                        fontWeight="bold"
                        color={reading.blood_oxygen < 95 ? 'error' : 'text.primary'}
                      >
                        {reading.blood_oxygen}%
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      {reading.temperature ? (
                        <Typography variant="body1">
                          {reading.temperature.toFixed(1)}°F
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          N/A
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {reading.activity_level ? (
                        <Chip
                          label={reading.activity_level.charAt(0).toUpperCase() + reading.activity_level.slice(1)}
                          color={getActivityLevelColor(reading.activity_level) as any}
                          size="small"
                        />
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          N/A
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {getAnomalyChip(reading.is_anomaly, reading.anomaly_score)}
                    </TableCell>
                  </motion.tr>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {filteredReadings.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography variant="body1" color="text.secondary">
                No health readings found.
              </Typography>
            </Box>
          )}

          {readings && readings.length > itemsPerPage && (
            <Box display="flex" justifyContent="center" mt={3}>
              <Pagination
                count={Math.ceil(readings.length / itemsPerPage)}
                page={page}
                onChange={(_, newPage) => setPage(newPage)}
                color="primary"
              />
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default HealthReadings;