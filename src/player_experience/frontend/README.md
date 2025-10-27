# TTA Player Experience Frontend

This is the React frontend application for the TTA (Therapeutic Text Adventure) Player Experience Interface.

## Features

- **Character Management**: Create and manage therapeutic adventure characters
- **World Selection**: Browse and select therapeutic environments
- **Real-time Chat**: WebSocket-based therapeutic chat interface
- **Settings Management**: Control therapeutic preferences and privacy settings
- **Progress Tracking**: Monitor therapeutic progress and achievements
- **Responsive Design**: Mobile-friendly interface with accessibility support

## Technology Stack

- **React 18** with TypeScript
- **Redux Toolkit** for state management
- **React Router** for navigation
- **Tailwind CSS** for styling
- **Socket.IO Client** for real-time communication
- **Jest & React Testing Library** for testing

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd src/player_experience/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will open at `http://localhost:3000`.

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (not recommended)

## Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Layout/         # Layout components (Header, Sidebar)
├── pages/              # Page components
│   ├── Auth/           # Authentication pages
│   ├── Dashboard/      # Dashboard page
│   ├── CharacterManagement/  # Character management
│   ├── WorldSelection/       # World selection
│   ├── Settings/       # Settings page
│   └── Chat/           # Chat interface
├── store/              # Redux store and slices
│   └── slices/         # Redux slices
├── services/           # API and WebSocket services
├── types/              # TypeScript type definitions
└── utils/              # Utility functions
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=http://localhost:8000
```

### API Integration

The frontend communicates with the TTA backend API at `http://localhost:8000` by default. The API client handles:

- Authentication with JWT tokens
- RESTful API calls for CRUD operations
- Error handling and response formatting

### WebSocket Integration

Real-time chat functionality uses Socket.IO to connect to the backend WebSocket server for:

- Live therapeutic conversations
- Typing indicators
- Interactive therapeutic elements
- Crisis detection and support

## State Management

The application uses Redux Toolkit with the following slices:

- **authSlice**: Authentication state and user management
- **playerSlice**: Player profile and dashboard data
- **characterSlice**: Character creation and management
- **worldSlice**: World selection and customization
- **chatSlice**: Chat sessions and message history
- **settingsSlice**: User preferences and settings

## Styling

The application uses Tailwind CSS with:

- Custom therapeutic color palette
- Responsive design utilities
- Accessibility-focused components
- Custom component classes for consistency

## Testing

Run tests with:

```bash
npm test
```

The test suite includes:

- Component unit tests
- Redux slice tests
- Integration tests for user workflows
- Accessibility tests

## Accessibility

The application follows WCAG 2.1 AA guidelines:

- Keyboard navigation support
- Screen reader compatibility
- High contrast mode
- Focus management
- Semantic HTML structure

## Deployment

Build the application for production:

```bash
npm run build
```

The build artifacts will be in the `build/` directory, ready for deployment to any static hosting service.

## Integration with TTA Backend

This frontend is designed to work with the TTA Player Experience API backend. Ensure the backend is running and accessible at the configured API URL.

Key integration points:

- Authentication via JWT tokens
- RESTful API for data operations
- WebSocket connection for real-time chat
- Crisis detection and safety features
- Therapeutic content delivery

## Contributing

When contributing to the frontend:

1. Follow the existing code structure and naming conventions
2. Write tests for new components and features
3. Ensure accessibility compliance
4. Update documentation as needed
5. Test integration with the backend API

## License

This project is part of the TTA (Therapeutic Text Adventure) platform.
