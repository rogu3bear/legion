import { render, screen } from '@testing-library/react';
import Hello from '../components/Hello'; // Adjusted import path

test('renders hello', () => {
  render(<Hello />);
  expect(screen.getByText(/hello/i)).toBeInTheDocument();
});
