# Health Tracker - Frontend

Next.js web application for tracking water intake, carb consumption, and exercise sessions.

## Features

- 🔐 Telegram Login Widget authentication
- 📊 Real-time progress dashboard
- 🎯 Goal configuration
- 🔥 Streak tracking
- ⚙️ User settings and preferences
- 📱 Responsive design

## Tech Stack

- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Icons:** Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see `../backend/README.md`)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Update .env.local with your values:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_BOT_USERNAME=your_bot_username
```

### Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Landing page with Telegram login
│   ├── dashboard/         # Main dashboard
│   ├── goals/             # Goal configuration
│   └── settings/          # User settings
├── components/
│   ├── auth/              # Authentication components
│   ├── dashboard/         # Dashboard components
│   ├── goals/             # Goal form components
│   └── ui/                # Reusable UI components
└── lib/
    ├── api.ts             # API client
    ├── auth.ts            # JWT token management
    └── utils.ts           # Utility functions
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_BOT_USERNAME` | Telegram bot username | `your_bot` |

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
```

## API Integration

The frontend communicates with the backend API using Axios. All API calls are defined in `lib/api.ts`.

### Authentication Flow

1. User clicks "Login with Telegram" button
2. Telegram Widget opens and user authorizes
3. Frontend receives Telegram user data
4. Frontend sends data to `/api/v1/auth/telegram`
5. Backend validates and returns JWT token
6. Frontend stores token in localStorage
7. All subsequent API calls include JWT in Authorization header

## License

MIT
