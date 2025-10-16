
import { useState, useContext } from 'react';
import { Form, Button, Container, Row, Col, Alert } from 'react-bootstrap';
import { useNavigate, Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Link } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();
  const { login, user } = useContext(AuthContext);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    try {

      await login(username, password);
      navigate('/', { replace: true });
    } catch {
      setError('Invalid username or password');
    }
  };

  if (user) {
    return <Navigate to="/" />;
  }

  return (
    <Container className="mt-5">
      <Row className="justify-content-md-center">
        <Col xs={12} md={6}>
          <h2 className="mb-4">Log In</h2>
          {error && <Alert variant="danger">{error}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="loginUsername" className="mb-3">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
            </Form.Group>

            <Form.Group controlId="loginPassword" className="mb-3">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </Form.Group>

            <Button variant="primary" type="submit" className="w-100">
              Log In
            </Button>
          </Form>
          <Link to={`/signup`} className="link-underline">
            Create an Account
          </Link>

        </Col>
      </Row>
    </Container>
  );
}
