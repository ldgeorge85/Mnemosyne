import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders without crashing and shows Mnemosyne', () => {
    render(<App />);
    expect(screen.getByText(/mnemosyne/i)).toBeInTheDocument();
  });
});
