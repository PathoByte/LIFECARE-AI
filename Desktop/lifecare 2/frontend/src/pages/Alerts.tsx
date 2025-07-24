import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Alert as MuiAlert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  Delete,
  MarkEmailRead,
  Notifications,
  NotificationsOff,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/common/LoadingSpinner';

interface Alert {
  id: number;
  user_id: string;
  alert_type: string;
  message: string;
  severity: string;
  is_read: boolean;
  created_at: string;
}

const Alerts: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; alertId?: number }>({
    open: false,
  });

  const { data: allAlerts, isLoading, error } = useQuery<Alert[]>({
    queryKey: ['alerts', user?.username],
    queryFn: () => alertsAPI.getAlerts(user!.username),
    enabled: !!user,
  });

  const markAsReadMutation = useMutation({
    mutationFn: (alertId: number) => alertsAPI.markAsRead(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alert marked as read');
    },
    onError: () => {
      toast.error('Failed to mark alert as read');
    },
  });

  const deleteAlertMutation = useMutation({
    mutationFn: (alertId: number) => alertsAPI.deleteAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      setDeleteDialog({ open: false });
      toast.success('Alert deleted');
    },
    onError: () => {
      toast.error('Failed to delete alert');
    },
  });

  const getAlertIcon = (type: string, severity: string) => {
    switch (severity) {
      case 'critical':
        return <Error color="error" />;
      case 'high':
        return <Warning color="error" />;
      case 'medium':
        return <Warning color="warning" />;
      case 'low':
        return <Info color="info" />;
      default:
        return <Notifications color="primary" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatDateTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const filteredAlerts = allAlerts?.filter(alert => {
    if (tabValue === 0) return true; // All alerts
    if (tabValue === 1) return !alert.is_read; // Unread alerts
    if (tabValue === 2) return alert.is_read; // Read alerts
    return true;
  }) || [];

  const unreadCount = allAlerts?.filter(alert => !alert.is_read).length || 0;

  if (isLoading) {
    return <LoadingSpinner message="Loading alerts..." />;
  }

  if (error) {
    return (
      <MuiAlert severity="error">
        Failed to load alerts. Please try again.
      </MuiAlert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Alerts & Notifications
        </Typography>
        {unreadCount > 0 && (
          <Chip
            icon={<Notifications />}
            label={`${unreadCount} unread`}
            color="error"
            variant="outlined"
          />
        )}
      </Box>

      <Card>
        <CardContent>
          <Tabs
            value={tabValue}
            onChange={(_, newValue) => setTabValue(newValue)}
            sx={{ mb: 3 }}
          >
            <Tab label={`All (${allAlerts?.length || 0})`} />
            <Tab label={`Unread (${unreadCount})`} />
            <Tab label={`Read (${(allAlerts?.length || 0) - unreadCount})`} />
          </Tabs>

          {filteredAlerts.length === 0 ? (
            <Box textAlign="center" py={6}>
              <NotificationsOff sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No alerts found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {tabValue === 1 ? 'All alerts have been read' : 'You have no alerts at this time'}
              </Typography>
            </Box>
          ) : (
            <List>
              {filteredAlerts.map((alert, index) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <ListItem
                    sx={{
                      border: '1px solid',
                      borderColor: alert.is_read ? 'divider' : 'primary.main',
                      borderRadius: 2,
                      mb: 2,
                      backgroundColor: alert.is_read ? 'background.paper' : 'primary.50',
                      '&:hover': {
                        backgroundColor: alert.is_read ? 'action.hover' : 'primary.100',
                      },
                    }}
                  >
                    <ListItemIcon>
                      {getAlertIcon(alert.alert_type, alert.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                          <Typography
                            variant="body1"
                            fontWeight={alert.is_read ? 'normal' : 'bold'}
                          >
                            {alert.message}
                          </Typography>
                          <Chip
                            label={alert.severity.toUpperCase()}
                            color={getSeverityColor(alert.severity) as any}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {formatDateTime(alert.created_at)}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Type: {alert.alert_type}
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Box display="flex" gap={1}>
                        {!alert.is_read && (
                          <IconButton
                            edge="end"
                            onClick={() => markAsReadMutation.mutate(alert.id)}
                            disabled={markAsReadMutation.isPending}
                            title="Mark as read"
                          >
                            <MarkEmailRead />
                          </IconButton>
                        )}
                        <IconButton
                          edge="end"
                          onClick={() => setDeleteDialog({ open: true, alertId: alert.id })}
                          title="Delete alert"
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                </motion.div>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false })}
      >
        <DialogTitle>Delete Alert</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this alert? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false })}>
            Cancel
          </Button>
          <Button
            onClick={() => deleteAlertMutation.mutate(deleteDialog.alertId!)}
            color="error"
            disabled={deleteAlertMutation.isPending}
          >
            {deleteAlertMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Alerts;