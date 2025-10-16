
import { Card, Col, Container, Row } from "react-bootstrap";
import { useQuery } from "@tanstack/react-query";
import { API } from "../constants";
import { Link } from "react-router-dom";
import "../styles/Homepage.css"
import { useState, useEffect } from "react";
import FilterSidebar from "../elements/FilterSidebar";


function Home(props) {

  const { isPending, data = [], error } = useQuery({
    queryKey: ["jobs"],
    queryFn: async () => {
      const response = await fetch(`${API}jobs/`);
      return response.json();
    },
  });

  const [filteredJobs, setFilteredJobs] = useState(data)

  useEffect(() => {
    setFilteredJobs(data);
  }, [data]);

  if (isPending) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;


const handleFilter = ({ minSalary, maxSalary, company }) => {
    const newList = data.filter((job) => {
      if (job.salary < minSalary) return false;
      if (job.salary > maxSalary) return false;
      if (company && job.company !== company) return false;
      return true;
    });

    setFilteredJobs(newList);  
  };

  return (

    <Container >
    
        <Row>
        <Col >
            <FilterSidebar onFilterChange={handleFilter}/>
        </Col>

        <Col xs={7} md={8} lg={10} mt={20}>
        { filteredJobs.map((job) => (
        
          <Row key={job.id} className="mb-4">
            <Link to={`/jobs/${job.id}`} className="link-underline">
            <Card className="hover-card">
              <Card.Body>
                <Card.Title className="card-title">{job.title}</Card.Title>
                <Card.Subtitle className="card-subtitle">
                  <p>{job.employer} | {job.location}</p>
                </Card.Subtitle>
                <Row>
                    <Col className="card-text">
                        <Card.Text>{job.description}</Card.Text>
                        <Row>
                            <Col><Card.Text>Salary: {job.salary}</Card.Text></Col> 
                            <Col> <Card.Text style={{textAlign:"right"}}>{job.expiration}</Card.Text></Col>
                        </Row>
                    </Col> 
                </Row>
              </Card.Body>
            </Card>
            </Link>
          </Row>
          
        ))}
        </Col>
        </Row>
        </Container>

  );
        }

export default Home; 
