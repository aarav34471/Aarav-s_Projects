// src/pages/Resource.js
import React from "react";
import { Card, Col, Container, Row } from "react-bootstrap";

const resources = [
  {
    name: "Writing Effective CVs & Covering Letters",
    purpose: "Comprehensive PDF guide to structuring and writing professional CVs and cover letters.",
    link: "https://www.surrey.ac.uk/sites/default/files/2018-10/writing-effective-cvs-and-cover-letters.pdf"
  },
  {
    name: "CV, application and interview support",
    purpose: "Advice on one-to-one sessions for CVs, application forms and mock interviews.",
    link: "https://www.surrey.ac.uk/employability-and-careers/students/cv-application-and-interview-support"
  },
  {
    name: "How do I write a CV and covering letter?",
    purpose: "Step-by-step online article with tips and links to downloadable templates via Surrey Pathfinder.",
    link: "https://help.surrey.ac.uk/article/how-do-i-write-cv-and-covering-letter"
  },
  {
    name: "How can I prepare for an interview?",
    purpose: "Guide to interview preparation and booking mock interviews.",
    link: "https://help.surrey.ac.uk/article/how-can-i-prepare-interview"
  },
  {
    name: "Application process",
    purpose: "Overview of the full application journey from CV prep to selection processes.",
    link: "https://my.surrey.ac.uk/careers/applying-jobs/application-process"
  },
  {
    name: "CV and application support hub",
    purpose: "Central hub linking FAQs on CVs, application forms, psychometric tests, and more.",
    link: "https://help.surrey.ac.uk/employability-and-careers/cv-and-application-support"
  },
  {
    name: "Careers advice",
    purpose: "Details on careers fairs, workshops, drop-in sessions and one-to-one appointments.",
    link: "https://help.surrey.ac.uk/employability-and-careers/careers-advice"
  },
  {
    name: "Top ten tips for writing your CV",
    purpose: "Quick-read list of best practices for CV writing from Surrey Unitemps.",
    link: "https://www.surrey.ac.uk/unitemps/our-candidates/top-ten-tips-writing-your-cv"
  },
  {
    name: "Graduate careers support",
    purpose: "Support available to Surrey graduates up to three years post-graduation.",
    link: "https://www.surrey.ac.uk/employability-and-careers/graduates"
  },
  {
    name: "Employability & Careers Centre",
    purpose: "Main Careers Centre page covering placements, professional training and guidance.",
    link: "https://www.surrey.ac.uk/employability-and-careers"
  }
];

function Resource() {
  return (
    <Container className="mt-4">
      <h3>University of Surrey Job Application Resources</h3>
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
