import { useState, useEffect, useContext } from "react";		
import { AuthContext } from "../context/AuthContext";

import { Card, Button, Container, Row, Col } from "react-bootstrap";
import { Link } from "react-router-dom";

import { useQuery, useQueryClient } from "@tanstack/react-query";		
import axios from "axios";		
import { API } from "../constants";



export default function EmployerJobView() {
    const { user, token} = useContext(AuthContext);

    const queryClient = useQueryClient();

    const [myJobs, setMyJobs] = useState([]);

    const { isLoading, data = [], error } = useQuery({
        queryKey: ["jobs"],
        queryFn: async () => {
          const response = await fetch(`${API}jobs/`);
          return response.json();
        },
      });

    useEffect(() => {
        if (user) {
          setMyJobs(data.filter(job => job.company === user.modelId));
        }
    }, [data, user]);

    if (isLoading) return <div>Loading…</div>;
    if (error)  return <div>Error: {error.message}</div>;

    async function handleDelete(jobId) {

        try {
          await axios.delete(
            `${API}jobs/${jobId}/`,
            {
              headers: {
                Authorization: `Bearer ${token}`,  
              }
            }
          );
          queryClient.invalidateQueries({ queryKey: ["jobs"] });
        } catch (err) {
          console.error(err)
        }
      }


  return (
    <Container className="mt-4">
      <Row xs={1} md={2} lg={3} className="g-4">
        {myJobs.map((job) => (
          <Col key={job.id}>
            <Card className="card-details h-100">
              <Card.Body className="d-flex flex-column">
                <Card.Title className="card-title">
                  <Row>
                    <Col>{job.title}</Col>
                  </Row>
                </Card.Title>

                <Card.Subtitle className="mb-2 text-muted card-subtitle">
                  {job.location}
                </Card.Subtitle>

                <Card.Text>
                  <strong>Salary:</strong> £{job.salary.toLocaleString()}
                </Card.Text>
                <Card.Text>
                  <strong>Expires on:</strong> {job.expiration}
                </Card.Text>
                <Card.Text>
                  <strong>Type:</strong>{" "}
                  {job.job_type === "FT" ? "Full‑time" : "Part‑time"}
                </Card.Text>

                <hr />

                <Card.Text className="flex-grow-1 card-text">
                  {job.description}
                </Card.Text>


                <div className="mt-3 d-flex justify-content-between">
                <Link to={`/myjobs/edit/${job.id}`}>
                    <Button variant="outline-success" size="sm">Edit</Button> 
                </Link>
                  <Button
                    variant="outline-danger"
                    size="sm"
                    onClick={() => handleDelete(job.id)}
                  >
                    Delete
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
}


