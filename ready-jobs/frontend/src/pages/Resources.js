import React from "react";
import { Card, Col, Container, Row } from "react-bootstrap";

const resources = [
  {
    name: "National Careers Service",
    purpose: "Explore careers, develop application skills and find practical guidance for your job search.",
    link: "https://nationalcareers.service.gov.uk/"
  },
  {
    name: "How to write a CV",
    purpose: "A practical guide to CV structure, content and presentation from the National Careers Service.",
    link: "https://nationalcareers.service.gov.uk/careers-advice/cv-sections"
  },
  {
    name: "Cover-letter guidance",
    purpose: "Advice on tailoring a concise cover letter to a role and employer.",
    link: "https://nationalcareers.service.gov.uk/careers-advice/covering-letter"
  },
  {
    name: "Interview preparation",
    purpose: "Common interview formats, preparation techniques and ways to practise your answers.",
    link: "https://nationalcareers.service.gov.uk/careers-advice/interview-advice"
  },
  {
    name: "Application forms",
    purpose: "Guidance for completing job applications and showing evidence against selection criteria.",
    link: "https://nationalcareers.service.gov.uk/careers-advice/application-forms"
  },
  {
    name: "Skills assessment",
    purpose: "Identify transferable strengths and careers that may fit your current skill set.",
    link: "https://nationalcareers.service.gov.uk/skills-assessment"
  },
  {
    name: "Prospects job profiles",
    purpose: "Research responsibilities, qualifications and progression routes across different careers.",
    link: "https://www.prospects.ac.uk/job-profiles"
  },
  {
    name: "Find a job",
    purpose: "Search the UK government's job-listing service by role, location and working pattern.",
    link: "https://findajob.dwp.gov.uk/"
  },
  {
    name: "Reasonable adjustments",
    purpose: "Understand workplace adjustments and support available to disabled applicants and employees.",
    link: "https://www.gov.uk/reasonable-adjustments-for-disabled-workers"
  },
  {
    name: "Employment rights",
    purpose: "Official guidance covering contracts, pay, leave, working hours and workplace rights.",
    link: "https://www.gov.uk/browse/working"
  }
];

function Resource() {
  return (
    <Container className="mt-4">
      <h3>Job Application Resources</h3>
      <Row xs={1} md={2} className="g-4 mt-3">
        {resources.map((res, idx) => (
          <Col key={idx}>
            <Card className="h-100">
              <Card.Body>
                <Card.Title>{res.name}</Card.Title>
                <Card.Text>{res.purpose}</Card.Text>
                <Card.Link
                  href={res.link}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View Resource
                </Card.Link>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
}

export default Resource;
