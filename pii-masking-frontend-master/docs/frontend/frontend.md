# Frontend Setup Guide

This document explains how to set up and run the frontend for the **PII Masking** project.

---

## Prerequisites

- [Node.js](https://nodejs.org/) — **v14 or higher** (LTS version recommended)
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)

---

## Tech Stack

The **PII Masking Frontend** is built using:

1. **React**  
   - UI library for building interactive user interfaces with reusable components.  
   - Hooks and functional components are used for state and lifecycle management.

2. **Vite**  
   - Next-generation frontend tooling for fast development and optimized production builds.  
   - Provides instant hot module replacement (HMR) and minimal configuration overhead.

3. **TypeScript**  
   - Superset of JavaScript with static typing for better developer experience and fewer runtime errors.  
   - Strong type definitions for props, state, and API responses.

4. **Tailwind CSS**  
   - Utility-first CSS framework for rapid UI development.  
   - Fully responsive design with mobile-first breakpoints.  
   - Highly customizable with Tailwind config for colors, spacing, and typography.

5. **Other Supporting Tools**  
   - **ESLint & Prettier** — Code linting and formatting.  
   - **PostCSS & Autoprefixer** — CSS transformation and browser compatibility.  
   - **Vite Plugin for React** — Ensures smooth JSX/TSX support.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd PII-Masking-Frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

---

## Running the Development Server

```bash
npm run dev
# or
yarn dev
```

The app will be available at **[http://localhost:5173](http://localhost:5173)** (Vite default port).

---

## Building for Production

```bash
npm run build
# or
yarn build
```

- The optimized production build will be in the `dist/` directory.

---

## Additional Notes

- Update environment variables in `.env` as needed.
- Refer to the `package.json` for available scripts.
