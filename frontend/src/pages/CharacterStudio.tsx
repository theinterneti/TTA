/**
 * TTA Character Studio Component
 *
 * Provides character creation and management functionality.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Avatar,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Person,
  Psychology,
  AutoStories,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store/store';

interface Character {
  id: string;
  name: string;
  description: string;
  archetype: string;
  traits: string[];
  backstory: string;
  therapeuticGoals: string[];
  createdAt: string;
}

const CharacterStudio: React.FC = () => {
  const dispatch = useDispatch();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    archetype: '',
    traits: '',
    backstory: '',
    therapeuticGoals: '',
  });

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    try {
      setIsLoading(true);
      // In a real app, this would fetch from the API
      // For now, we'll use mock data
      const mockCharacters: Character[] = [
        {
          id: '1',
          name: 'Alex the Explorer',
          description: 'A curious adventurer who helps players discover new perspectives',
          archetype: 'Explorer',
          traits: ['Curious', 'Brave', 'Empathetic'],
          backstory: 'Alex grew up in a small town but always dreamed of seeing the world...',
          therapeuticGoals: ['Build confidence', 'Encourage exploration'],
          createdAt: new Date().toISOString(),
        },
      ];
      setCharacters(mockCharacters);
    } catch (error: any) {
      setError('Failed to load characters');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateCharacter = () => {
    setFormData({
      name: '',
      description: '',
      archetype: '',
      traits: '',
      backstory: '',
      therapeuticGoals: '',
    });
    setIsCreateDialogOpen(true);
  };

  const handleEditCharacter = (character: Character) => {
    setSelectedCharacter(character);
    setFormData({
      name: character.name,
      description: character.description,
      archetype: character.archetype,
      traits: character.traits.join(', '),
      backstory: character.backstory,
      therapeuticGoals: character.therapeuticGoals.join(', '),
    });
    setIsEditDialogOpen(true);
  };

  const handleSaveCharacter = async () => {
    try {
      const characterData = {
        ...formData,
        traits: formData.traits.split(',').map(t => t.trim()).filter(t => t),
        therapeuticGoals: formData.therapeuticGoals.split(',').map(g => g.trim()).filter(g => g),
      };

      if (selectedCharacter) {
        // Update existing character
        const updatedCharacter = {
          ...selectedCharacter,
          ...characterData,
        };
        setCharacters(prev => prev.map(c => c.id === selectedCharacter.id ? updatedCharacter : c));
        setIsEditDialogOpen(false);
      } else {
        // Create new character
        const newCharacter: Character = {
          id: Date.now().toString(),
          ...characterData,
          createdAt: new Date().toISOString(),
        };
        setCharacters(prev => [...prev, newCharacter]);
        setIsCreateDialogOpen(false);
      }

      setSelectedCharacter(null);
    } catch (error: any) {
      setError('Failed to save character');
    }
  };

  const handleDeleteCharacter = async (characterId: string) => {
    if (window.confirm('Are you sure you want to delete this character?')) {
      try {
        setCharacters(prev => prev.filter(c => c.id !== characterId));
      } catch (error: any) {
        setError('Failed to delete character');
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const archetypes = [
    'Explorer',
    'Mentor',
    'Companion',
    'Guardian',
    'Healer',
    'Challenger',
    'Storyteller',
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Character Studio
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Create and manage therapeutic characters for your gaming experiences
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreateCharacter}
          sx={{ mb: 3 }}
        >
          Create New Character
        </Button>
      </Box>

      <Grid container spacing={3}>
        {characters.map((character) => (
          <Grid item xs={12} md={6} lg={4} key={character.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                    <Person />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" component="h2">
                      {character.name}
                    </Typography>
                    <Chip
                      label={character.archetype}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {character.description}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Traits:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {character.traits.map((trait, index) => (
                      <Chip key={index} label={trait} size="small" />
                    ))}
                  </Box>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Therapeutic Goals:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {character.therapeuticGoals.map((goal, index) => (
                      <Chip key={index} label={goal} size="small" color="secondary" />
                    ))}
                  </Box>
                </Box>
              </CardContent>

              <Box sx={{ p: 2, pt: 0 }}>
                <Button
                  startIcon={<Edit />}
                  onClick={() => handleEditCharacter(character)}
                  sx={{ mr: 1 }}
                >
                  Edit
                </Button>
                <Button
                  startIcon={<Delete />}
                  color="error"
                  onClick={() => handleDeleteCharacter(character.id)}
                >
                  Delete
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create/Edit Character Dialog */}
      <Dialog
        open={isCreateDialogOpen || isEditDialogOpen}
        onClose={() => {
          setIsCreateDialogOpen(false);
          setIsEditDialogOpen(false);
          setSelectedCharacter(null);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedCharacter ? 'Edit Character' : 'Create New Character'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Character Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              multiline
              rows={3}
              sx={{ mb: 2 }}
            />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Archetype</InputLabel>
              <Select
                name="archetype"
                value={formData.archetype}
                onChange={(e) => setFormData(prev => ({ ...prev, archetype: e.target.value }))}
                label="Archetype"
              >
                {archetypes.map((archetype) => (
                  <MenuItem key={archetype} value={archetype}>
                    {archetype}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Traits (comma-separated)"
              name="traits"
              value={formData.traits}
              onChange={handleInputChange}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Backstory"
              name="backstory"
              value={formData.backstory}
              onChange={handleInputChange}
              multiline
              rows={4}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Therapeutic Goals (comma-separated)"
              name="therapeuticGoals"
              value={formData.therapeuticGoals}
              onChange={handleInputChange}
              sx={{ mb: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setIsCreateDialogOpen(false);
              setIsEditDialogOpen(false);
              setSelectedCharacter(null);
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleSaveCharacter} variant="contained">
            {selectedCharacter ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CharacterStudio;
