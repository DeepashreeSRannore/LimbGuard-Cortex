import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders LimbGuard-Cortex application', () => {
  render(<App />);
  const titleElement = screen.getByText(/LimbGuard-Cortex/i);
  expect(titleElement).toBeInTheDocument();
});
