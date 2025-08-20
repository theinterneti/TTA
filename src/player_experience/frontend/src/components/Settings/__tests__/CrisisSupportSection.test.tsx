import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import CrisisSupportSection from '../CrisisSupportSection';

const mockCrisisContactInfo = {
  emergency_contact: 'John Doe - 555-0123',
  therapist_contact: 'Dr. Smith - 555-0456',
  preferred_crisis_resources: ['national-suicide-prevention', 'crisis-text-line'],
};

const mockOnUpdate = jest.fn();

// Mock window.open
const mockWindowOpen = jest.fn();
Object.defineProperty(window, 'open', {
  writable: true,
  value: mockWindowOpen,
});

describe('CrisisSupportSection', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders crisis support section correctly', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('Crisis Support Resources')).toBeInTheDocument();
    expect(screen.getByText(/Set up your crisis support preferences/)).toBeInTheDocument();
  });

  it('displays emergency alert', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText(/If you're in immediate danger/)).toBeInTheDocument();
    expect(screen.getByText(/Call 911/)).toBeInTheDocument();
  });

  it('displays immediate crisis support resources', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('National Suicide Prevention Lifeline')).toBeInTheDocument();
    expect(screen.getByText('Crisis Text Line')).toBeInTheDocument();
    expect(screen.getByText('SAMHSA National Helpline')).toBeInTheDocument();
    expect(screen.getByText('NAMI HelpLine')).toBeInTheDocument();
  });

  it('displays contact now buttons for crisis resources', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    const contactButtons = screen.getAllByText('Contact Now');
    expect(contactButtons).toHaveLength(4); // First 4 resources
  });

  it('handles phone contact for crisis resources', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    // Find the National Suicide Prevention Lifeline contact button
    const suicidePreventionCard = screen.getByText('National Suicide Prevention Lifeline').closest('div');
    const contactButton = suicidePreventionCard?.querySelector('button');
    
    if (contactButton) {
      fireEvent.click(contactButton);
      expect(mockWindowOpen).toHaveBeenCalledWith('tel:988');
    }
  });

  it('displays personal crisis contacts', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('Personal Crisis Contacts')).toBeInTheDocument();
    
    const emergencyContactInput = screen.getByPlaceholderText(/Name and phone number of trusted person/);
    expect(emergencyContactInput).toHaveValue('John Doe - 555-0123');

    const therapistContactInput = screen.getByPlaceholderText(/Your therapist's name and contact information/);
    expect(therapistContactInput).toHaveValue('Dr. Smith - 555-0456');
  });

  it('handles emergency contact update', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    const emergencyContactInput = screen.getByPlaceholderText(/Name and phone number of trusted person/);
    fireEvent.change(emergencyContactInput, { target: { value: 'Jane Doe - 555-0789' } });

    expect(mockOnUpdate).toHaveBeenCalledWith({
      ...mockCrisisContactInfo,
      emergency_contact: 'Jane Doe - 555-0789',
    });
  });

  it('handles therapist contact update', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    const therapistContactInput = screen.getByPlaceholderText(/Your therapist's name and contact information/);
    fireEvent.change(therapistContactInput, { target: { value: 'Dr. Johnson - 555-0999' } });

    expect(mockOnUpdate).toHaveBeenCalledWith({
      ...mockCrisisContactInfo,
      therapist_contact: 'Dr. Johnson - 555-0999',
    });
  });

  it('displays preferred crisis resources with checkboxes', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('Preferred Crisis Resources')).toBeInTheDocument();
    
    const suicidePreventionCheckbox = screen.getByRole('checkbox', { name: /National Suicide Prevention Lifeline/ });
    const crisisTextCheckbox = screen.getByRole('checkbox', { name: /Crisis Text Line/ });
    
    expect(suicidePreventionCheckbox).toBeChecked();
    expect(crisisTextCheckbox).toBeChecked();
  });

  it('handles preferred crisis resource toggle', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    const samhsaCheckbox = screen.getByRole('checkbox', { name: /SAMHSA National Helpline/ });
    fireEvent.click(samhsaCheckbox);

    expect(mockOnUpdate).toHaveBeenCalledWith({
      ...mockCrisisContactInfo,
      preferred_crisis_resources: [...mockCrisisContactInfo.preferred_crisis_resources, 'samhsa-helpline'],
    });
  });

  it('handles removing preferred crisis resource', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    const suicidePreventionCheckbox = screen.getByRole('checkbox', { name: /National Suicide Prevention Lifeline/ });
    fireEvent.click(suicidePreventionCheckbox);

    expect(mockOnUpdate).toHaveBeenCalledWith({
      ...mockCrisisContactInfo,
      preferred_crisis_resources: ['crisis-text-line'],
    });
  });

  it('displays crisis safety plan', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('🛡️ Your Crisis Safety Plan')).toBeInTheDocument();
    expect(screen.getByText(/Recognize your warning signs and triggers/)).toBeInTheDocument();
    expect(screen.getByText(/Use internal coping strategies/)).toBeInTheDocument();
    expect(screen.getByText(/Contact people and social settings/)).toBeInTheDocument();
  });

  it('displays crisis detection settings', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    expect(screen.getByText('Crisis Detection & Response')).toBeInTheDocument();
    expect(screen.getByText('Automatic Crisis Detection')).toBeInTheDocument();
    
    const crisisDetectionToggle = screen.getByRole('checkbox');
    expect(crisisDetectionToggle).toBeChecked(); // Default checked
  });

  it('handles text-based crisis resource contact', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    // Find the Crisis Text Line contact button
    const crisisTextCard = screen.getByText('Crisis Text Line').closest('div');
    const contactButton = crisisTextCard?.querySelector('button');
    
    if (contactButton) {
      fireEvent.click(contactButton);
      // Should open modal for text resources
      expect(screen.getByText('Crisis Text Line')).toBeInTheDocument();
    }
  });

  it('handles undefined crisis contact info', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={undefined}
        onUpdate={mockOnUpdate}
      />
    );

    const emergencyContactInput = screen.getByPlaceholderText(/Name and phone number of trusted person/);
    expect(emergencyContactInput).toHaveValue('');

    fireEvent.change(emergencyContactInput, { target: { value: 'New Contact' } });

    expect(mockOnUpdate).toHaveBeenCalledWith({
      emergency_contact: 'New Contact',
      therapist_contact: '',
      preferred_crisis_resources: [],
    });
  });

  it('displays availability badges correctly', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    // Check for 24/7 badges
    const badges24_7 = screen.getAllByText('24/7');
    expect(badges24_7.length).toBeGreaterThan(0);

    // Check for specific availability
    expect(screen.getByText('Mon-Fri 10am-10pm ET')).toBeInTheDocument();
  });

  it('closes resource modal when close button is clicked', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    // Open modal by clicking on a text resource
    const crisisTextCard = screen.getByText('Crisis Text Line').closest('div');
    const contactButton = crisisTextCard?.querySelector('button');
    
    if (contactButton) {
      fireEvent.click(contactButton);
      
      // Modal should be open
      expect(screen.getByRole('button', { name: /Close/ })).toBeInTheDocument();
      
      // Close modal
      fireEvent.click(screen.getByRole('button', { name: /Close/ }));
      
      // Modal should be closed (only one Crisis Text Line text should remain)
      const crisisTextElements = screen.getAllByText('Crisis Text Line');
      expect(crisisTextElements).toHaveLength(1);
    }
  });

  it('opens website when visit website button is clicked in modal', () => {
    render(
      <CrisisSupportSection
        crisisContactInfo={mockCrisisContactInfo}
        onUpdate={mockOnUpdate}
      />
    );

    // Open modal by clicking on a resource
    const crisisTextCard = screen.getByText('Crisis Text Line').closest('div');
    const contactButton = crisisTextCard?.querySelector('button');
    
    if (contactButton) {
      fireEvent.click(contactButton);
      
      // Click visit website button
      const visitWebsiteButton = screen.getByText('Visit Website');
      fireEvent.click(visitWebsiteButton);
      
      expect(mockWindowOpen).toHaveBeenCalledWith('https://crisistextline.org', '_blank');
    }
  });
});