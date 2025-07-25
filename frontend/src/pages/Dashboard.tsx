import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  DialogActions,
  Alert,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  MonitorHeart,
  Bloodtype,
  ThermostatAuto,
  Add,
  TrendingUp,
  Warning,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { healthAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/common/LoadingSpinner';

interface HealthReading {
  id: number;
  timestamp: string;
  heart_rate: number;
  blood_oxygen: number;
  temperature?: number;
  is_anomaly: boolean;
  anomaly_score: number;
}

interface DashboardData {
  recent_readings: HealthReading[];
  metrics: {
    avg_heart_rate: number;
    avg_blood_oxygen: number;
    anomaly_count: number;
    total_readings: number;
    last_reading_time?: string;
  };
  alerts: any[];
  anomaly_trend: any[];
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [openDialog, setOpenDialog] = useState(false);
  const [newReading, setNewReading] = useState({
    heart_rate: '',
    blood_oxygen: '',
    temperature: '',
  });

  const { data: dashboardData, isLoading, error } = useQuery<DashboardData>({
    queryKey: ['dashboard', user?.username],
    queryFn: () => healthAPI.getDashboardData(user!.username),
    enabled: !!user,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const createReadingMutation = useMutation({
    mutationFn: (reading: any) => healthAPI.createReading({
      ...reading,
      user_id: user!.username,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setOpenDialog(false);
      setNewReading({ heart_rate: '', blood_oxygen: '', temperature: '' });
      toast.success('Health reading added successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to add reading');
    },
  });

  const handleAddReading = () => {
    const reading = {
      heart_rate: parseFloat(newReading.heart_rate),
      blood_oxygen: parseFloat(newReading.blood_oxygen),
      temperature: newReading.temperature ? parseFloat(newReading.temperature) : undefined,
    };

    if (reading.heart_rate < 30 || reading.heart_rate > 220) {
      toast.error('Heart rate must be between 30-220 BPM');
      return;
    }

    if (reading.blood_oxygen < 70 || reading.blood_oxygen > 100) {
      toast.error('Blood oxygen must be between 70-100%');
      return;
    }

    createReadingMutation.mutate(reading);
  };

  const formatChartData = (readings: HealthReading[]) => {
    return readings.slice(-20).map(reading => ({
      time: new Date(reading.timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      heart_rate: reading.heart_rate,
      blood_oxygen: reading.blood_oxygen,
      is_anomaly: reading.is_anomaly,
    }));
  };

  const getHealthStatus = (metrics: any) => {
    if (metrics.anomaly_count > metrics.total_readings * 0.3) {
      return { status: 'Critical', color: 'error', icon: <Warning /> };
    } else if (metrics.anomaly_count > 0) {
      return { status: 'Attention Needed', color: 'warning', icon: <Warning /> };
    } else {
      return { status: 'Good', color: 'success', icon: <TrendingUp /> };
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load dashboard data. Please try again.
      </Alert>
    );
  }

  const chartData = dashboardData ? formatChartData(dashboardData.recent_readings) : [];
  const healthStatus = dashboardData ? getHealthStatus(dashboardData.metrics) : null;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Health Dashboard
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
          sx={{ borderRadius: 2 }}
        >
          Add Reading
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <MonitorHeart sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {dashboardData?.metrics.avg_heart_rate.toFixed(0) || 0}
                    </Typography>
                    <Typography variant="body2" opacity={0.8}>
                      Avg Heart Rate (BPM)
                    </Typography>
                  </Box>
                </Box>
                {healthStatus && (
                  <Chip
                    icon={healthStatus.icon}
                    label={healthStatus.status}
                    color={healthStatus.color as any}
                    size="small"
                    sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }}
                  />
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Bloodtype color="error" sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {dashboardData?.metrics.avg_blood_oxygen.toFixed(1) || 0}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Blood Oxygen
                    </Typography>
                  </Box>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={dashboardData?.metrics.avg_blood_oxygen || 0}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Warning color="warning" sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {dashboardData?.metrics.anomaly_count || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Anomalies Detected
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Out of {dashboardData?.metrics.total_readings || 0} readings
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <TrendingUp color="success" sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {dashboardData?.metrics.total_readings || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Readings
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Last 7 days
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Charts */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Vital Signs Trend
                </Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="heart_rate"
                        stroke="#f44336"
                        strokeWidth={2}
                        name="Heart Rate (BPM)"
                      />
                      <Line
                        type="monotone"
                        dataKey="blood_oxygen"
                        stroke="#2196f3"
                        strokeWidth={2}
                        name="Blood Oxygen (%)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Anomaly Trend
                </Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={dashboardData?.anomaly_trend || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
                      <YAxis />
                      <Tooltip labelFormatter={(date) => new Date(date).toLocaleDateString()} />
                      <Area
                        type="monotone"
                        dataKey="anomaly_count"
                        stroke="#ff9800"
                        fill="#ff9800"
                        fillOpacity={0.3}
                        name="Anomalies"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recent Alerts */}
        {dashboardData?.alerts && dashboardData.alerts.length > 0 && (
          <Grid item xs={12}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Alerts
                  </Typography>
                  {dashboardData.alerts.slice(0, 3).map((alert, index) => (
                    <Alert
                      key={alert.id}
                      severity={alert.severity === 'high' ? 'error' : 'warning'}
                      sx={{ mb: 1 }}
                    >
                      {alert.message}
                    </Alert>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        )}
      </Grid>

      {/* Add Reading Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Health Reading</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Heart Rate (BPM)"
            type="number"
            value={newReading.heart_rate}
            onChange={(e) => setNewReading({ ...newReading, heart_rate: e.target.value })}
            margin="normal"
            inputProps={{ min: 30, max: 220 }}
            required
          />
          <TextField
            fullWidth
            label="Blood Oxygen (%)"
            type="number"
            value={newReading.blood_oxygen}
            onChange={(e) => setNewReading({ ...newReading, blood_oxygen: e.target.value })}
            margin="normal"
            inputProps={{ min: 70, max: 100, step: 0.1 }}
            required
          />
          <TextField
            fullWidth
            label="Temperature (°F) - Optional"
            type="number"
            value={newReading.temperature}
            onChange={(e) => setNewReading({ ...newReading, temperature: e.target.value })}
            margin="normal"
            inputProps={{ min: 95, max: 110, step: 0.1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleAddReading}
            variant="contained"
            disabled={createReadingMutation.isPending || !newReading.heart_rate || !newReading.blood_oxygen}
          >
            {createReadingMutation.isPending ? 'Adding...' : 'Add Reading'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard;