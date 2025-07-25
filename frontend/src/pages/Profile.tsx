import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Avatar,
  Divider,
  MenuItem,
  Alert,
} from '@mui/material';
import {
  Person,
  Edit,
  Save,
  Cancel,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

const Profile: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    age: user?.age?.toString() || '',
    gender: user?.gender || '',
    medical_conditions: user?.medical_conditions || '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const updateData = {
        full_name: formData.full_name,
        age: formData.age ? parseInt(formData.age) : undefined,
        gender: formData.gender || undefined,
        medical_conditions: formData.medical_conditions || undefined,
      };

      const success = await updateUser(updateData);
      if (success) {
        setEditing(false);
      }
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      full_name: user?.full_name || '',
      age: user?.age?.toString() || '',
      gender: user?.gender || '',
      medical_conditions: user?.medical_conditions || '',
    });
    setEditing(false);
  };

  if (!user) {
    return (
      <Alert severity="error">
        User information not available.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Profile Settings
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <Avatar
                  sx={{
                    width: 120,
                    height: 120,
                    mx: 'auto',
                    mb: 2,
                    bgcolor: 'primary.main',
                    fontSize: '3rem',
                  }}
                >
                  {user.full_name.charAt(0).toUpperCase()}
                </Avatar>
                <Typography variant="h5" fontWeight="bold" gutterBottom>
                  {user.full_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  @{user.username}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {user.email}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Member since {new Date(user.created_at).toLocaleDateString()}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                  <Typography variant="h6">
                    Personal Information
                  </Typography>
                  {!editing ? (
                    <Button
                      startIcon={<Edit />}
                      onClick={() => setEditing(true)}
                      variant="outlined"
                    >
                      Edit Profile
                    </Button>
                  ) : (
                    <Box display="flex" gap={1}>
                      <Button
                        startIcon={<Cancel />}
                        onClick={handleCancel}
                        variant="outlined"
                        color="inherit"
                      >
                        Cancel
                      </Button>
                      <Button
                        startIcon={<Save />}
                        onClick={handleSave}
                        variant="contained"
                        disabled={loading}
                      >
                        {loading ? 'Saving...' : 'Save Changes'}
                      </Button>
                    </Box>
                  )}
                </Box>

                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Full Name"
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                      disabled={!editing}
                      variant={editing ? 'outlined' : 'filled'}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Username"
                      value={user.username}
                      disabled
                      variant="filled"
                      helperText="Username cannot be changed"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      value={user.email}
                      disabled
                      variant="filled"
                      helperText="Email cannot be changed"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Age"
                      name="age"
                      type="number"
                      value={formData.age}
                      onChange={handleChange}
                      disabled={!editing}
                      variant={editing ? 'outlined' : 'filled'}
                      inputProps={{ min: 1, max: 150 }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Gender"
                      name="gender"
                      select
                      value={formData.gender}
                      onChange={handleChange}
                      disabled={!editing}
                      variant={editing ? 'outlined' : 'filled'}
                    >
                      <MenuItem value="">Select Gender</MenuItem>
                      <MenuItem value="male">Male</MenuItem>
                      <MenuItem value="female">Female</MenuItem>
                      <MenuItem value="other">Other</MenuItem>
                    </TextField>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Account Status"
                      value={user.is_active ? 'Active' : 'Inactive'}
                      disabled
                      variant="filled"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Medical Conditions"
                      name="medical_conditions"
                      multiline
                      rows={4}
                      value={formData.medical_conditions}
                      onChange={handleChange}
                      disabled={!editing}
                      variant={editing ? 'outlined' : 'filled'}
                      placeholder="Any existing medical conditions, medications, or health notes..."
                      helperText="This information helps provide better health recommendations"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Profile;