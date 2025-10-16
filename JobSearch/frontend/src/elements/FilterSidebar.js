import { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import "../styles/Sidebar.css"

function FilterSidebar({ onFilterChange }) {
  const [minSalary, setMinSalary] = useState(0);
  const [maxSalary, setMaxSalary] = useState(100000);

  const handleSubmit = (e) => {
    e.preventDefault();
    onFilterChange({ minSalary, maxSalary });
  };

  return (
    <Form onSubmit={handleSubmit} className="form" >

      <Form.Group className="form-group">
        <Form.Label>Min Salary</Form.Label>
        <Form.Control
          type="number"
          value={minSalary}
          onChange={(e) => setMinSalary(Number(e.target.value))}
        />
      </Form.Group>

      <Form.Group className="form-group">
        <Form.Label>Max Salary</Form.Label>
        <Form.Control
          type="number"
          value={maxSalary}
          onChange={(e) => setMaxSalary(Number(e.target.value))}
        />
      </Form.Group>

      <Button className="button" type="submit" >
        Apply Filters
      </Button>
    </Form>
  );
}

export default FilterSidebar;
