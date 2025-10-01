# DocuBot Frontend

A minimal, aesthetic light-themed frontend for DocuBot - a RAG chatbot that helps users interact with technical documentation.

## Features

- **Chat Interface**: Clean, modern chat UI for interacting with the AI assistant
- **Settings Page**: Simple form to add documentation URLs for indexing
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Minimal Aesthetic**: Clean, light-themed design with smooth animations

## Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first CSS framework
- **React** - Component-based UI library

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Pages

- **Home (`/`)**: Main chat interface where users can interact with the AI assistant
- **Settings (`/settings`)**: Form to add documentation URLs for the RAG system to crawl and index

## Project Structure

```
src/
├── app/
│   ├── globals.css      # Global styles and TailwindCSS configuration
│   ├── layout.tsx       # Root layout component
│   ├── page.tsx         # Home page with chat interface
│   └── settings/
│       └── page.tsx     # Settings page with URL input form
```

## Design Principles

- **Minimal**: Clean, uncluttered interface
- **Light Theme**: Consistent light color scheme
- **Accessible**: Proper focus states and keyboard navigation
- **Responsive**: Mobile-first design approach
- **Smooth**: Subtle animations and transitions

## Future Enhancements

- Integration with backend RAG system
- Real-time chat functionality
- Document management features
- Advanced search capabilities
