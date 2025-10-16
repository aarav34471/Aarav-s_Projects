import React, { useState, useEffect, useContext } from "react";
import { Card, Col, Container, Row, Form } from "react-bootstrap";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { API } from "../constants";
import axios from "axios";  
import { AuthContext } from "../context/AuthContext";

export default function ApplicationView() {
  const { user, token } = useContext(AuthContext);
  const queryClient     = useQueryClient();
  const [myApps, setMyApps] = useState([]);

  // derive the Django media URL by stripping "/api/" off API
  const backend    = API.split("/api")[0];      
  const filesRoute = `${backend}`;               

  const fetchJobs = async () => {
    const res = await fetch(`${API}jobs/`);
    return res.json();
  };
  const fetchApps = async () => {
    const res = await fetch(`${API}applications/`);
    return res.json();
  };
    const fetchGrads = async () => {
    const res = await fetch(`${API}graduates/`);
    return res.json();
  };

  const { data: appsData = [], isPending, error } = useQuery({
    queryKey: ["applications"],
    queryFn: fetchApps,
  });
  const { data: jobData = [], isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: fetchJobs,
  });
  const { data: gradsData = [] } = useQuery({
    queryKey: ["graduates"],
    queryFn: fetchGrads,
  });

  useEffect(() => {
    if (!user) {
      setMyApps([]);
      return;
    }
    //gather IDs of jobs this employer posted
    const jobIds = jobData
      .filter(job => job.company === user.modelId)
      .map(job => job.id);

    //filter applications for those job IDs
    const filtered = appsData.filter(app => jobIds.includes(app.job));
    setMyApps(filtered);
  }, [user, jobData, appsData, gradsData]);

  if (isLoading || isPending) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const handleStatusChange = async (appId, newStatus, gradId, jobId) => {
    try {
      const res = await fetch(`${API}applications/${appId}/`, {
        method:  "PUT",
        headers: {
          "Content-Type":  "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ 
          graduate: gradId,
          job: jobId,
          status:  newStatus }),
      });
    
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      if (newStatus === "OFFER"){
        alert("Updated status to OFFER");
      }
      if (newStatus === "INTERVIEW"){
        alert("Updated status to INTERVIEW");
      }
      if (newStatus === "APPLIED"){
        alert("Updated status to APPLIED");
      }
      if (newStatus === "REJECTED"){
        alert("Updated status to REJECTED");
      }
      const serviceId = 'service_623rjzn';
      const templateId = 'template_3bpcmkn';
      const publicKey = 'xw3SLy7tZOuNlT4zt';

      // find graduate email from fetched grads list
      const grad = gradsData.find(g => g.id === gradId);

      const email = grad?.email;

      const data = {
          service_id: serviceId,
          template_id: templateId,
          user_id: publicKey,
          template_params: {
              email: email,
              application: appId,
              status: newStatus,
          }
      }


      try { //send email with application status update
          await axios.post("https://api.emailjs.com/api/v1.0/email/send", data);
      }
      catch (error) {
          console.log("error sending email");
      }

      return res.json();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Container className="mt-4">
      <Row xs={1} className="g-4">
        {myApps.map(app => (
          <Col key={app.id}>
            <Card className="card-details h-100">
              <Card.Body>
                <Card.Title>Application #{app.id}</Card.Title>
                <Card.Subtitle className="mb-2 text-muted">
                  Job: {app.job} — Graduate: {app.graduate}
                </Card.Subtitle>

                <Card.Text>
                  <strong>Cover Letter:</strong>{" "}
                  <a
                    href={`${filesRoute}${app.cover_letter}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View
                  </a>
                </Card.Text>

                <Card.Text>
                  <strong>CV:</strong>{" "}
                  <a
                    href={`${filesRoute}${app.cv}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View
                  </a>
                </Card.Text>

                <Form.Group controlId={`status-${app.id}`} className="mb-3">
                  <Form.Label>Status</Form.Label>
                  <Form.Select
                    value={app.status}
                    onChange={e => handleStatusChange(app.id, e.target.value, app.graduate, app.job)}
                  >
                    <option value="APPLIED">Applied</option>
                    <option value="INTERVIEW">Interview</option>
                    <option value="OFFER">Offer</option>
                    <option value="REJECTED">Rejected</option>
                  </Form.Select>
                </Form.Group>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
}
