import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import TherapeuticSettingsSection from '../TherapeuticSettingsSection';

const mockSettings = {
  intensity_level: 'MEDIUM' as const,
  preferred_approaches: ['Cognitive Behavioral Therapy (CBT)', 'Mindfulness-Based Therapy'],
  trigger_warnings: ['violence', 'loss'],
  comfort_topics: ['nature', 'creativity'],
  avoid_topics: ['family conflicts'],
};

const mockOnUpdate = jest.fn();

describe('TherapeuticSettingsSection', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders therapeutic settings correctly', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('Therapeutic Preferences')).toBeInTheDocument();
    expect(screen.getByText('Therapeutic Intensity Level')).toBeInTheDocument();
    expect(screen.getByText('Preferred Therapeutic Approaches')).toBeInTheDocument();
  });

  it('displays current intensity level', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const mediumButton = screen.getByRole('button', { name: /MEDIUM.*Balanced therapeutic approach/ });
    expect(mediumButton).toHaveClass('border-primary-500');
  });

  it('handles intensity level change', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const highButton = screen.getByRole('button', { name: /HIGH.*Intensive therapeutic work/ });
    fireEvent.click(highButton);

    expect(mockOnUpdate).toHaveBeenCalledWith({ intensity_level: 'HIGH' });
  });

  it('displays selected therapeutic approaches', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const cbtCheckbox = screen.getByRole('checkbox', { name: /Cognitive Behavioral Therapy/ });
    const mindfulnessCheckbox = screen.getByRole('checkbox', { name: /Mindfulness-Based Therapy/ });
    
    expect(cbtCheckbox).toBeChecked();
    expect(mindfulnessCheckbox).toBeChecked();
  });

  it('handles therapeutic approach toggle', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const narrativeTherapyCheckbox = screen.getByRole('checkbox', { name: /Narrative Therapy/ });
    fireEvent.click(narrativeTherapyCheckbox);

    expect(mockOnUpdate).toHaveBeenCalledWith({
      preferred_approaches: [...mockSettings.preferred_approaches, 'Narrative Therapy']
    });
  });

  it('handles removing therapeutic approach', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const cbtCheckbox = screen.getByRole('checkbox', { name: /Cognitive Behavioral Therapy/ });
    fireEvent.click(cbtCheckbox);

    expect(mockOnUpdate).toHaveBeenCalledWith({
      preferred_approaches: ['Mindfulness-Based Therapy']
    });
  });

  it('shows custom approach input when add custom is clicked', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const addCustomButton = screen.getByText('Add custom approach');
    fireEvent.click(addCustomButton);

    expect(screen.getByPlaceholderText('Enter custom therapeutic approach...')).toBeInTheDocument();
    expect(screen.getByText('Add')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('handles adding custom therapeutic approach', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const addCustomButton = screen.getByText('Add custom approach');
    fireEvent.click(addCustomButton);

    const input = screen.getByPlaceholderText('Enter custom therapeutic approach...');
    fireEvent.change(input, { target: { value: 'Art Therapy' } });

    const addButton = screen.getByText('Add');
    fireEvent.click(addButton);

    expect(mockOnUpdate).toHaveBeenCalledWith({
      preferred_approaches: [...mockSettings.preferred_approaches, 'Art Therapy']
    });
  });

  it('handles adding custom approach with Enter key', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const addCustomButton = screen.getByText('Add custom approach');
    fireEvent.click(addCustomButton);

    const input = screen.getByPlaceholderText('Enter custom therapeutic approach...');
    fireEvent.change(input, { target: { value: 'Music Therapy' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });

    expect(mockOnUpdate).toHaveBeenCalledWith({
      preferred_approaches: [...mockSettings.preferred_approaches, 'Music Therapy']
    });
  });

  it('cancels custom approach input', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const addCustomButton = screen.getByText('Add custom approach');
    fireEvent.click(addCustomButton);

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    expect(screen.queryByPlaceholderText('Enter custom therapeutic approach...')).not.toBeInTheDocument();
    expect(screen.getByText('Add custom approach')).toBeInTheDocument();
  });

  it('displays and handles trigger warnings', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const triggerWarningsTextarea = screen.getByPlaceholderText(/e.g., violence, loss/);
    expect(triggerWarningsTextarea).toHaveValue('violence, loss');

    fireEvent.change(triggerWarningsTextarea, { target: { value: 'violence, loss, trauma' } });

    expect(mockOnUpdate).toHaveBeenCalledWith({
      trigger_warnings: ['violence', 'loss', 'trauma']
    });
  });

  it('displays and handles comfort topics', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const comfortTopicsTextarea = screen.getByPlaceholderText(/e.g., nature, creativity/);
    expect(comfortTopicsTextarea).toHaveValue('nature, creativity');

    fireEvent.change(comfortTopicsTextarea, { target: { value: 'nature, creativity, music' } });

    expect(mockOnUpdate).toHaveBeenCalledWith({
      comfort_topics: ['nature', 'creativity', 'music']
    });
  });

  it('displays and handles topics to avoid', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const avoidTopicsTextarea = screen.getByPlaceholderText(/e.g., specific phobias/);
    expect(avoidTopicsTextarea).toHaveValue('family conflicts');

    fireEvent.change(avoidTopicsTextarea, { target: { value: 'family conflicts, work stress' } });

    expect(mockOnUpdate).toHaveBeenCalledWith({
      avoid_topics: ['family conflicts', 'work stress']
    });
  });

  it('handles empty topic lists correctly', () => {
    const emptySettings = {
      ...mockSettings,
      trigger_warnings: [],
      comfort_topics: [],
      avoid_topics: [],
    };

    render(
      <TherapeuticSettingsSection
        settings={emptySettings}
        onUpdate={mockOnUpdate}
      />
    );

    const triggerWarningsTextarea = screen.getByPlaceholderText(/e.g., violence, loss/);
    expect(triggerWarningsTextarea).toHaveValue('');

    fireEvent.change(triggerWarningsTextarea, { target: { value: 'new topic' } });

    expect(mockOnUpdate).toHaveBeenCalledWith({
      trigger_warnings: ['new topic']
    });
  });

  it('filters out empty topics when parsing comma-separated values', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const triggerWarningsTextarea = screen.getByPlaceholderText(/e.g., violence, loss/);
    fireEvent.change(triggerWarningsTextarea, { target: { value: 'topic1, , topic2,  , topic3' } });

    expect(mockOnUpdate).toHaveBeenCalledWith({
      trigger_warnings: ['topic1', 'topic2', 'topic3']
    });
  });

  it('displays therapeutic goals tip', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('💡 Therapeutic Goals Tip')).toBeInTheDocument();
    expect(screen.getByText(/Your therapeutic preferences will be used to personalize/)).toBeInTheDocument();
  });

  it('shows custom approaches with remove buttons', () => {
    const settingsWithCustom = {
      ...mockSettings,
      preferred_approaches: [...mockSettings.preferred_approaches, 'Custom Art Therapy'],
    };

    render(
      <TherapeuticSettingsSection
        settings={settingsWithCustom}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('Custom Art Therapy')).toBeInTheDocument();
    
    // Find the remove button for the custom approach
    const customApproachContainer = screen.getByText('Custom Art Therapy').closest('div');
    const removeButton = customApproachContainer?.querySelector('button');
    
    if (removeButton) {
      fireEvent.click(removeButton);
      expect(mockOnUpdate).toHaveBeenCalledWith({
        preferred_approaches: mockSettings.preferred_approaches
      });
    }
  });

  it('prevents adding duplicate custom approaches', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const addCustomButton = screen.getByText('Add custom approach');
    fireEvent.click(addCustomButton);

    const input = screen.getByPlaceholderText('Enter custom therapeutic approach...');
    fireEvent.change(input, { target: { value: 'Cognitive Behavioral Therapy (CBT)' } });

    const addButton = screen.getByText('Add');
    fireEvent.click(addButton);

    // Should not call onUpdate since it's a duplicate
    expect(mockOnUpdate).not.toHaveBeenCalled();
  });

  it('prevents adding empty custom approaches', () => {
    render(
      <TherapeuticSettingsSection
        settings={mockSettings}
        onUpdate={mockOnUpdate}
      />
    );

    const addCustomButton = screen.getByText('Add custom approach');
    fireEvent.click(addCustomButton);

    const input = screen.getByPlaceholderText('Enter custom therapeutic approach...');
    fireEvent.change(input, { target: { value: '   ' } }); // Only whitespace

    const addButton = screen.getByText('Add');
    fireEvent.click(addButton);

    // Should not call onUpdate since it's empty
    expect(mockOnUpdate).not.toHaveBeenCalled();
  });
});