
import { Card, Col, Container, Row, Button } from "react-bootstrap";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { API } from "../constants";
import { useNavigate } from "react-router-dom";
import "../styles/Homepage.css"
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useState, useEffect } from "react";
import axios from "axios";




function Bookmarks(props) {

  const { user, token } = useContext(AuthContext);

  const queryClient = useQueryClient();  

  const [myBookmarks, setMyBookmarks] = useState([]);

  const navigate = useNavigate()

  const bookmarks = async () => {
    const response = await fetch(`${API}bookmarks/`);
    return response.json();
  }
  const jobs = async () => {
    const response = await fetch(`${API}jobs/`);
    return response.json();
  };

  const {data: bookmarksData = [] , isPending, error} = useQuery({
    queryKey: ["bookmarks"],
    queryFn: bookmarks,
  });
  //pull jobs and bookmarks 
  const {data: jobData = [] , isLoading} = useQuery({
    queryKey: ["jobs"],
    queryFn: jobs,
  });

  useEffect(() => {


    if (!user) {
      setMyBookmarks([]);
      return;
    }

    // keep only this user's bookmark entries
    const userBms = bookmarksData.filter((b) => b.gradID === user.modelId );

    // extract the jobIDs they bookmarked
    const jobIds = userBms.map((b) => b.jobID);
    // filter the jobs list to those IDs

    const filteredJobs = jobData.filter((job) =>
      jobIds.includes(job.id)
    );
    setMyBookmarks(filteredJobs);
  }, [user, bookmarksData, jobData]);

  

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  async function handleDelete(jobId) {
    try {
      const bm = bookmarksData.find(
        b => b.gradID === user.modelId && b.jobID === jobId
      );

      await axios.delete(
        `${API}bookmarks/${bm.id}/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,  
          }
        }
      );
      // refresh data
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
    } catch (err) {
      console.error(err)
    }
  }




  return (

    <Container className="mt-4">
      <Row xs={1} md={2} lg={3} className="g-4">
        {myBookmarks.map((job) => (
          <Col key={job.id}>

            <Card className="card-details h-100">
              <Card.Body className="d-flex flex-column">
                <Card.Title className="card-title">
                  <Row>
                    <Col>{job.title}</Col>
                  </Row>
                </Card.Title>

                <Card.Subtitle className="mb-2 text-muted card-subtitle">
                  {job.company} | {job.location}
                </Card.Subtitle>

                <Card.Text>
                  <strong>Salary:</strong> £{job.salary}
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
                  <Button
                    variant="outline-danger"
                    size="sm"
                    onClick={() => handleDelete(job.id)}
                  >
                    Remove
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => navigate(`/jobs/${job.id}`)}
                  >
                    View
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

export default Bookmarks; 
