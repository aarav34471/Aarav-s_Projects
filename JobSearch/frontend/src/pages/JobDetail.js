
import { Card, Col, Container, Row, Button } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useParams } from "react-router-dom";

import { useQuery } from "@tanstack/react-query";
import { API } from "../constants";
import { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import "../styles/Homepage.css"
import { getDriveTime } from "../elements/GoogleMapsApi";




function JobDetail(props) {

  const { user } = useContext(AuthContext);
  

  const { id } = useParams(); 

  const [driveTime, setDriveTime] = useState(null);
  const [kilometers, setKilometers] = useState(null);


  const { isPending, data = {}, error } = useQuery({
    queryKey: ["jobs", id],
    queryFn: async () => {
      const response = await fetch(`${API}jobs/${id}/`);
      return await response.json();
    },
  });


  //GOOGLE MAPS API

  useEffect(() => {

    if (!data || !user?.latitude || !user?.longitude) return;
  

    (async () => {

      const { durationSec, distanceKm }  = await getDriveTime(
        { lat: user.latitude, lng: user.longitude },
        { lat: data.latitude, lng: data.longitude },
      );
      const min = parseInt(durationSec/60);
      setKilometers(distanceKm.toFixed(1));
      setDriveTime(min);
    })();
  }, [data, user]);

  if (isPending) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;



  const bookmarkClick = async (e) => {
    e.preventDefault();

    const now = new Date();
  // gives "2025-05-10T12:35:23.369Z"
    const iso = now.toISOString();

  // replace ".369Z" with ".369000Z"
    const date = `${iso}000Z`

    console.log(date);

    try {
      const response = await fetch(`${API}bookmarks/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          status: "INCOMPLETE",
          gradID: user.modelId,
          jobID: data.id,
          date_created: date,
          }) 
      });
    
      if (!response.ok) throw new Error("Failed to bookmark job");

      const result = await response.json();
      alert("Job bookmarked successfully!");

    } 
      catch (error) {
          alert("Error: " + error.message);
    }
  }; 

  return (
    <Container className="mt-4">
    <Card className="card-details">
      <Card.Body>

        <Card.Title className="card-title">
          <Row>
            <Col>{data.title}</Col>
            <Col className="text-end"><Button 
                variant="outline-primary" 
                size="sm"
                onClick={bookmarkClick}
              > 🔖 Bookmark </Button>
          </Col>
        </Row>
      </Card.Title>


        <Card.Subtitle className="mb-3 text-muted card-subtitle">
          {data.company} | {data.location} | Drive Time: {driveTime} minutes. | Distance: {kilometers} kilometers.
        </Card.Subtitle>


        <Card.Text>
          <strong>Salary:</strong> £{data.salary.toLocaleString()}
        </Card.Text>
        <Card.Text>
          <strong>Expires on:</strong>{" "}
          {data.expiration}
        </Card.Text>
        <Card.Text>
          <strong>Job Type:</strong>{" "}
          {data.job_type === "FT" ? "Full-time" : "Part-time"}
        </Card.Text>
        <Card.Text>
          <strong>Requirements:</strong> {data.requirements}
        </Card.Text>


        {data.tags?.length > 0 && (
          <Card.Text>
            <strong>Tags:</strong> {data.tags.join(", ")}
          </Card.Text>
        )}

        <hr />


        <Card.Text className="card-text">{data.description}</Card.Text>
        <Link to={`/application/${data.id}`}>
          <Button variant="primary" className="mt-4">
            Apply
          </Button>
        </Link>

      </Card.Body>
      
    </Card>
  </Container>
  );

}

export default JobDetail;
