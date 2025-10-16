// src/components/GraduateApplications.js
import React, { useState, useEffect, useContext } from "react";
import { Card, Col, Container, Row } from "react-bootstrap";
import { useQuery } from "@tanstack/react-query";
import { API } from "../constants";
import { AuthContext } from "../context/AuthContext";

export default function GraduateApplications() {
  const { user, token } = useContext(AuthContext);
  const [myApps, setMyApps] = useState([]);

  // derive your Django server root
  const backend = API.split("/api")[0]; // e.g. "http://127.0.0.1:8000"

  const fetchApps = async () => {
    const res = await fetch(`${API}applications/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.json();
  };

  const { data: appsData = [], isLoading, error } = useQuery({
    queryKey: ["graduateApplications"],
    queryFn: fetchApps,
  });

  useEffect(() => {
    if (!user) {
      setMyApps([]);
      return;
    }
    // filter to only this graduate’s applications
    const filtered = appsData.filter(app => app.graduate === user.modelId);
    setMyApps(filtered);
  }, [user, appsData]);

  if (isLoading) return <div>Loading...</div>;
  if (error)   return <div>Error: {error.message}</div>;

  return (
    <Container className="mt-4">
      <Row xs={1} className="g-4">
        {myApps.map(app => (
          <Col key={app.id}>
            <Card className="card-details h-100">
              <Card.Body>
                <Card.Title>Application #{app.id}</Card.Title>
                <Card.Subtitle className="mb-2 text-muted">
                  Status: {app.status}
                </Card.Subtitle>

                <Card.Text>
                  <strong>Cover Letter:</strong>{" "}
                  <a
                    href={`${backend}${app.cover_letter}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View
                  </a>
                </Card.Text>

                <Card.Text>
                  <strong>CV:</strong>{" "}
                  <a
                    href={`${backend}${app.cv}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View
                  </a>
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
}
