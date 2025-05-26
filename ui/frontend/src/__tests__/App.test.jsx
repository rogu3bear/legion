import { render, screen } from '@testing-library/react'
import SimpleComponent from '../components/simple'

test('renders Simple Component', () => {
  render(<SimpleComponent />)
  expect(screen.getByText(/Simple Agent Component/i)).toBeInTheDocument()
}) 