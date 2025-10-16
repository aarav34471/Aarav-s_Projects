import { useState, useEffect } from "react";
import { Form, Button, Container, Alert, Row, Col } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "../constants"; 

export default function SignUp() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
    account_type: "graduate", // default to graduate
    address: "",
    // for graduates
    degree: "",
    status: "UG",
    // for mentor
    mentor_degree: "",
    biography: "",
    // employer
    latitude: 0,
    longitude: 0,
  });


  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!navigator.geolocation) return;
    //ask user for sharing their location to give their lat long if not it defaults as 0,0
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setForm(prev => ({
          ...prev,
          latitude: coords.latitude,
          longitude: coords.longitude
        }));
      },

      (err) => {
        console.warn('Geolocation error:', err);

      },

    );
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const payload = {
        username: form.username,
        email: form.email,
        password: form.password,
        password2: form.password2,
        account_type: form.account_type,
        latitude: form.latitude,    
        longitude: form.longitude,
    };



    if (form.account_type === "graduate") {
        payload.degree = form.degree;
        payload.status = form.status;

    } else if (form.account_type === "mentor") {
        payload.mentor_degree = form.mentor_degree;
        payload.biography = form.biography;


    } else if (form.account_type === "employer") {
        payload.address = form.address;


    }

    const serviceId = 'service_623rjzn';
    const templateId = 'template_5xs72zg';
    const publicKey = 'xw3SLy7tZOuNlT4zt';

    const data = {
        service_id: serviceId,
        template_id: templateId,
        user_id: publicKey,
        template_params: {
            name: payload.username,
            email: payload.email,
        }
    }

    try {

        await axios.post(`${API}register/`, payload);
        setSuccess(true);
  
        try {
          const res = await axios.post("https://api.emailjs.com/api/v1.0/email/send", data);

        }
        catch (error) {
            console.log("error sending email");
        }

        setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
        const errorMessage = err.response.data.detail || "An error occurred during sign-up.";
        setError(errorMessage);
        alert(`Error Signing Up: ${errorMessage}`);
    }
  };

  return (
    <Container className="mt-4" style={{ maxWidth: 600 }}>
      <h2>Sign Up</h2>
      {success && <Alert variant="success">Account created! Redirecting…</Alert>}
      {error && <Alert variant="danger">{error}</Alert>}

      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3" controlId="signupUsername">
          <Form.Label>Username</Form.Label>
          <Form.Control
            name="username"
            value={form.username}
            onChange={handleChange}
            required
          />
        </Form.Group>

        <Form.Group className="mb-3" controlId="signupEmail">
          <Form.Label>Email</Form.Label>
          <Form.Control
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </Form.Group>

        <Form.Group className="mb-3" controlId="signupPassword">
          <Form.Label>Password</Form.Label>
          <Form.Control
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </Form.Group>

        <Form.Group className="mb-3" controlId="signupPassword2">
          <Form.Label>Confirm Password</Form.Label>
          <Form.Control
            type="password"
            name="password2"
            value={form.password2}
            onChange={handleChange}
            required
          />
        </Form.Group>

        <Form.Group className="mb-3" controlId="signupAccountType">
          <Form.Label>Account Type</Form.Label>
          <Form.Select
            name="account_type"
            value={form.account_type}
            onChange={handleChange}
          >
            <option value="graduate">Graduate</option>
            <option value="mentor">Mentor</option>
            <option value="employer">Employer</option>
          </Form.Select>
        </Form.Group>

        {form.account_type === "graduate" && (
          <>
            <Row>
              <Col>
                <Form.Group className="mb-3" controlId="signupDegree">
                  <Form.Label>Degree</Form.Label>
                  <Form.Control
                    name="degree"
                    value={form.degree}
                    onChange={handleChange}
                    required
                  />
                </Form.Group>
              </Col>
              <Col>
                <Form.Group className="mb-3" controlId="signupStatus">
                  <Form.Label>Status</Form.Label>
                  <Form.Select
                    name="status"
                    value={form.status}
                    onChange={handleChange}
                  >
                    <option value="UG">Undergraduate</option>
                    <option value="PG">Postgraduate</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
          </>
        )}

        {form.account_type === "mentor" && (
          <>
            <Form.Group className="mb-3" controlId="signupMentorDegree">
              <Form.Label>Degree</Form.Label>
              <Form.Control
                name="mentor_degree"
                value={form.mentor_degree}
                onChange={handleChange}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3" controlId="signupBio">
              <Form.Label>Biography</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="biography"
                value={form.biography}
                onChange={handleChange}
                required
              />
            </Form.Group>
            
          </>
        )}

        {form.account_type === "employer" && (
          <>
            <Form.Group className="mb-3" controlId="signupAddress">
              <Form.Label>Address</Form.Label>
              <Form.Control
                name="address"
                value={form.address}
                onChange={handleChange}
                required
              />
            </Form.Group>
          </>
        )}

        <Button variant="primary" type="submit" disabled={success}>
          Create Account
        </Button>
      </Form>
    </Container>
  );
}

