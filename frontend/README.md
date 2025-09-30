# DocuBot Frontend

A modern React/Next.js frontend for the DocuBot RAG chatbot project - an AI-powered tool that transforms documentation websites into intelligent chat assistants for developers.

## Features

- **Interactive Chatbot Interface**: Clean, responsive chat UI with real-time messaging
- **Settings Management**: Configure documentation URLs for the RAG system
- **Dark/Light Mode Support**: Automatic theme detection with CSS variables
- **TypeScript Support**: Full type safety throughout the application
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI Components**: Built with Tailwind CSS and Lucide React icons

## Tech Stack

- **Next.js 15**: React framework with App Router
- **React 18**: Latest React with hooks and modern patterns
- **TypeScript**: Full type safety and developer experience
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Lucide React**: Beautiful, consistent icons

## Project Structure

```
src/
├── app/
│   ├── page.tsx          # Main chat interface
│   ├── layout.tsx        # Root layout with navigation
│   ├── globals.css       # Global styles and Tailwind imports
│   └── settings/
│       └── page.tsx      # Settings page for URL configuration
├── components/
│   ├── Navigation.tsx    # Main navigation component
│   └── LoadingSpinner.tsx # Reusable loading component
└── types/
    └── index.ts          # TypeScript type definitions
```

## Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Open Application**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Usage

### Chat Interface
- Start by visiting the main page to access the chatbot
- Type questions about your documentation in natural language
- The bot provides context-aware responses based on configured documentation

### Settings
- Navigate to `/settings` to configure your documentation URL
- Enter the URL of the documentation website you want to use
- Save the settings to enable the RAG functionality

## Configuration

The application stores settings in localStorage:
- Documentation URL
- Configuration status
- Last updated timestamp

## Development

### Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Environment Setup

The project uses:
- Node.js 18+
- NPM or Yarn
- Modern browser with ES2020 support

## API Integration

The frontend is designed to integrate with a backend RAG system:

- Chat messages are sent to `/api/chat` endpoint
- Settings are saved locally and can be synced with backend
- Real-time responses with loading states
- Error handling for failed requests

## Styling

The application uses a modern design system with:
- CSS custom properties for theming
- Responsive breakpoints
- Consistent spacing and typography
- Accessible color contrast
- Smooth animations and transitions

## Future Enhancements

- Real backend API integration
- WebSocket support for real-time chat
- Message history persistence
- User authentication
- Multiple documentation sources
- Chat export functionality
- Advanced settings and customization
