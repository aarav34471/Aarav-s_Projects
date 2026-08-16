// src/pages/Index.js
import React, { useContext } from "react";
import { Card, Col, Container, Row } from "react-bootstrap";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import "../styles/Index.css";

function Index() {
  const { user } = useContext(AuthContext);

  return (
    <Container className="container-main">
      <Row>
        <Col>

          <Row>
            <Col>
              <div className="description-1">
                <h5>Search Jobs</h5>
                <p>Discover and explore all available job listings.</p>
              </div>
            </Col>
            <Col>
              <div className="card-right">
                <Link to="/jobs/" style={{ textDecoration: "none" }}>
                  <Card className="hover-card" style={{ borderRadius: "30px" }}>
                    <Card.Body>
                      <Card.Text style={{ fontSize: "15px", textAlign: "center" }}>
                        Go to Jobs
                      </Card.Text>
                    </Card.Body>
                  </Card>
                </Link>
              </div>
            </Col>
          </Row>

          {user?.account_type === "graduate" && (
          <Row className="mt-4">
            <Col>
              <div className="description-1">
                <h5>Your Bookmarks</h5>
                <p>View jobs you’ve saved for later.</p>
              </div>
            </Col>
            <Col>
              <div className="card-right">
                <Link to="/bookmarks/" style={{ textDecoration: "none" }}>
                  <Card className="hover-card" style={{ borderRadius: "30px" }}>
                    <Card.Body>
                      <Card.Text style={{ fontSize: "15px", textAlign: "center" }}>
                        Bookmarks
                      </Card.Text>
                    </Card.Body>
                  </Card>
                </Link>
              </div>
            </Col>
          </Row>
          )}


          {user?.account_type === "employer" && (
            <Row className="mt-4">
              <Col>
                <div className="description-1">
                  <h5>Post a Job</h5>
                  <p>Create a new job posting for candidates to apply.</p>
                </div>
              </Col>
              <Col>
                <div className="card-right">
                  <Link to="/jobs/create" style={{ textDecoration: "none" }}>
                    <Card className="hover-card" style={{ borderRadius: "30px" }}>
                      <Card.Body>
                        <Card.Text style={{ fontSize: "15px", textAlign: "center" }}>
                          Post Job
                        </Card.Text>
                      </Card.Body>
                    </Card>
                  </Link>
                </div>
              </Col>
            </Row>
          )}


          {user?.account_type === "employer" && (
            <Row className="mt-4">
              <Col>
                <div className="description-1">
                  <h5>My Jobs</h5>
                  <p>Manage the jobs you have posted.</p>
                </div>
              </Col>
              <Col>
                <div className="card-right">
                  <Link to="/myjobs/" style={{ textDecoration: "none" }}>
                    <Card className="hover-card" style={{ borderRadius: "30px" }}>
                      <Card.Body>
                        <Card.Text style={{ fontSize: "15px", textAlign: "center" }}>
                          My Jobs
                        </Card.Text>
                      </Card.Body>
                    </Card>
                  </Link>
                </div>
              </Col>
            </Row>
          )}


          {user?.account_type === "employer" && (
            <Row className="mt-4">
              <Col>
                <div className="description-1">
                  <h5>View Applications</h5>
                  <p>See all applications submitted for your jobs.</p>
                </div>
              </Col>
              <Col>
                <div className="card-right">
                  <Link to="/viewapplications/" style={{ textDecoration: "none" }}>
                    <Card className="hover-card" style={{ borderRadius: "30px" }}>
                      <Card.Body>
                        <Card.Text style={{ fontSize: "15px", textAlign: "center" }}>
                          Applications
                        </Card.Text>
                      </Card.Body>
                    </Card>
                  </Link>
                </div>
              </Col>
            </Row>
          )}


          {user?.account_type === "graduate" && (
            <Row className="mt-4">
              <Col>
                <div className="description-1">
                  <h5>My Applications</h5>
                  <p>Track the status of your job applications.</p>
                </div>
              </Col>
              <Col>
                <div className="card-right">
                  <Link to="/myapplications/" style={{ textDecoration: "none" }}>
                    <Card className="hover-card" style={{ borderRadius: "30px" }}>
                      <Card.Body>
                        <Card.Text style={{ fontSize: "15px", textAlign: "center" }}>
                          Applications
                        </Card.Text>
                      </Card.Body>
                    </Card>
                  </Link>
                </div>
              </Col>
            </Row>
          )}


          <Row className="mt-4">
            <Col>
              <div className="description-1">
                <h5>{user ? "Logout" : "Login"}</h5>
                <p>{user ? "Sign out of your account" : "Access your account"}</p>
              </div>
            </Col>
            <Col>
              <div className="card-right">
                <Link to={user ? "/logout" : "/login"} style={{ textDecoration: "none" }}>
                  <Card className="hover-card" style={{ borderRadius: "30px" }}>
                    <Card.Body>
                      <Card.Text style={{ fontSize: "15px", textAlign: "center" }}>
                        {user ? "Logout" : "Login"}
                      </Card.Text>
                    </Card.Body>
                  </Card>
                </Link>
              </div>
            </Col>
          </Row>


          {!user && (
            <Row className="mt-4">
              <Col>
                <div className="description-1">
                  <h5>Sign Up</h5>
                  <p>Create a new account to start applying.</p>
                </div>
              </Col>
              <Col>
                <div className="card-right">
                  <Link to="/signup" style={{ textDecoration: "none" }}>
                    <Card className="hover-card" style={{ borderRadius: "30px" }}>
                      <Card.Body>
                        <Card.Text style={{ fontSize: "15px", textAlign: "center" }}>
                          Sign Up
                        </Card.Text>
                      </Card.Body>
                    </Card>
                  </Link>
                </div>
              </Col>
            </Row>
          )}
        </Col>
      </Row>
    </Container>
  );
}

export default Index;
